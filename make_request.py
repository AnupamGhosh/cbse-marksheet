import asyncio
import logging
import urllib.parse

from asyncio import StreamReader, StreamWriter
from urllib.parse import SplitResult
from typing import Any, Coroutine, Dict, Tuple


class HTTPRequest:
    REQUEST_TEMPLATE = (
        "{verb} {url_path} HTTP/1.1\r\n"
        "Host: {url_hostname}\r\n"
        "Accept: */*\r\n"
        "Authority: {url_hostname}\r\n"
        "{referer}"
        "Origin: https://{url_hostname}\r\n"
        "{content_type}"
        "{content_length}"
        "\r\n"
        "{request_data}"
    ).format
    ENCODING = 'utf8'
    CONTENT_TYPE = 'content_type'
    REFERER = 'referer'

    async def open_connection(self, url: SplitResult) -> Tuple[StreamReader, StreamWriter]:
        reader, writer = await asyncio.open_connection(url.hostname, 443, ssl=True)
        return reader, writer

    def raw_request(
        self, verb: str, path: str, hostname: str, referer: str = '',
        content_type: str = '', content_len: int = 0, data: str = ''
    ) -> str:

        content_length = ''
        if referer:
            referer = f'Referer: {referer}\r\n'
        if content_type:
            content_type = f'Content-Type: {content_type}\r\n'
        if content_len > 0:
            content_length = f'Content-Length: {content_len}\r\n'
            data += "\r\n"
        return HTTPRequest.REQUEST_TEMPLATE(
            verb=verb, url_path=path, url_hostname=hostname, referer=referer,
            content_type=content_type, content_length=content_length, request_data=data)

    async def _request(self, url: SplitResult, request_txt: str)-> "HTTPResponseContextManager":
        reader, writer = await self.open_connection(url)
        logging.debug(f"Sending request\n{request_txt}")
        # print(request_txt)
        writer.write(request_txt.encode(HTTPRequest.ENCODING))
        return HTTPResponse(reader, writer)

    def get(self, url: str) -> "HTTPResponseContextManager":
        url = urllib.parse.urlsplit(url)
        http_request_txt = self.raw_request("GET", url.path, url.hostname)
        return HTTPResponseContextManager(self._request(url, http_request_txt))

    def post(self, url: str, params: Dict[str, str], headers: Dict[str, str]) -> "HTTPResponseContextManager":
        url = urllib.parse.urlsplit(url)
        content_type = headers[HTTPRequest.CONTENT_TYPE]
        request_data = self.format_req_data(params, content_type)
        content_len = len(request_data)
        referer = headers.get(HTTPRequest.REFERER)

        http_request_txt = self.raw_request(
            "POST", url.path, url.hostname, referer, content_type, content_len, request_data)
        return HTTPResponseContextManager(self._request(url, http_request_txt))

    def format_req_data(self, req_data: Dict[str, str], content_type: str) -> str:
        if content_type == 'application/x-www-form-urlencoded':
            return urllib.parse.urlencode(req_data)


class HTTPResponse:
    TIMEOUT = 1 # seconds

    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer

    async def raw_response(self) -> str:
        response = ''
        while True:
            try:
                line = await asyncio.wait_for(self.reader.readline(), timeout=HTTPResponse.TIMEOUT)
            except asyncio.TimeoutError:
                logging.debug("Returning response on timeout")
                return response
            if not line:
                break

            response += line.decode(HTTPRequest.ENCODING).rstrip() + "\n"

        return response

    def close(self) -> None:
        self.writer.close()


class HTTPResponseContextManager:
    def __init__(self, coro: Coroutine[Any, Any, HTTPResponse]) -> None:
        self.coro = coro

    async def __aenter__(self) -> HTTPResponse:
        self._resp = await self.coro
        return self._resp

    async def __aexit__(self, *_args) -> None:
        self._resp.close()


async def main():
    req = HTTPRequest()
    # get_url = "https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.htm"
    # async with req.get(get_url) as response:
    #     print(await response.raw_response())

    post_url = "https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.asp"
    params = { 'regno': 6619017, 'B1': 'Submit' }
    headers = { 
        HTTPRequest.CONTENT_TYPE: 'application/x-www-form-urlencoded', 
        HTTPRequest.REFERER: 'https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.htm'
    }
    async with req.post(post_url, params, headers) as response:
        print(await response.raw_response())


if __name__ == "__main__":
    asyncio.run(main())