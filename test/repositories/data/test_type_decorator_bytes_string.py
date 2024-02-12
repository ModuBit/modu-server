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

from repositories.data.type_decorator import Bytes2String


def test_process_bind_param():
    bytes_string = Bytes2String()
    assert bytes_string.process_bind_param(None, None) == None
    assert bytes_string.process_bind_param(b'1234', None) == base64.b64encode(b'1234').decode('utf-8')
    assert (bytes_string.process_bind_param('Maner·Fan'.encode('utf-8'), None)
            == base64.b64encode('Maner·Fan'.encode('utf-8')).decode('utf-8'))

    random = os.urandom(16)
    assert bytes_string.process_bind_param(random, None) == base64.b64encode(random).decode('utf-8')


def test_process_result_value():
    bytes_string = Bytes2String()
    assert bytes_string.process_result_value(None, None) == None
    assert bytes_string.process_result_value(base64.b64encode(b'1234').decode('utf-8'), None) == b'1234'
    assert (bytes_string.process_result_value(base64.b64encode('Maner·Fan'.encode('utf-8')).decode('utf-8'), None)
            == 'Maner·Fan'.encode('utf-8'))

    random = os.urandom(16)
    assert bytes_string.process_result_value(base64.b64encode(random).decode('utf-8'), None) == random

    manerfan_str = bytes_string.process_bind_param('Maner·Fan'.encode('utf-8'), None)
    assert bytes_string.process_result_value(manerfan_str, None) == 'Maner·Fan'.encode('utf-8')
