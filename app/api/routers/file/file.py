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

from urllib.parse import unquote_plus
from fastapi.responses import StreamingResponse, Response
from fastapi import APIRouter, Depends, Header, UploadFile, Request
from repositories.data.file.file_models import SimpleFile
from repositories.data.account.account_models import Account
from services import file_service
from api.dependencies.principal import current_account

router = APIRouter()


@router.post("/upload")
async def file_upload(
    file: UploadFile, current_user: Account = Depends(current_account)
):
    """
    文件上传
    :param file: 文件
    """
    file_info = await file_service.file_upload(current_user, file)
    return SimpleFile(
        file_key=file_info.file_key,
        filename=file_info.filename,
        file_url=file_info.file_url,
    )


@router.get("/{file_key:path}/preview")
async def file_preview(
    file_key: str,
    expires: int,
    signature: str,
    if_none_match: str = Header(default=""),
) -> StreamingResponse:
    """
    文件预览
    :param file_key: 文件KEY
    :param expires: 过期时间
    :param signature: 签名
    :param if_none_match: 如果匹配，返回 304 Not Modified
    """
    return await _get_file_stream_response(file_key, expires, signature, "inline", if_none_match)


@router.get("/{file_key:path}")
async def file(
    file_key: str,
    expires: int,
    signature: str,
    content_disposition: str = Header(default="attachment"),
    if_none_match: str = Header(default=""),
) -> StreamingResponse:
    """
    文件
    :param file_key: 文件KEY
    :param expires: 过期时间
    :param signature: 签名
    :param content_disposition: 内容分发
    :param if_none_match: 如果匹配，返回 304 Not Modified
    """
    return await _get_file_stream_response(
        file_key, expires, signature, content_disposition, if_none_match
    )


async def _get_file_stream_response(
    file_key: str,
    expires: int,
    signature: str,
    content_disposition: str = "attachment",
    if_none_match: str = Header(default=""),
) -> StreamingResponse:
    """
    文件
    :param file_key: 文件KEY
    :param expires: 过期时间
    :param signature: 签名
    :param content_disposition: 内容分发
    :param if_none_match: 如果匹配，返回 304 Not Modified
    """

    etag = unquote_plus(file_key)
    
    # 如果客户端的 ETag 匹配，返回 304 Not Modified
    if if_none_match and if_none_match == etag:
        return Response(status_code=304, headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=604800, stale-while-revalidate=86400",  # 7天缓存，1天宽限期
        })

    file_stream, file = await file_service.file_content(file_key, expires, signature)

    headers = {
        "Content-Disposition": f"{content_disposition}; filename={file.filename}",
        "Cache-Control": "public, max-age=604800, stale-while-revalidate=86400",  # 7天缓存，1天宽限期
        "ETag": etag,  # 使用文件唯一标识作为 ETag
    }

    return StreamingResponse(
        file_stream, media_type=file.file_mime_type, headers=headers
    )
