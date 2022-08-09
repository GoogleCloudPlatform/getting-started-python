# Copyright 2022 Google LLC
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

import main


def fake_validate(assertion):
    if assertion == "Valid":
        return "nobody@example.com", "user0001"
    else:
        return None, None


main.validate_assertion = fake_validate


def test_home_page():
    client = main.app.test_client()

    # Good request check
    r = client.get("/", headers={"X-Goog-IAP-JWT-Assertion": "Valid"})
    assert "nobody@example.com" in r.text

    # Missing header check
    r = client.get("/")
    assert "None" in r.text

    # Bad header check
    r = client.get("/", headers={"X-Goog-IAP-JWT-Assertion": "Not Valid"})
    assert "None" in r.text
