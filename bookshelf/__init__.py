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

import logging
import os

from flask import Flask, redirect, url_for, current_app

from oauth2 import oauth2


def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        setup_logging(app)

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)

    # Create a health check handler. Health checks are used by the App Engine
    # Managed VMs environment to determine if an instance is capable of serving
    # requests. This can also be used by load balancers outside of App Engine
    # for the same purpose.
    @app.route('/_ah/health')
    def health_check():
        return 'ok', 200

    # Register all blueprints
    app.register_blueprint(oauth2)

    from .crud import crud
    app.register_blueprint(crud, url_prefix='/books')

    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('crud.list'))

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'cloudsql':
        from . import model_cloudsql
        model = model_cloudsql
    elif model_backend == 'datastore':
        from . import model_datastore
        model = model_datastore
    elif model_backend == 'mongodb':
        from . import model_mongodb
        model = model_mongodb
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model


# [START setup_logging]
def setup_logging(app):
    log_path = app.config.get('LOG_PATH')

    # Handler that outputs all logs to the console
    console_handler = logging.StreamHandler()

    # This handler outputs all logs into general.log
    general_handler = logging.FileHandler(
        os.path.join(log_path, 'general.log'))
    general_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(name)-12s: %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))

    # Configure root logger with the above handlers.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.NOTSET)
    root_logger.addHandler(general_handler)

    # The console handler isn't used in production because cloud logging
    # automatically collects stderr. If you log to both stderr and general.log
    # there would be duplicate logs in the log viewer. This also allows you to
    # easily check for any top-level exceptions or application crashes by
    # viewing just the stderr log without all of the noise from the general
    # log.
    if app.debug:
        root_logger.addHandler(console_handler)
# [END setup_logging]
