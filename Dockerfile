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

# The Google App Engine base image is debian (wheezy) with ca-certificates
# installed.
FROM gcr.io/google_appengine/base

# Install Python, pip, and C dev libraries necessary to compile the most popular
# Python libraries.
RUN apt-get -q update && \
 apt-get install --no-install-recommends -y -q \
   python2.7 python-pip python-dev build-essential git mercurial \
   libffi-dev libssl-dev libxml2-dev \
   libxslt1-dev libpq-dev libmysqlclient-dev libcurl4-openssl-dev \
   libjpeg-dev zlib1g-dev libpng12-dev && \
 apt-get clean && rm /var/lib/apt/lists/*_*

# Upgrade pip (debian package version tends to run a few version behind) and
# install virtualenv system-wide.
RUN pip install --upgrade pip virtualenv

EXPOSE 8080

# Install all application dependencies into a new virtualenv.
WORKDIR /app
RUN virtualenv /env
ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r /app/requirements.txt
ADD . /app

# Set virtualenv environment variables. This is equivalent to running source
# /env/bin/activate
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
ENV PORT 8080

# Clear any existing cmd.
CMD []

# Gunicorn is used to run the application on Google App Engine.
ENTRYPOINT gunicorn -b 0.0.0.0:$PORT main:app
