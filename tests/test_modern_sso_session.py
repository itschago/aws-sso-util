import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_ROOT = REPO_ROOT / "lib"
if str(LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(LIB_ROOT))

from aws_sso_lib.config import (
    _get_all_instances_from_config,
    _get_instance_from_profile_config,
    _get_instance_from_sso_session,
)

START_URL = "https://d-example.awsapps.com/start"
SSO_REGION = "us-east-2"


class ModernSSOSessionConfigTests(unittest.TestCase):
    def test_get_instance_from_sso_session(self):
        instance = _get_instance_from_sso_session(
            "nycbs",
            {
                "sso_start_url": START_URL,
                "sso_region": SSO_REGION,
                "sso_registration_scopes": "sso:account:access",
            },
        )
        self.assertIsNotNone(instance)
        self.assertEqual(START_URL, instance.start_url)
        self.assertEqual(SSO_REGION, instance.region)
        self.assertEqual("sso-session nycbs", instance.start_url_source)
        self.assertEqual("sso-session nycbs", instance.region_source)

    def test_profile_resolves_shared_sso_session(self):
        full_config = {
            "sso_sessions": {
                "nycbs": {
                    "sso_start_url": START_URL,
                    "sso_region": SSO_REGION,
                }
            }
        }
        profile = {
            "sso_session": "nycbs",
            "sso_account_id": "123456789012",
            "sso_role_name": "AdministratorAccess",
            "region": "us-east-2",
        }
        instance = _get_instance_from_profile_config(
            "testacct-dev", profile, full_config
        )
        self.assertIsNotNone(instance)
        self.assertEqual(START_URL, instance.start_url)
        self.assertEqual(SSO_REGION, instance.region)

    def test_legacy_profile_still_resolves(self):
        profile = {
            "sso_start_url": START_URL,
            "sso_region": SSO_REGION,
            "sso_account_id": "123456789012",
            "sso_role_name": "AdministratorAccess",
            "region": "us-east-2",
        }
        instance = _get_instance_from_profile_config(
            "testacct-dev", profile, {}
        )
        self.assertIsNotNone(instance)
        self.assertEqual(START_URL, instance.start_url)
        self.assertEqual(SSO_REGION, instance.region)
        self.assertEqual("profile", instance.start_url_source)
        self.assertEqual("profile", instance.region_source)

    def test_all_instances_discovers_modern_sso_sessions(self):
        full_config = {
            "sso_sessions": {
                "nycbs": {
                    "sso_start_url": START_URL,
                    "sso_region": SSO_REGION,
                }
            },
            "profiles": {
                "testacct-dev": {
                    "sso_session": "nycbs",
                    "sso_account_id": "123456789012",
                    "sso_role_name": "AdministratorAccess",
                }
            },
        }
        instances = _get_all_instances_from_config(full_config)
        self.assertEqual(1, len(instances))
        self.assertEqual(START_URL, instances[0].start_url)
        self.assertEqual(SSO_REGION, instances[0].region)

    def test_missing_shared_session_returns_none(self):
        instance = _get_instance_from_profile_config(
            "testacct-dev",
            {"sso_session": "does-not-exist"},
            {"sso_sessions": {}},
            missing_ok=True,
        )
        self.assertIsNone(instance)


if __name__ == "__main__":
    unittest.main()
