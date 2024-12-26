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

from Crypto.Cipher import AES


def encrypt(key_material: bytes, plain_bytes: bytes) -> tuple[bytes, bytes, bytes]:
    """
    加密
    :param key_material: 密钥
    :param plain_bytes: 待加密字节
    :return: 加密后字节
    """

    cipher = AES.new(key_material, AES.MODE_OCB)
    cipher_bytes, tag = cipher.encrypt_and_digest(plain_bytes)

    return tag, cipher.nonce, cipher_bytes


def decrypt(
    key_material: bytes, tag: bytes, nonce: bytes, cipher_bytes: bytes
) -> bytes:
    """
    解密
    :param key_material: 密钥
    :param tag: tag
    :param nonce: nonce
    :param cipher_bytes: 待解密字节
    :return: 解密后字节
    """

    cipher = AES.new(key_material, AES.MODE_OCB, nonce=nonce)
    return cipher.decrypt_and_verify(cipher_bytes, tag)
