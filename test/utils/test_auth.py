"""
Copyright 2024 Maner·Fan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time

import pytest

from utils import auth
from utils.errors.base_error import UnauthorizedError


def test_password_hash():
    with pytest.raises(TypeError) as exc_info:
        auth.hash_password(None)
    assert str(exc_info.value) == "secret must be unicode or bytes, not None"

    with pytest.raises(TypeError) as exc_info:
        auth.verify_password(None, auth.hash_password("123456"))
    assert str(exc_info.value) == "secret must be unicode or bytes, not None"

    assert not auth.verify_password("123456", None)
    assert auth.verify_password("123456", auth.hash_password("123456"))
    assert not auth.verify_password("1234567", auth.hash_password("123456"))


def test_jose():
    secret = "d0b3bf3fa3f693cc680fb2bf6a896e18a76fa93b800c4c6d27dedf1edb49888b"
    algorithm = "HS256"

    payload = {"name": "Maner·Fan", "github": "https://github.com/manerfan"}

    encoded = auth.jose_encode(payload, secret, algorithm, 1)
    decoded = auth.jose_decode(encoded, secret, algorithm)
    assert decoded["name"] == payload["name"]
    assert decoded["github"] == payload["github"]
    assert decoded["exp"] is not None

    with pytest.raises(UnauthorizedError) as exc_info:
        encoded = auth.jose_encode(payload, secret, algorithm, 0.01)
        time.sleep(2)
        auth.jose_decode(encoded, secret, algorithm)
    assert exc_info is not None
    assert str(exc_info.value) == "Token has expired."

    with pytest.raises(UnauthorizedError) as exc_info:
        encoded = auth.jose_encode(payload, secret, algorithm, 1)
        auth.jose_decode(encoded + ".123", secret, algorithm)
    assert exc_info is not None
    assert str(exc_info.value) == "Invalid Token."
