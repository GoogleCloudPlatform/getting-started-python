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

# [START getting_started_auth_all]
import sys

from flask import Flask
app = Flask(__name__)

AUDIENCE = None


# [START getting_started_auth_metadata]
def get_metadata(item_name):
    """Returns a string with the project metadata value for the item_name.
    See https://cloud.google.com/compute/docs/storing-retrieving-metadata for
    possible item_name values.
    """
    import requests

    endpoint = 'http://metadata.google.internal'
    path = '/computeMetadata/v1/project/'
    path += item_name
    response = requests.get(
        '{}{}'.format(endpoint, path),
        headers={'Metadata-Flavor': 'Google'}
    )
    metadata = response.text
    return metadata
# [END getting_started_auth_metadata]


# [START getting_started_auth_audience]
def audience():
    """Returns the audience value (the JWT 'aud' property) for the current
    running instance. Since this involves a metadata lookup, the result is
    cached when first requested for faster future responses.
    """
    global AUDIENCE
    if AUDIENCE is None:
        project_number = get_metadata('numeric-project-id')
        project_id = get_metadata('project-id')
        AUDIENCE = '/projects/{}/apps/{}'.format(
            project_number, project_id
        )
    return AUDIENCE
# [END getting_started_auth_audience]


# [START getting_started_auth_validate_assertion]
def validate_iap_jwt(iap_jwt) -> tuple[str, str]:
    """Checks that the JWT assertion is valid (properly signed, for the
    correct audience) and if so, returns strings for the requesting user's
    email and a persistent user ID. If not valid, returns None for each field.

    """
    from google.auth.transport import requests as google_auth_requests
    from google.oauth2 import id_token

    try:
        decoded_jwt = id_token.verify_token(
            iap_jwt,
            google_auth_requests.Request(),
            audience=audience(),
            certs_url="https://www.gstatic.com/iap/verify/public_key",
        )
        return decoded_jwt["email"], decoded_jwt["sub"]
    except Exception as e:
        print('Failed to validate assertion: {}'.format(e), file=sys.stderr)
        return None, None
# [END getting_started_auth_validate_assertion]


# [START getting_started_auth_front_controller]
@app.route('/', methods=['GET'])
def say_hello():
    from flask import request

    assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    email, id = validate_iap_jwt(assertion)
    page = "<h1>Hello {}</h1>".format(email)
    return page
# [END getting_started_auth_front_controller]
# [END getting_started_auth_all]
