# Copyright 2016 Google Inc.
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

from flask import current_app
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb


builtin_list = list


def init_app(app):
    pass


# [START model]
class Book(ndb.Model):
    author = ndb.StringProperty()
    description = ndb.StringProperty(indexed=False)
    publishedDate = ndb.StringProperty()
    title = ndb.StringProperty()
# [END model]


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()
    book = {}
    book['id'] = entity.key.id()
    book['author'] = entity.author
    book['description'] = entity.description
    book['publishedDate'] = entity.publishedDate
    book['title'] = entity.title
    return book
# [END from_datastore]



# [START list]
def list(limit=10, cursor=None):
    if cursor:
        cursor = Cursor(urlsafe=cursor)
    query = Book.query().order(Book.title)
    entities, cursor, more = query.fetch_page(limit, start_cursor=cursor)
    entities = builtin_list(map(from_datastore, entities))
    return entities, cursor.urlsafe() if len(entities) == limit else None
# [END list]


# [START read]
def read(id):
    book_key = ndb.Key('Book', int(id))
    results = book_key.get()
    return from_datastore(results)
# [END read]


# [START update]
def update(data, id=None):
    if id:
        key = ndb.Key('Book', int(id))
        book = key.get()
    else:
        book = Book()
    book.author = data['author']
    book.description = data['description']
    book.publishedDate = data['publishedDate']
    book.title = data['title']
    book.put()
    return from_datastore(book)

create = update
# [END update]


# [START delete]
def delete(id):
    key = ndb.Key('Book', int(id))
    key.delete()
# [END delete]
