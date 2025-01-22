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

import pytest
from repositories.storage.local_fs_storage import LocalFsStorage


@pytest.mark.asyncio
async def test_local_fs_storage():
    storage = LocalFsStorage(root_path=".data")
    assert storage is not None

    file_key = await storage.put_file("test.txt", "test content")
    assert file_key is not None
    
    file_bytes = await storage.get_file_bytes(file_key)
    assert file_bytes is not None
    assert file_bytes == b"test content"

    stream = storage.get_stream(file_key)
    assert stream is not None
    content = b""
    async for chunk in stream:
        content += chunk
    assert content == b"test content"

    assert await storage.exists_file(file_key)
    assert await storage.delete_file(file_key)
    assert not await storage.exists_file(file_key)

    url = await storage.sign_url(file_key, 3600)
    assert url is not None
    assert url.startswith(f"/api/file/{file_key}")
