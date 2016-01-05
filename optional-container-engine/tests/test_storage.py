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

import httplib2
from nose.plugins.attrib import attr
from six import BytesIO
from test_crud import IntegrationBase


@attr('slow')
class StorageIntegrationTest(IntegrationBase):

    backend = 'datastore'

    def testAddWithImage(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publishedDate': 'Test Date Published',
            'description': 'Test Description',
            'image': (BytesIO(b'hello world'), 'hello.jpg')
        }

        with self.app.test_client() as c:
            rv = c.post('/books/add', data=data, follow_redirects=True)

        assert rv.status == '200 OK'
        body = rv.data.decode('utf-8')

        img_tag = re.search('<img.*?src="(.*)"', body).group(1)

        http = httplib2.Http()
        resp, content = http.request(img_tag)
        assert resp.status == 200
        assert content == b'hello world'

    def testAddBadFileType(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publishedDate': 'Test Date Published',
            'description': 'Test Description',
            'image': (BytesIO(b'<?php phpinfo(); ?>'),
                      '1337h4x0r.php')
        }

        with self.app.test_client() as c:
            rv = c.post('/books/add', data=data,
                        follow_redirects=True)
        # check we weren't pwned
        assert rv.status == '400 BAD REQUEST'
