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

import logging, os

from flask import current_app, Flask, Markup, flash, redirect, render_template, url_for, request
import firestore, storage, google.cloud.error_reporting, google.cloud.logging

# [START upload_image_file]
def upload_image_file(file):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not file:
        return None

    public_url = storage.upload_file(
        file.read(),
        file.filename,
        file.content_type
    )

    current_app.logger.info(
        "Uploaded file %s as %s.", file.filename, public_url)

    return public_url
# [END upload_image_file]

app = Flask(__name__)
app.config.update(
    SECRET_KEY='secret',
    PROJECT_ID=os.getenv('GOOGLE_CLOUD_PROJECT'),
    CLOUD_STORAGE_BUCKET=os.getenv('GOOGLE_STORAGE_BUCKET'),
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg', 'gif'])
)

app.debug = False
app.testing = False

# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)
    client = google.cloud.logging.Client(app.config['PROJECT_ID'])
    # Attaches a Google Stackdriver logging handler to the root logger
    client.setup_logging(logging.INFO)

# Add an error handler. This is useful for debugging the live application,
# however, you should disable the output of the exception for production
# applications.
@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


@app.route("/")
def list():
    cursor = request.args.get('cursor', None)
    books, next_cursor = firestore.next_page(cursor=cursor)

    return render_template(
        "list.html",
        books=books,
        cursor=next_cursor)


@app.route('/books/<id>')
def view(id):
    book = firestore.read(id)
    return render_template("view.html", book=book)


@app.route('/books/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        # If an image was uploaded, update the data to point to the new image.
        # [START image_url]
        image_url = upload_image_file(request.files.get('image'))
        # [END image_url]

        # [START image_url2]
        if image_url:
            data['imageUrl'] = image_url
        # [END image_url2]

        book = firestore.create(data)

        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Add", book={})


@app.route('/books/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    book = firestore.read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        image_url = upload_image_file(request.files.get('image'))

        if image_url:
            data['imageUrl'] = image_url

        book = firestore.update(data, id)

        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Edit", book=book)


@app.route('/books/<id>/delete')
def delete(id):
    firestore.delete(id)
    return redirect(url_for('.list'))

@app.route('/logs')
def logs():
    logging.info('Hey, you triggered a custom log entry. Good job!')
    flash(Markup('''You triggered a custom log entry. You can view it in the
        <a href="https://console.cloud.google.com/logs">Cloud Console</a>'''))
    return redirect(url_for('.list'))

@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')

# Add an error handler that reports exceptions to Stackdriver Error
# Reporting. Note that this error handler is only used when debug
# is False
@app.errorhandler(500)
def server_error(e):
    client = google.cloud.error_reporting.Client(app.config['PROJECT_ID'])
    client.report_exception(
        http_context=google.cloud.error_reporting.build_flask_context(request))
    return """
    An internal error occurred.
    """, 500

# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
