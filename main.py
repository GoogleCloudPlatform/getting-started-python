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


app = bookshelf.create_app(config)


# [START books_queue]
# Make the queue available at the top-level, this allows you to run
# `psqworker main.books_queue`. We have to use the app's context because
# it contains all the configuration for plugins.
# If you were using another task queue, such as celery or rq, you can use this
# section to configure your queues to work with Flask.
with app.app_context():
    books_queue = bookshelf.tasks.get_books_queue()
# [END books_queue]


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
