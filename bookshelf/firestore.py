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

# [START bookshelf_firestore_client_import]
from google.cloud import firestore
# [END bookshelf_firestore_client_import]

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict


def next_page(limit=10, cursor=None):
    db = firestore.Client()

    query = db.collection(u'Book').limit(limit).order_by(u'title')

    if cursor:
        # Construct a new query starting at this document.
        query = query.start_after({ u'title': cursor })

    docs = query.stream()
    docs = list(map(document_to_dict, docs))

    next_cursor = None
    if limit == len(docs):
        # Get the last document from the results and set as the next cursor.
        next_cursor = docs[-1][u'title']
    return docs, next_cursor


def read(id):
    # [START bookshelf_firestore_client]
    db = firestore.Client()
    book_ref = db.collection(u'Book').document(id)
    snapshot = book_ref.get()
    # [END bookshelf_firestore_client]
    return document_to_dict(snapshot)


def update(data, id=None):
    db = firestore.Client()
    book_ref = db.collection(u'Book').document(id)
    book_ref.set(data)
    return document_to_dict(book_ref.get())


create = update


def delete(id):
    db = firestore.Client()
    book_ref = db.collection(u'Book').document(id)
    book_ref.delete()
