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
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
) -> tuple[str, dict[str, str]]:
    full_url = _build_url(url, params)
    request = Request(full_url, headers=headers or {})

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
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
) -> tuple[dict[str, object] | list[object], dict[str, str]]:
    body, response_headers = request_text(
        url,
        params=params,
        headers=headers,
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
