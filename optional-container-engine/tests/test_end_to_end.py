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

import os
import time
import unittest

from bs4 import BeautifulSoup
import httplib2
from nose.plugins.attrib import attr
from six.moves.urllib.parse import urlencode


@attr('e2e')
class EndToEndTest(unittest.TestCase):
    """ Tests designed to be run against live environments.

    Unlike the integration tests in the other packages, these tests are
    designed to be run against fully-functional live environments.

    To run locally, start both main.py and worker.py and run this file.

    It can be run against a live environment by settings the E2E_HOST and
    E2E_PORT environment variables before running the tests:

        E2E_HOST=your-app-id.appspot.com E2E_PORT=80 \
        nosetests tests/test_end_to_end.py

    """

    def setUp(self):
        host = os.environ.get('E2E_HOST', 'localhost')
        port = os.environ.get('E2E_PORT', '8080')
        self.host = "http://{}:{}".format(host, port)

    def testCreateBook(self):
        h = httplib2.Http()

        data = {
            'title': 'a confederacy of dunces',
        }

        headers = {'Content-type': 'application/x-www-form-urlencoded'}

        resp, content = h.request(self.host + "/books/add", "POST",
                                  urlencode(data),
                                  headers=headers)
        created_book = resp['location']
        self.assertEquals(resp.status, 302)
        book_id = created_book.split('/')[-1]
        time.sleep(5)

        resp, content = h.request(created_book)

        self.assertEquals(resp.status, 200)
        soup = BeautifulSoup(content)

        title = soup.find('h4', 'book-title').contents[0].strip()
        self.assertEquals(title, 'A Confederacy of Dunces')

        author = soup.find('h5', 'book-author').string
        self.assertIn('John Kennedy Toole', author)

        description = soup.find('p', 'book-description').string
        self.assertIn('Ignatius Reilly', description)

        image_tag = soup.find('img', 'book-image')['src']
        resp, content = h.request(image_tag)
        self.assertEquals(resp.status, 200)

        resp, content = h.request(self.host + "/books/{}/delete"
                                  .format(book_id))
        self.assertEquals(resp.status, 200)
