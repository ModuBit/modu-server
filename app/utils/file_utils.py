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

import hashlib
import time
from typing import BinaryIO
from urllib.parse import quote_plus, unquote_plus

from config import app_config
from fastapi import UploadFile
from utils.crypto import composition
from utils.errors.base_error import BaseServiceError


def readable_size(number: int | float) -> str:
    """
    将数字转换为可读的格式
    """
    if number < 1024:
        return f"{number}B"
    elif number < 1024 * 1024:
        return f"{number / 1024}KB"
    elif number < 1024 * 1024 * 1024:
        return f"{number / 1024 / 1024}MB"
    elif number < 1024 * 1024 * 1024 * 1024:
        return f"{number / 1024 / 1024 / 1024}GB"
    else:
        return f"{number / 1024 / 1024 / 1024 / 1024}TB"


def get_number_from_string(number_expr: str | float | int | None) -> float | int | None:
    """
    从字符串中获取数字

    参数:
        number_expr: 输入的字符串、浮点数或整数
            支持以下格式:
            - 纯数字: "123", 123, 123.45
            - 带单位的字符串: "2KB", "5MB", "1.5GB"
            - 数学表达式: "2 * 1024"

    返回:
        转换后的数值(整数或浮点数)

    示例:
        >>> get_number_from_string("2MB")
        2097152
        >>> get_number_from_string("1.5GB")
        1610612736
        >>> get_number_from_string("2 * 1024")
        2048
    """

    if number_expr is None:
        return None

    if isinstance(number_expr, (int, float)):
        return number_expr

    if not isinstance(number_expr, str):
        raise ValueError(f"不支持的输入类型: {type(number_expr)}")

    # 处理类似 "2MB" 的字符串格式或 "2 * 1024" 的表达式
    size_str = number_expr.strip().upper()

    # 处理数学表达式
    if "*" in size_str:
        try:
            return eval(size_str)
        except:
            raise ValueError(f"无效的数学表达式: {number_expr}")

    # 处理带单位的值
    units = {
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024,
    }

    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                return int(float(size_str[: -len(unit)]) * multiplier)
            except:
                raise ValueError(f"无效的大小格式: {number_expr}")

    # 处理纯数字
    try:
        return int(float(number_expr))
    except:
        raise ValueError(f"无效的数字格式: {number_expr}")


def get_file_name_and_ext(filename: str) -> tuple[str, str]:
    """
    获取文件名和扩展名
    """
    file_name = filename
    file_ext = ""
    if "." in file_name:
        file_ext = file_name.rsplit(".", 1)[1].lower()
        file_name = file_name[: -len(file_ext) - 1]
    return file_name, file_ext


def validate_file_type(mime_type: str, filename: str, accept: str) -> bool:
    """
    验证文件类型是否符合规则
    :param file: 上传的文件
    :param accept: 文件类型规则，例如 "image/*,.png"
    :return: 是否符合规则
    """
    if not accept:
        return True

    # 分割规则
    rules = [rule.strip() for rule in accept.split(",")]

    # 获取文件的扩展名
    _, file_ext = get_file_name_and_ext(filename)

    for rule in rules:
        # MIME 类型通配符匹配 (例如 image/*)
        if rule.endswith("/*"):
            mime_prefix = rule[:-2]
            if mime_type and mime_type.startswith(mime_prefix):
                return True

        # 完整 MIME 类型匹配 (例如 image/png)∑
        elif "/" in rule:
            if mime_type == rule:
                return True

        # 文件扩展名匹配 (例如 .png)
        elif rule.startswith("."):
            if file_ext == rule.lower():
                return True

    return False


def file_hash(file: BinaryIO) -> str:
    """
    获取文件的哈希值
    :param file: 二进制文件对象
    :return: 文件的MD5哈希值
    """
    # 记录当前文件指针位置
    current_pos = file.tell()

    # 计算哈希值
    hash_value = hashlib.md5(file.read()).hexdigest()

    # 恢复文件指针位置
    file.seek(current_pos)

    return hash_value


def file_signature(file_key: str, expires: int) -> tuple[int, str]:
    """
    生成文件签名
    :param file_key: 文件KEY
    :param expires: 过期时间
    :return: 文件KEY, 过期时间, 签名
    """
    real_expires = int(time.time()) + expires
    signature = composition.encrypt_str(
        app_config.security.secret, f"{real_expires}", f"{file_key}{real_expires}"
    )
    signature = hashlib.md5(signature.encode()).hexdigest()
    return (real_expires, signature)

def file_signature_check(file_key: str, expires: int, signature: str):
    """
    验证文件签名
    """
    file_key = unquote_plus(file_key)
    signature = composition.encrypt_str(
        app_config.security.secret, f"{expires}", f"{file_key}{expires}"
    )
    signature = hashlib.md5(signature.encode()).hexdigest()
    if signature != signature:
        raise BaseServiceError("签名验证失败")

    if expires < int(time.time()):
        raise BaseServiceError("签名已过期")
