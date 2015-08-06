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
#! /bin/bash

# [START startup]
# Talk to the metadata server to get the project id
PROJECTID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")

# Install logging monitor and configure it to pickup application logs
# [START logging]
curl -s "https://storage.googleapis.com/signals-agents/logging/google-fluentd-install.sh" | bash

cat >/etc/google-fluentd/config.d/pythonapp.conf << EOF
<source>
  type tail
  format json
  path /opt/app/general.log
  pos_file /var/tmp/fluentd.pythonapp-general.pos
  tag pythonapp-general
</source>
EOF

service google-fluentd restart &
# [END logging]

# Install dependencies from apt
apt-get update
apt-get install -y git build-essential supervisor python python-dev python-pip libffi-dev

# pip from apt is out of date, so make it update itself and install virtualenv.
pip install --upgrade pip virtualenv

# Get the source code
git config --global credential.helper gcloud.sh
git clone https://source.developers.google.com/p/$PROJECTID /opt/app

# Install app dependencies
virtualenv /opt/app/env
# TODO: remove trusted host
/opt/app/env/bin/pip install -r /opt/app/requirements.txt  --trusted-host=130.211.177.15

# Install gunicorn. We'll use gunicorn instead of flask's built-in server for
# production serving.
/opt/app/env/bin/pip install gunicorn

# Create a start-app script that activates the virtualenv and runs the app
# using gunicorn. The number of workers assumes an f1-micro/g1-small instance, 
# but larger instances should be configured with more workers. The rule of
# thumb  is 2 * cores + 1. 
cat >/opt/app/start-app.sh << EOF
#!/bin/bash
cd /opt/app
source env/bin/activate
gunicorn main:app --workers 2 --bind 0.0.0.0:8080
EOF

chmod u+x /opt/app/start-app.sh

# Create a pythonapp user. The application will run as this user.
useradd -m -d /home/pythonapp pythonapp
chown -R pythonapp:pythonapp /opt/app

# Configure supervisor to start gunicorn inside of our virtualenv and run the
# applicaiton.
cat >/etc/supervisor/conf.d/python-app.conf << EOF
[program:pythonapp]
directory=/opt/app
command=/opt/app/start-app.sh
autostart=true
autorestart=true
user=pythonapp
environment=HOME="/home/pythonapp",USER="pythonapp",PYTHON_ENV="production"
EOF

supervisorctl reread
supervisorctl update

# Application should now be running under supervisor
# [END startup]
