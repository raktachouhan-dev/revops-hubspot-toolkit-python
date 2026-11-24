from unittest.mock import MagicMock

import pytest

from toolkit.hubspot import HubSpotClient, HubSpotError


def resp(status=200, body=None, headers=None):
    r = MagicMock()
    r.status_code, r.headers, r.text = status, headers or {}, "err"
    r.content = b"x" if body is not None else b""
    r.json.return_value = body
    return r


def client(*responses, dry_run=False):
    s = MagicMock()
    s.request.side_effect = list(responses)
    return HubSpotClient(token="t", dry_run=dry_run, session=s), s


def test_creates_when_missing():
    c, s = client(resp(body={"results": []}), resp(body={"id": "9"}))
    assert c.upsert_company("a.example", {"name": "A"}) == ("created", "9")
    assert s.request.call_args_list[1].args[0] == "POST"


def test_updates_when_found():
    c, s = client(resp(body={"results": [{"id": "5"}]}), resp(body={}))
    assert c.upsert_company("a.example", {"name": "A"}) == ("updated", "5")
    assert s.request.call_args_list[1].args[0] == "PATCH"


def test_dry_run_makes_no_write_call():
    c, s = client(resp(body={"results": []}), dry_run=True)
    assert c.upsert_company("a.example", {"name": "A"}) == ("would_create", None)
    assert s.request.call_count == 1


def test_retries_on_rate_limit(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    c, s = client(resp(429, headers={"Retry-After": "0"}), resp(body={"results": []}))
    assert c.find_company_by_domain("a.example") is None
    assert s.request.call_count == 2


def test_raises_on_client_error():
    c, _ = client(resp(401, body={}))
    with pytest.raises(HubSpotError):
        c.find_company_by_domain("a.example")
