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

from Crypto.Hash import HMAC, SHA256

from utils.crypto import aes


def encrypt(secret: bytes, key: bytes, plain_bytes: bytes) -> bytes:
    """
    加密
    :param secret: 密钥
    :param key: 密钥
    :param plain_bytes: 待加密字节
    :return: 加密后字节
    """

    key_material = _key_material(secret, key)

    [tag, nonce, cipher_bytes] = aes.encrypt(key_material, plain_bytes)
    return tag + nonce + cipher_bytes


def encrypt_str(secret: str, key: str, plain_content: str) -> str:
    """
    加密
    :param secret: 密钥
    :param key: 密钥
    :param plain_content: 待加密内容
    :return: 加密后内容
    """
    cipher_bytes = encrypt(secret.encode('utf-8'), key.encode('utf-8'), plain_content.encode('utf-8'))
    return cipher_bytes.hex()


def decrypt(secret: bytes, key: bytes, cipher_bytes: bytes) -> bytes:
    """
    解密
    :param secret: 密钥
    :param key: 密钥
    :param cipher_bytes: 待解密字节
    :return: 解密后的字节
    """

    key_material = _key_material(secret, key)

    tag = cipher_bytes[:16]
    nonce = cipher_bytes[16:16 + 15]
    cb = cipher_bytes[16 + 15:]

    return aes.decrypt(key_material, tag, nonce, cb)


def decrypt_str(secret: str, key: str, cipher_content: str) -> str:
    """
        解密
        :param secret: 密钥
        :param key: 密钥
        :param cipher_content: 待解密内容
        :return: 解密后的内容
        """
    plain_bytes = decrypt(secret.encode('utf-8'), key.encode('utf-8'), bytearray.fromhex(cipher_content))
    return plain_bytes.decode('utf-8')


def _key_material(secret: bytes, key: bytes) -> bytes:
    """"
    生成key material
    """
    hmac = HMAC.new(secret, digestmod=SHA256)
    hmac.update(key)
    return hmac.digest()
