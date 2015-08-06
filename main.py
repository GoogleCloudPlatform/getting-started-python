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

import bookshelf
import config


def create_app():
    # Environment configuration
    env = os.environ.get('PYTHON_ENV', 'development')
    port = 8080

    # Production environment configuration.
    if env == 'production':
        host = '0.0.0.0'
        debug = False
    # Local environment configuration.
    else:
        host = '127.0.0.1'
        debug = True

    # Create the application, passing in any configuration needed from the
    # environment.
    app = bookshelf.create_app(config, debug=debug)

    return app, host, port


app, host, port = create_app()


# [START books_queue]
# Make the queue available at the top-level, this allows you to run
# `psqworker main.books_queue`. We have to use the app's context because
# it contains all the configuration for plugins.
# If you were using another task queue, such as celery or rq, you can use this
# section to configure your queues to work with Flask.
with app.app_context():
    books_queue = bookshelf.tasks.get_books_queue()
# [END books_queue]


if __name__ == '__main__':
    app.run(host, port)
