# Copyright 2016: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from tests.unit import test


class HealthApiTestCase(test.TestCase):

    def setUp(self):
        super(HealthApiTestCase, self).setUp()
        self.config = {
            "use_fake_api_data": False,
            "services": {},
        }
        self.mock_config(self.config)

    @mock.patch("ceagle.api.client.get_client")
    def test_status_health_api(self, mock_get_client):
        mock_get_client.return_value.get.return_value = ({"test": 1}, 200)
        resp = self.get("/api/v1/status/health/day")
        self.assertEqual((200, {"test": 1}), resp)
        mock_get_client.return_value.get.assert_called_once_with(
            "/api/v1/health/day")

    @mock.patch("ceagle.api.client.get_client")
    def test_region_status_health_api(self, mock_get_client):
        mock_get_client.return_value.get.return_value = ({"test": 2}, 200)
        resp = self.get("/api/v1/region/test_region/status/health/day")
        self.assertEqual((200, {"test": 2}), resp)
        mock_get_client.return_value.get.assert_called_with(
            "/api/v1/region/test_region/health/day")

    def test_health_api_no_endpoint(self):
        code, resp = self.get("/api/v1/status/health/day")
        self.assertEqual(404, code)
        self.assertEqual({"error": "Unknown service 'health'"}, resp)

        code, resp = self.get("/api/v1/region/test_region/status/health/day")
        self.assertEqual(404, code)
        self.assertEqual({"error": "Unknown service 'health'"}, resp)


class AvailabilityApiTestCase(test.TestCase):

    def setUp(self):
        super(AvailabilityApiTestCase, self).setUp()
        self.config = {
            "use_fake_api_data": False,
            "services": {"availability": "foo_endpoint"},
        }
        self.mock_config(self.config)

    @mock.patch("ceagle.api.client.get_client")
    def test_get_status_availability(self, mock_get_client):
        mock_get_client.return_value.get.return_value = ("ok", 42)
        resp = self.get("/api/v1/status/availability/day")
        self.assertEqual((42, "ok"), resp)
        mock_get_client.return_value.get.assert_called_once_with(
            "/api/v1/availability/day")

    @mock.patch("ceagle.api.client.get_client")
    def test_get_region_status_availability(self, mock_get_client):
        mock_get_client.return_value.get.return_value = ("ok", 42)
        resp = self.get("/api/v1/region/foo_region/status/availability/day")
        self.assertEqual((42, "ok"), resp)
        mock_get_client.return_value.get.assert_called_once_with(
            "/api/v1/region/foo_region/availability/day")


class StatusApiTestCase(test.TestCase):

    def setUp(self):
        super(StatusApiTestCase, self).setUp()
        self.config = {
            "use_fake_api_data": False,
            "services": {
                "availability": "foo_endpoint",
                "health": "bar_endpoint",
            },
        }
        self.mock_config(self.config)

    @mock.patch("ceagle.api.v1.status.client.get_client")
    def test_get_status(self, mock_client):
        health_resp = {"health": {"foo": {"fci": 42}}}
        mock_health_client = mock.Mock()
        mock_health_client.get.return_value = (health_resp, 200)

        avail_resp = {"availability": {"bar": {"availability": 24}}}
        mock_avail_client = mock.Mock()
        mock_avail_client.get.return_value = (avail_resp, 200)
        mock_client.side_effect = [mock_health_client, mock_avail_client]

        uri = "/api/v1/status/day"
        code, resp = self.get(uri)
        self.assertEqual(200, code)
        mock_health_client.get.assert_called_once_with(
            "/api/v1/health/day")
        mock_avail_client.get.assert_called_once_with(
            "/api/v1/availability/day")
        expected = {
            "period": "day",
            "status": {
                "bar": {"availability": 24, "health": None,
                        "performance": None, "sla": None},
                "foo": {"availability": None, "health": 42,
                        "performance": None, "sla": None}
            }
        }
        self.assertEqual(expected, resp)

    @mock.patch("ceagle.api.v1.status.client.get_client")
    def test_get_region_status(self, mock_client):
        health_resp = {"health": {"foo": {"fci": 42}}}
        mock_health_client = mock.Mock()
        mock_health_client.get.return_value = (health_resp, 200)

        avail_resp = {"availability": {"bar": {"availability": 24}}}
        mock_avail_client = mock.Mock()
        mock_avail_client.get.return_value = (avail_resp, 200)
        mock_client.side_effect = [mock_health_client, mock_avail_client]

        uri = "/api/v1/region/foo_region/status/day"
        code, resp = self.get(uri)
        self.assertEqual(200, code)
        mock_health_client.get.assert_called_once_with(
            "/api/v1/region/foo_region/health/day")
        mock_avail_client.get.assert_called_once_with(
            "/api/v1/region/foo_region/availability/day")
        expected = {
            "period": "day",
            "status": {
                "bar": {"availability": 24, "health": None,
                        "performance": None, "sla": None},
                "foo": {"availability": None, "health": 42,
                        "performance": None, "sla": None}
            }
        }
        self.assertEqual(expected, resp)
