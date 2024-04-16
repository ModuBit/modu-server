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
from utils.dictionary import dict_get, FrozenDictData


def test_dict_get():
    # 测试成功获取值的情况
    dictionary = {'a': {'b': {'c': 'value'}}}
    assert dict_get(dictionary, 'a.b.c') == 'value'

    # 测试多层嵌套的情况
    dictionary = {'a': {'b': {'c': {'d': 'value'}}}}
    assert dict_get(dictionary, 'a.b.c.d') == 'value'

    # 测试键不存在的情况
    assert dict_get(dictionary, 'b.c.d') is None

    # 测试使用默认值的情况
    assert dict_get(dictionary, 'b.c.d', default='default_value') == 'default_value'

    # 测试空的键字符串的情况
    assert dict_get(dictionary, '') is None

    # 测试传入None作为keys的情况
    assert dict_get(dictionary, None) is None

    # 测试传入非字符串作为keys的情况
    assert dict_get(dictionary, 123) is None


def test_frozen_dict_data():
    dictionary = FrozenDictData({'a': {'b': {'c': 'value'}, 'd': [1, 2], 'e': [{'e1': 1, 'e2': [1, 2]}]}})

    # 测试同时支持两种取值方式
    assert dictionary.a.b.c == 'value'
    assert dictionary['a']['b']['c'] == 'value'
    assert dictionary.a.d == [1, 2]
    assert dictionary['a']['d'] == [1, 2]
    assert dictionary.a.d[1] == 2
    assert dictionary['a']['d'][1] == 2
    assert dictionary.a.e[0].e1 == 1
    assert dictionary['a']['e'][0]['e1'] == 1
    assert dictionary.a.e[0].e2 == [1, 2]
    assert dictionary['a']['e'][0]['e2'] == [1, 2]
    assert dictionary.a.e[0].e2[1] == 2
    assert dictionary['a']['e'][0]['e2'][1] == 2
    assert dictionary.d is None

    # 测试支持dict_get
    assert dict_get(dictionary, 'a.b.c') == 'value'
    assert dict_get(dictionary, 'b.c.d') is None
    assert dict_get(dictionary, 'b.c.d', default='default_value') == 'default_value'
    assert dict_get(dictionary, '') is None
    assert dict_get(dictionary, None) is None
    assert dict_get(dictionary, 123) is None
