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

import contextvars

from fastapi import FastAPI
from loguru import logger
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_ot_trace_id = contextvars.ContextVar('ot_trace_id', default='0')
_ot_span_id = contextvars.ContextVar('ot_span_id', default='0')
_ot_service_name = contextvars.ContextVar('ot_service_name', default='unknown_service')


def ot_config(fast_app: FastAPI):
    """
    OpenTelemetry 配置
    :param fast_app: FastAPI
    """

    # 初始化TracerProvider
    trace.set_tracer_provider(TracerProvider())

    # 创建一个控制台导出器并配置它以在TracerProvider上
    tracer_provider = trace.get_tracer_provider()
    span_processor = BatchSpanProcessor(InMemorySpanExporter())
    tracer_provider.add_span_processor(span_processor)

    # 使用OpenTelemetry中间件来自动跟踪请求
    FastAPIInstrumentor.instrument_app(fast_app)


def ot_instrument_loguru():
    """
    将OpenTelemetry trace配置到loguru
    """

    provider = trace.get_tracer_provider()
    service_name = None

    def add_trace_context(record):
        record["extra"]["ot_span_id"] = "0"
        record["extra"]["ot_trace_id"] = "0"

        nonlocal service_name
        if service_name is None:
            resource = getattr(provider, "resource", None)
            if resource:
                service_name = resource.attributes.get("service.name") or ""
            else:
                service_name = ""

        _ot_service_name.set(service_name)

        span = trace.get_current_span()
        if span != trace.INVALID_SPAN:
            ctx = span.get_span_context()
            if ctx != trace.INVALID_SPAN_CONTEXT:
                _ot_trace_id.set(f"{ctx.trace_id:032x}")
                _ot_span_id.set(f"{ctx.span_id:016x}")

        record["extra"]["ot_trace_id"] = _ot_trace_id.get()
        record["extra"]["ot_span_id"] = _ot_span_id.get()
        record["extra"]["ot_service_name"] = _ot_service_name.get()

    logger.configure(patcher=add_trace_context)
