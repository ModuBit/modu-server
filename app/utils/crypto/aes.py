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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def _cipher(key_material: bytes, iv: bytes) -> Cipher:
    """
    生成Cipher
    """

    # 创建哈希上下文
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

    # 添加密码到哈希上下文中
    digest.update(key_material)

    # 计算得到密钥
    key = digest.finalize()

    # 配置AES加密对象
    return Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())


def encrypt(key_material: bytes, iv: bytes, plain_bytes: bytes) -> bytes:
    """
    加密
    :param key_material: 密钥
    :param salt: 盐值
    :param iv: 初始向量
    :param plain_bytes: 待加密字节
    :return: 加密后字节
    """

    encryptor = _cipher(key_material, iv).encryptor()

    # PKCS7填充
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plain_bytes) + padder.finalize()

    # 加密
    return encryptor.update(padded_plaintext) + encryptor.finalize()


def decrypt(key_material: bytes, iv: bytes, cipher_bytes: bytes) -> bytes:
    """
    解密
    :param key_material: 密钥
    :param iv: 初始向量
    :param cipher_bytes: 待解密字节
    :return: 解密后字节
    """

    decryptor = _cipher(key_material, iv).decryptor()

    # 解密
    padded_plaintext = decryptor.update(cipher_bytes) + decryptor.finalize()

    # 移除PKCS7填充
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_plaintext) + unpadder.finalize()
