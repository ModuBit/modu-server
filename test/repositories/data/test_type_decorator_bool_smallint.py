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

from repositories.data.type_decorator import Bool2SmallInt


def test_process_bind_param():
    bool_smallint = Bool2SmallInt()
    assert bool_smallint.process_bind_param(True, None) == 1
    assert bool_smallint.process_bind_param(False, None) == 0
    assert bool_smallint.process_bind_param(None, None) == 0


def test_process_result_value():
    bool_smallint = Bool2SmallInt()
    assert bool_smallint.process_result_value(1, None)
    assert not bool_smallint.process_result_value(0, None)
    assert bool_smallint.process_result_value(11, None)
    assert bool_smallint.process_result_value(b'1234', None)
    assert bool_smallint.process_result_value('1234', None)
