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

import json
import main
import pytest


class MockFirestoreClient():
    def __init__(self, *args, **kwargs):
        pass

    def collection(self, name):
        return self

    def stream(self):
        return [self]

    def to_dict(self):
        return {
            'Original': 'This is a test sentence',
            'Language': 'de',
            'Translated': 'This should be in German in a real environment',
            'OriginalLanguage': 'en',
        }


class MockPublisherClient():
    def __init__(self, *args, **kwargs):
        self.messages = []

    def publish(self, topic_name, json_message):
        message = json.loads(json_message)
        self.messages.append({
            'topic': topic_name,
            'message': message,
        })


@pytest.yield_fixture
def db():
    client = MockFirestoreClient()
    yield client


@pytest.yield_fixture
def publisher():
    client = MockPublisherClient()
    yield client



def test_index(db, publisher):
    main.app.testing = True
    main.db = db
    main.publisher = publisher
    client = main.app.test_client()

    r = client.get('/')
    assert r.status_code == 200
    response_text = r.data.decode('utf-8')
    assert 'Text to translate' in response_text
    assert 'This should be in German' in response_text


def test_translate(db, publisher):
    main.app.testing = True
    main.db = db
    main.publisher = publisher
    client = main.app.test_client()

    r = client.post('/request-translation', data={
        'v': 'This is a test',
        'lang': 'fr',
    })

    assert r.status_code < 400
    assert len(publisher.messages) == 1
    assert '/translate' in publisher.messages[0]['topic']
    assert publisher.messages[0]['message']['Original'] == 'This is a test'
    assert publisher.messages[0]['message']['Language'] == 'fr'

