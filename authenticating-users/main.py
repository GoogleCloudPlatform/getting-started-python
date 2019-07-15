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

import sys

from flask import Flask
app = Flask(__name__)

CERTS = None
AUDIENCE = None


def certs():
    import requests

    global CERTS
    if CERTS is None:
        try:
            response = requests.get(
                'https://www.gstatic.com/iap/verify/public_key'
            )
            CERTS = response.json()
        except Exception as e:
            print('Failed to fetch CERTS: {}'.format(e), file=sys.stderr)
    return CERTS


def get_metadata(item_name):
    import requests

    endpoint = 'http://metadata.google.internal'
    path = '/computeMetadata/v1/project/'
    path += item_name
    try:
        response = requests.get(
            '{}{}'.format(endpoint, path),
            headers = {'Metadata-Flavor': 'Google'}
        )
        metadata = response.json()
    except Exception as e:
        print(
            'Failed to get metadata for {}: {}'.format(item_name, e),
            file=sys.stderr
        )
        metadata = None
    return metadata


def audience():
    global AUDIENCE
    if AUDIENCE is None:
        project_number = get_metadata('numeric-project-id')
        project_id = get_metadata('project-id')
        AUDIENCE = '/projects/{}/apps/{}'.format(
            project_number, project_id
        )
    return AUDIENCE


def validate_assertion(assertion):
    from jose import jwt

    try:
        info = jwt.decode(
            assertion,
            certs(),
            algorithms=['ES256'],
            audience=audience()
            )
        return info['email'], info['sub']
    except Exception as e:
        print('Failed to validate assertion: {}'.format(e), file=sys.stderr)
        return None, None


@app.route('/', methods=['GET'])
def say_hello():
    from flask import request

    assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    email, id = validate_assertion(assertion)
    page = "<h1>Hello {}</h1>".format(email)
    return page
