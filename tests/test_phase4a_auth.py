from __future__ import annotations

import unittest
from unittest.mock import patch

from nba_oracle.auth import create_access_token, decode_access_token, hash_password, verify_password


class Phase4AAuthTests(unittest.TestCase):
    def test_password_hash_roundtrip(self) -> None:
        password_hash = hash_password("secret-pass")
        self.assertTrue(verify_password("secret-pass", password_hash))
        self.assertFalse(verify_password("wrong-pass", password_hash))

    def test_access_token_roundtrip(self) -> None:
        with patch("nba_oracle.auth.ORACLE_SECRET_KEY", "test-secret-key-material-0123456789"):
            token = create_access_token("oracle-operator", extra={"role": "operator"})
            payload = decode_access_token(token)
        self.assertEqual(payload["sub"], "oracle-operator")
        self.assertEqual(payload["role"], "operator")


if __name__ == "__main__":
    unittest.main()
