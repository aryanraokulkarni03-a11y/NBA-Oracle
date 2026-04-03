from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HttpRequestError(RuntimeError):
    """Raised when an upstream HTTP request fails."""


def request_text(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    json_body: dict[str, object] | list[object] | None = None,
    timeout: int = 20,
) -> tuple[str, dict[str, str]]:
    full_url = _build_url(url, params)
    payload = None
    request_headers = dict(headers or {})
    if json_body is not None:
        payload = json.dumps(json_body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    request = Request(full_url, headers=request_headers, data=payload, method=method.upper())

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            response_headers = {key.lower(): value for key, value in response.headers.items()}
    except (HTTPError, URLError) as exc:
        raise HttpRequestError(str(exc)) from exc

    return body, response_headers


def request_json(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    json_body: dict[str, object] | list[object] | None = None,
    timeout: int = 20,
) -> tuple[dict[str, object] | list[object], dict[str, str]]:
    body, response_headers = request_text(
        url,
        method=method,
        params=params,
        headers=headers,
        json_body=json_body,
        timeout=timeout,
    )
    return json.loads(body), response_headers


def _build_url(url: str, params: dict[str, object] | None) -> str:
    if not params:
        return url

    cleaned = {key: value for key, value in params.items() if value is not None}
    query = urlencode(cleaned, doseq=True)
    if "?" in url:
        return f"{url}&{query}"
    return f"{url}?{query}"
