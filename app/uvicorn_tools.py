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

from uvicorn.protocols.http.httptools_impl import HttpToolsProtocol
from uvicorn_worker import UvicornWorker


class ModuHttpToolsProtocol(HttpToolsProtocol):

    def _has_event_stream(self):
        """
        判断 header 中是否存在 accept: text/event-stream
        """
        headers_str = [
            (k.decode("utf-8").lower(), v.decode("utf-8").lower())
            for k, v in self.headers
        ]

        for key, value in headers_str:
            if key == "accept" and "text/event-stream" in value:
                return True

        return False

    def _remove_accept_encoding(self):
        """
        移除 header 中的 accept-encoding
        """
        new_headers = [
            (k, v)
            for k, v in self.headers
            if k.decode("utf-8").lower() != "accept-encoding"
        ]
        return new_headers

    def on_headers_complete(self):
        super().on_headers_complete()

        if self._has_event_stream():
            self.headers = self._remove_accept_encoding()


class ModuUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"http": ModuHttpToolsProtocol}
