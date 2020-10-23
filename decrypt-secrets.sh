#!/bin/bash

# Copyright 2016 Google Inc. All rights reserved.
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

set -euo pipefail

# Always cd to the project root.
readonly root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${root}

# Use SECRET_MANAGER_PROJECT if set, fallback to cloud-devrel-kokoro-resources.
readonly project_id="${SECRET_MANAGER_PROJECT:-cloud-devrel-kokoro-resources}"

# If there's already a secret file, skip retrieving the secret.
if [[ -f "service-account.json" ]]; then
    echo "The secret already exists, skipping."
    exit 0
fi

gcloud secrets versions access latest \
       --secret="getting-started-python-service-account" \
       --project="${project_id}" \
       > service-account.json
