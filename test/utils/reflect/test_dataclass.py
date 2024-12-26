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

from dataclasses import dataclass

from utils.reflect.dataclass import tolerant


@tolerant
@dataclass
class DataClassTest:
    v_int: int | None
    v_str: str | None
    v_list: list[str] | None


def test_tolerant():
    data1 = DataClassTest()
    assert data1.v_int is None
    assert data1.v_str is None
    assert data1.v_list is None

    data2 = DataClassTest(v_int=1)
    assert data2.v_int == 1
    assert data2.v_str is None
    assert data2.v_list is None

    data3 = DataClassTest(v_list=["1", "2"])
    assert data3.v_int is None
    assert data3.v_str is None
    assert data3.v_list == ["1", "2"]

    data4 = DataClassTest(v_int=1, v_str="str", v_list=["1", "2"])
    assert data4.v_int == 1
    assert data4.v_str == "str"
    assert data4.v_list == ["1", "2"]
