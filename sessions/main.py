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

import random
from uuid import uuid4

from google.cloud import firestore
from flask import Flask, make_response, request


app = Flask(__name__)
sessions = firestore.Client().collection('sessions')
colors = ['red', 'blue', 'green', 'yellow', 'pink']


# Updates and returns the info for given session_id. If there is no session_id,
# it creates a random one. If there is no session data, it creates and stores
# initial values (1 view, random color). Updates the session by incrementing
# the number of views.
def update_session(session_id):
    if session_id is None:
        session_id = str(uuid4())   # Random, unique identifier

    doc = sessions.document(session_id).get()
    if doc.exists:
        session = doc.to_dict()
        prior_views = session.get('views', 0)
        session['views'] = prior_views + 1
        doc.reference.set(session)
    else:
        session = {
            'color': random.choice(colors),
            'views': 1
        }
        sessions.add(session, document_id=session_id)

    session['session_id'] = session_id
    return session


@app.route('/', methods=['GET'])
def home():
    template = '<body bgcolor={}>Views {}</body>'

    session = update_session(request.cookies.get('session_id'))

    resp = make_response(template.format(session['color'], session['views']))
    resp.set_cookie('session_id', session['session_id'], httponly=True)
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
