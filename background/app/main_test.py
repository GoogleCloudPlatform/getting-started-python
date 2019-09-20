# Copyright 2019 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest
import uuid

from google.cloud import firestore
from google.cloud import pubsub

os.environ['GOOGLE_CLOUD_PROJECT'] = os.environ['FIRESTORE_PROJECT_ID']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'firestore-service-account.json'
    )
)

SUBSCRIPTION_NAME = 'projects/{}/subscriptions/{}'.format(
    os.getenv('FIRESTORE_PROJECT_ID'), 'test-' + str(uuid.uuid4())
)

import main


@pytest.yield_fixture
def db():
    def clear_collection(collection):
        """ Removes every document from the collection, to make it easy to see
            what has been added by the current test run.
        """
        for doc in collection.stream():
            doc.reference.delete()

    client = firestore.Client()
    translations = client.collection('translations')
    clear_collection(translations)
    translations.add({
        'Original': 'A testing message',
        'Language': 'fr',
        'Translated': '"A testing message", but in French',
        'OriginalLanguage': 'en',
        },
        document_id='test translation'
    )
    yield client


@pytest.yield_fixture
def publisher():
    client = pubsub.PublisherClient()
    yield client


@pytest.yield_fixture
def subscriber():
    subscriber = pubsub.SubscriberClient()
    topic_name = 'projects/{}/topics/{}'.format(
        os.getenv('FIRESTORE_PROJECT_ID'), 'translate'
    )
    subscription = subscriber.create_subscription(
        SUBSCRIPTION_NAME, topic_name
    )
    yield subscriber
    subscriber.delete_subscription(SUBSCRIPTION_NAME)
    

def test_index(db, publisher):
    main.app.testing = True
    main.db = db
    main.publisher = publisher
    client = main.app.test_client()

    r = client.get('/')
    assert r.status_code == 200
    response_text = r.data.decode('utf-8')
    assert 'Text to translate' in response_text
    assert 'but in French' in response_text


def test_translate(db, publisher, subscriber):
    main.app.testing = True
    main.db = db
    main.publisher = publisher
    client = main.app.test_client()

    r = client.post('/request-translation', data={
        'v': 'This is a test',
        'lang': 'fr',
    })

    assert r.status_code < 400

    response = subscriber.pull(SUBSCRIPTION_NAME, 1, timeout=2.0)
    assert len(response.received_messages) == 1
    assert b'This is a test' in response.received_messages[0].message.data
    assert b'fr' in response.received_messages[0].message.data
