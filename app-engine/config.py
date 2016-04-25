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

"""
This file contains all of the configuration values for the application.
Update this file with the values for your specific Google Cloud project.
You can create and manage projects at https://console.developers.google.com
"""

# There are two different ways to store the data in the application.
# You can choose 'datastore', or 'cloudsql'. Be sure to
# configure the respective settings for the one you choose below.
# You do not have to configure the other data backend. If unsure, choose
# 'datastore' as it does not require any additional configuration.
DATA_BACKEND = 'datastore'

# SQLAlchemy configuration
# Replace user, pass, host, and database with the respective values of your
# Cloud SQL instance.
SQLALCHEMY_DATABASE_URI = \
    'mysql+pymysql://user:password@host/database'
