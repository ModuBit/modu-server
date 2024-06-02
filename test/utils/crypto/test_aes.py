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

import base64
import os

from utils.crypto import aes


def test_aes():
    [tag, nonce, cipher_bytes] = aes.encrypt(b'1234567890123456', 'Hello Maner·Fan'.encode('utf-8'))
    decrypted = aes.decrypt(b'1234567890123456', tag, nonce, cipher_bytes)
    assert decrypted == 'Hello Maner·Fan'.encode('utf-8')


def test_urandom_16():
    for _ in range(16):
        _iv = os.urandom(16)
        assert len(_iv) == 16

        _b64 = base64.b64encode(_iv).decode("utf-8")
        assert len(_b64) == 24
