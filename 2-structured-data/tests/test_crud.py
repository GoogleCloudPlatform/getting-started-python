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

import bookshelf
import config
from flaky import flaky
from gcloud.exceptions import ServiceUnavailable
import pytest


@pytest.yield_fixture(params=['datastore', 'cloudsql', 'mongodb'])
def app(request):
    """This fixtures provides a Flask app instance configured for testing.

    Because it's parametric, it will cause every test that uses this fixture
    to run three times: one time for each backend (datastore, cloudsql, and
    mongodb).

    It also ensures the tests run within a request context, allowing
    any calls to flask.request, flask.current_app, etc. to work."""
    app = bookshelf.create_app(
        config,
        testing=True,
        config_overrides={
            'DATA_BACKEND': request.param
        })

    with app.test_request_context():
        yield app


@pytest.yield_fixture
def model(monkeypatch, app):
    """This fixture provides a modified version of the app's model that tracks
    all created items and deletes them at the end of the test.

    Any tests that directly or indirectly interact with the database should use
    this to ensure that resources are properly cleaned up.

    Monkeypatch is provided by pytest and used to patch the model's create
    method.

    The app fixture is needed to provide the configuration and context needed
    to get the proper model object.
    """
    model = bookshelf.get_model()

    ids_to_delete = []

    # Monkey-patch create so we can track the IDs of every item
    # created and delete them after the test case.
    original_create = model.create

    def tracking_create(*args, **kwargs):
        res = original_create(*args, **kwargs)
        ids_to_delete.append(res['id'])
        return res

    monkeypatch.setattr(model, 'create', tracking_create)

    yield model

    # Delete all items that we created during tests.
    list(map(model.delete, ids_to_delete))


def flaky_filter(info, *args):
    """Used by flaky to determine when to re-run a test case."""
    _, e, _ = info
    return isinstance(e, ServiceUnavailable)


# Mark all test cases in this class as flaky, so that if errors occur they
# can be retried. This is useful when databases are temporarily unavailable.
@flaky(rerun_filter=flaky_filter)
# Tell pytest to use both the app and model fixtures for all test cases.
# This ensures that configuration is properly applied and that all database
# resources created during tests are cleaned up.
@pytest.mark.usefixtures('app', 'model')
class TestCrudActions(object):

    def test_list(self, app, model):
        for i in range(1, 12):
            model.create({'title': u'Book {0}'.format(i)})

        with app.test_client() as c:
            rv = c.get('/books/')

        assert rv.status == '200 OK'

        body = rv.data.decode('utf-8')
        assert 'Book 1' in body, "Should show books"
        # Ordering is lexical, so 9 will be on page two and 10 and 11 will
        # be after 1.
        assert 'Book 9' not in body, "Should not show more than 10 books"
        assert 'More' in body, "Should have more than one page"

    def test_add(self, app):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publishedDate': 'Test Date Published',
            'description': 'Test Description'
        }

        with app.test_client() as c:
            rv = c.post('/books/add', data=data, follow_redirects=True)

        assert rv.status == '200 OK'
        body = rv.data.decode('utf-8')
        assert 'Test Book' in body
        assert 'Test Author' in body
        assert 'Test Date Published' in body
        assert 'Test Description' in body

    def test_edit(self, app, model):
        existing = model.create({'title': "Temp Title"})

        with app.test_client() as c:
            rv = c.post(
                '/books/%s/edit' % existing['id'],
                data={'title': 'Updated Title'},
                follow_redirects=True)

        assert rv.status == '200 OK'
        body = rv.data.decode('utf-8')
        assert 'Updated Title' in body
        assert 'Temp Title' not in body

    def test_delete(self, app, model):
        existing = model.create({'title': "Temp Title"})

        with app.test_client() as c:
            rv = c.get(
                '/books/%s/delete' % existing['id'],
                follow_redirects=True)

        assert rv.status == '200 OK'
        assert not model.read(existing['id'])
