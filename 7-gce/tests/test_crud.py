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

import unittest

import bookshelf
from bookshelf import tasks
import config
from flaky import flaky
from gcloud.exceptions import ServiceUnavailable
import mock
from nose.plugins.attrib import attr
from oauth2client.client import OAuth2Credentials


def flaky_filter(e, *args):
    return isinstance(e, ServiceUnavailable)


@flaky(rerun_filter=flaky_filter)
class IntegrationBase(unittest.TestCase):

    def createBooks(self, n=1):
        with self.app.test_request_context():
            for i in range(1, n + 1):
                self.model.create({'title': u'Book {0}'.format(i)})

    def setUp(self):
        self.app = bookshelf.create_app(
            config,
            testing=True,
            config_overrides={
                'DATA_BACKEND': self.backend
            }
        )

        with self.app.app_context():
            self.model = bookshelf.get_model()

        self.ids_to_delete = []

        # Monkey-patch create so we can track the IDs of every item
        # created and delete them during tearDown.
        self.original_create = self.model.create

        def tracking_create(*args, **kwargs):
            res = self.original_create(*args, **kwargs)
            self.ids_to_delete.append(res['id'])
            return res

        self.model.create = tracking_create

        # Monkey-patch get_books_queue to prevents pubsub events
        # from firing
        self.original_get_books_queue = tasks.get_books_queue
        tasks.get_books_queue = mock.Mock()

    def tearDown(self):

        # Delete all items that we created during tests.
        with self.app.test_request_context():
            list(map(self.model.delete, self.ids_to_delete))

        self.model.create = self.original_create
        tasks.get_books_queue = self.original_get_books_queue

    def _generate_credentials(self, scopes=('email', 'profile')):
        return OAuth2Credentials(
            'access_token',
            'client_id',
            'client_secret',
            'refresh_token',
            '3600',
            None,
            'Test',
            id_token={
                'sub': '123',
                'email': 'user@example.com'
            },
            scopes=scopes)


@attr('slow')
class CrudTestsMixin(object):
    def testList(self):
        self.createBooks(11)

        with self.app.test_client() as c:
            rv = c.get('/books/')

        assert rv.status == '200 OK'

        body = rv.data.decode('utf-8')
        assert 'Book 1' in body, "Should show books"
        # Ordering is lexical, so 9 will be on page two and 10 and 11 will
        # be after 1.
        assert 'Book 9' not in body, "Should not show more than 10 books"
        assert 'More' in body, "Should have more than one page"

    def testListByUser(self):
        data1 = {
            'title': 'Book 1',
            'createdById': 'abc'
        }

        data2 = {
            'title': 'Book 2',
            'createdById': 'def'
        }

        with self.app.test_request_context():
            self.model.create(data1)
            self.model.create(data2)

        with self.app.test_client() as c:
            rv = c.get('/books/')
            assert rv.status == '200 OK'
            body = rv.data.decode('utf-8')
            assert 'Book 1' in body, "Should show both books"
            assert 'Book 2' in body, "Should show both books"

        with self.app.test_client() as c:
            with c.session_transaction() as session:
                session['profile'] = {'id': 'abc'}
                session['google_oauth2_credentials'] = \
                    self._generate_credentials().to_json()

            rv = c.get('/books/mine')
            assert rv.status == '200 OK'
            body = rv.data.decode('utf-8')
            assert 'Book 1' in body, "Should show book 1"
            assert 'Book 2' not in body, "Should not show both books"

    def testAddAndView(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publishedDate': 'Test Date Published',
            'description': 'Test Description'
        }

        with self.app.test_client() as c:
            rv = c.post('/books/add', data=data, follow_redirects=True)

        assert rv.status == '200 OK'

        body = rv.data.decode('utf-8')
        assert 'Test Book' in body
        assert 'Test Author' in body
        assert 'Test Date Published' in body
        assert 'Test Description' in body

    def testEditAndView(self):
        with self.app.test_request_context():
            existing = self.model.create({'title': "Temp Title"})

        with self.app.test_client() as c:
            rv = c.post(
                '/books/%s/edit' % existing['id'],
                data={'title': 'Updated Title'},
                follow_redirects=True)

        assert rv.status == '200 OK'

        body = rv.data.decode('utf-8')
        assert 'Updated Title' in body
        assert 'Temp Title' not in body

    def testDelete(self):
        with self.app.test_request_context():
            existing = self.model.create({'title': "Temp Title"})

        with self.app.test_client() as c:
            rv = c.get(
                '/books/%s/delete' % existing['id'],
                follow_redirects=True)

        assert rv.status == '200 OK'

        with self.app.test_request_context():
            assert not self.model.read(existing['id'])


@attr('datastore')
class TestDatastore(CrudTestsMixin, IntegrationBase):
    backend = 'datastore'


@attr('cloudsql')
class TestCloudSql(CrudTestsMixin, IntegrationBase):
    backend = 'cloudsql'


@attr('mongodb')
class TestMongo(CrudTestsMixin, IntegrationBase):
    backend = 'mongodb'
