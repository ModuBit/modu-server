""""
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

import datetime

import simplejson as json
from asyncpg.pgproto.pgproto import UUID

default_excluded_fields = {"id", "created_at", "updated_at"}

# 注册表，存储类型与其对应的序列化和反序列化函数
serialization_registry = {}
deserialization_registry = {}


def register_type(type_, serializer, deserializer):
    serialization_registry[type_] = serializer
    deserialization_registry[type_.__name__] = deserializer


def custom_serializer(obj):
    obj_type = type(obj)
    if obj_type in serialization_registry:
        return {
            "__type__": obj_type.__name__,
            "__value__": serialization_registry[obj_type](obj),
        }
    raise TypeError(f"Object of type {obj_type} {obj} is not JSON serializable")


def custom_deserializer(dct):
    if "__type__" in dct and "__value__" in dct:
        obj_type = dct["__type__"]
        if obj_type in deserialization_registry:
            return deserialization_registry[obj_type](dct["__value__"])
    return dct


# 注册 UUID 序列化和反序列化函数
register_type(UUID, lambda obj: str(obj), lambda obj: UUID(obj))

# 注册 datetime.datetime 序列化和反序列化函数
register_type(
    datetime.datetime,
    lambda obj: obj.timestamp() * 1000,
    lambda obj: datetime.datetime.fromtimestamp(obj / 1000),
)


def dumps(
    obj,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=False,
    cls=None,
    indent=None,
    separators=None,
    encoding="utf-8",
    default=None,
    use_decimal=True,
    namedtuple_as_object=True,
    tuple_as_array=True,
    bigint_as_string=False,
    sort_keys=False,
    item_sort_key=None,
    for_json=False,
    ignore_nan=False,
    int_as_string_bitcount=None,
    iterable_as_array=False,
    **kw,
):
    return json.dumps(
        obj,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=cls,
        indent=indent,
        separators=separators,
        encoding=encoding,
        default=default or custom_serializer,
        use_decimal=use_decimal,
        namedtuple_as_object=namedtuple_as_object,
        tuple_as_array=tuple_as_array,
        bigint_as_string=bigint_as_string,
        sort_keys=sort_keys,
        item_sort_key=item_sort_key,
        for_json=for_json,
        ignore_nan=ignore_nan,
        int_as_string_bitcount=int_as_string_bitcount,
        iterable_as_array=iterable_as_array,
        **kw,
    )


def loads(
    s,
    encoding=None,
    cls=None,
    object_hook=None,
    parse_float=None,
    parse_int=None,
    parse_constant=None,
    object_pairs_hook=None,
    use_decimal=False,
    allow_nan=False,
    **kw,
):
    return json.loads(
        s,
        encoding=encoding,
        cls=cls,
        object_hook=object_hook or custom_deserializer,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        object_pairs_hook=object_pairs_hook,
        use_decimal=use_decimal,
        allow_nan=allow_nan,
        **kw,
    )
