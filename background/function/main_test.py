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

import base64
import json
import main
import pytest


class MockTranslateClient():
    def __init__(self, *args, **kwargs):
        pass

    def translate(self, s, target_language='N/A'):
        return {
            'translatedText': 'This is the output string',
            'detectedSourceLanguage': 'en',
        }


@pytest.yield_fixture
def xlate():
    client = MockTranslateClient()
    yield client


last_message = None
def dummy_update(transaction, message):
    global last_message
    last_message = message


def test_invocations(xlate):
    main.update_database = dummy_update
    main.xlate = xlate

    event = {
        'data': base64.b64encode(json.dumps({
            'Original': 'My test message',
            'Language': 'de',
        }).encode('utf-8'))
    }

    main.translate_message(event, None)

    assert last_message is not None
    assert last_message['Original'] == 'My test message'
    assert last_message['Language'] == 'de'
    assert last_message['Translated'] == 'This is the output string'
    assert last_message['OriginalLanguage'] == 'en'
