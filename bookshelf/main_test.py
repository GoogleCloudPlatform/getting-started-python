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

import re

import main
import pytest
import requests
from retrying import retry
from six import BytesIO


@pytest.yield_fixture
def app(request):
    """This fixtures provides a Flask app instance configured for testing.

    It also ensures the tests run within a request context, allowing
    any calls to flask.request, flask.current_app, etc. to work."""
    app = main.app

    with app.test_request_context():
        yield app


@pytest.yield_fixture
def firestore():

    import firestore
    """This fixture provides a modified version of the app's firebase model that
    tracks all created items and deletes them at the end of the test.

    Any tests that directly or indirectly interact with the database should use
    this to ensure that resources are properly cleaned up.
    """

    # Ensure no books exist before running. This typically helps if tests
    # somehow left the database in a bad state.
    delete_all_books(firestore)

    yield firestore

    # Delete all books that we created during tests.
    delete_all_books(firestore)


# The backend data stores can sometimes be flaky. It's useful to retry this
# a few times before giving up.
@retry(
    stop_max_attempt_number=3,
    wait_exponential_multiplier=100,
    wait_exponential_max=2000)
def delete_all_books(firestore):
    while True:
        books, _ = firestore.next_page(limit=50)
        if not books:
            break
        for book in books:
            firestore.delete(book['id'])


# Mark all test cases in this class as flaky, so that if errors occur they
# can be retried. This is useful when databases are temporarily unavailable.
# @flaky(rerun_filter=flaky_filter)
# Tell pytest to use both the app and model fixtures for all test cases.
# This ensures that configuration is properly applied and that all database
# resources created during tests are cleaned up. These fixtures are defined
# in conftest.py
def test_list(app, firestore):
    for i in range(1, 12):
        firestore.create({'title': u'Book {0}'.format(i)})

    with app.test_client() as c:
        rv = c.get('/')

    assert rv.status == '200 OK'

    body = rv.data.decode('utf-8')
    assert 'Book 1' in body, "Should show books"
    assert len(re.findall('<h4>Book', body)) <= 10, (
        "Should not show more than 10 books")
    assert 'More' in body, "Should have more than one page"


def test_add(app):
    data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'publishedDate': 'Test Date Published',
        'description': 'Test Description'
    }

    with app.test_client() as c:
        rv = c.post('books/add', data=data, follow_redirects=True)

    assert rv.status == '200 OK'
    body = rv.data.decode('utf-8')
    assert 'Test Book' in body
    assert 'Test Author' in body
    assert 'Test Date Published' in body
    assert 'Test Description' in body


def test_edit(app, firestore):
    existing = firestore.create({'title': "Temp Title"})

    with app.test_client() as c:
        rv = c.post(
            'books/%s/edit' % existing['id'],
            data={'title': 'Updated Title'},
            follow_redirects=True)

    assert rv.status == '200 OK'
    body = rv.data.decode('utf-8')
    assert 'Updated Title' in body
    assert 'Temp Title' not in body


def test_delete(app, firestore):
    existing = firestore.create({'title': "Temp Title"})

    with app.test_client() as c:
        rv = c.get(
            'books/%s/delete' % existing['id'],
            follow_redirects=True)

    assert rv.status == '200 OK'
    assert not firestore.read(existing['id'])


def test_upload_image(app):
    data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'publishedDate': 'Test Date Published',
        'description': 'Test Description',
        'image': (BytesIO(b'hello world'), 'hello.jpg')
    }

    with app.test_client() as c:
        rv = c.post('books/add', data=data, follow_redirects=True)

    assert rv.status == '200 OK'
    body = rv.data.decode('utf-8')

    img_tag = re.search('<img.*?src="(.*)"', body).group(1)

    r = requests.get(img_tag)
    assert r.status_code == 200
    assert r.text == 'hello world'


def test_upload_bad_file(app):
    data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'publishedDate': 'Test Date Published',
        'description': 'Test Description',
        'image': (BytesIO(b'<?php phpinfo(); ?>'),
                  '1337h4x0r.php')
    }

    with app.test_client() as c:
        rv = c.post('/books/add', data=data, follow_redirects=True)

    # check we weren't pwned
    assert rv.status == '400 BAD REQUEST'
