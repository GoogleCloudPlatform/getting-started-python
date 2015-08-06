# Copyright 2015 Google Inc.
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

"""
Blueprint module for OAuth2 for Login (OpenID Connect) for Google Accounts.
"""

import json
import random
import string
from functools import wraps

import httplib2
from flask import Blueprint, current_app, redirect, request, session, url_for
from oauth2client.client import Credentials, OAuth2WebServerFlow, \
    FlowExchangeError


oauth2 = Blueprint('oauth2', __name__)


def get_credentials():
    serialized = session.get('oauth2credentials')
    if not serialized:
        return None
    return Credentials.new_from_json(serialized)


# [START required]
def required(f):
    """Decorator to require OAuth2 credentials for a view.

    All functions can check the current state by checking if oauth2.credentials
    is not None, but this decorator will redirect the user to the authorization
    flow if they do not have the appropriate credentials. Once the user has
    authorized the application, they will be returned to the original URL.

    """
    @wraps(f)
    def decr(*args, **kwargs):
        if not current_app.testing and not get_credentials():
            return redirect(url_for('oauth2.login', return_url=request.url))
        else:
            return f(*args, **kwargs)
    return decr
# [END required]


# [START request_user_info]
def _request_user_info(credentials):
    """
    Makes an HTTP request to the Google+ API to retrieve the user's basic
    profile information, including full name and photo.
    """
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request(
        'https://www.googleapis.com/plus/v1/people/me')

    if resp.status != 200:
        current_app.logger.error(
            "Error while obtaining user profile: %s" % resp)
        return None

    profile = json.loads(content)
    return profile
# [END request_user_info]


# [START make_flow]
def _make_flow():
    # Generate a CSRF token to prevent malicious requests.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))

    session['oauth2state'] = state

    return OAuth2WebServerFlow(
        client_id=current_app.config['OAUTH2_CLIENT_ID'],
        client_secret=current_app.config['OAUTH2_CLIENT_SECRET'],
        scope=['email', 'profile'],
        state=state,
        approval_prompt='force',
        redirect_uri=url_for("oauth2.callback", _external=True))
# [END make_flow]


# [START login]
@oauth2.route('/login')
def login():
    return_url = request.args.get('return_url')
    if not return_url:
        return_url = request.referrer or '/'
    session['oauth2return'] = return_url

    flow = _make_flow()
    auth_url = flow.step1_get_authorize_url()
    return redirect(auth_url)
# [END login]


@oauth2.route('/logout')
def logout():
    session.pop('oauth2credentials', None)
    session.pop('profile', None)
    return redirect(request.referrer or '/')


# [START callback]
@oauth2.route('/oauth2callback')
def callback():
    # Check the CSRF token.
    if request.args.get('state', '') != session.pop('oauth2state', None):
        return 'Invalid request state', 400

    flow = _make_flow()

    # Exchange the auth code for credentials.
    try:
        credentials = flow.step2_exchange(request.args['code'])
    except FlowExchangeError as e:
        current_app.logger.exception(e)
        return e.message, 400

    # Save the credentials to the session.
    session['oauth2credentials'] = credentials.to_json()

    # Get the user's profile from Google and save it to the session.
    session['profile'] = _request_user_info(credentials)

    return redirect(session.pop('oauth2return', '/'))
# [END callback]
