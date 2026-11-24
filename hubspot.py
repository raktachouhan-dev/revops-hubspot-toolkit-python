"""Minimal HubSpot CRM v3 client for companies: search by domain, create, update, upsert.

Safe by default: dry_run=True makes no write calls. Reads the private-app token from
the HUBSPOT_TOKEN environment variable. Not tested against a live HubSpot account.
"""
import os
import time

import requests

BASE = "https://api.hubapi.com"


class HubSpotError(RuntimeError):
    pass


class HubSpotClient:
    def __init__(self, token=None, dry_run=True, max_retries=3, session=None):
        self.token = token or os.environ.get("HUBSPOT_TOKEN", "")
        self.dry_run = dry_run
        self.max_retries = max_retries
        self.session = session or requests.Session()

    def _request(self, method, path, **kwargs):
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        for attempt in range(self.max_retries + 1):
            resp = self.session.request(method, BASE + path, headers=headers, timeout=30, **kwargs)
            if resp.status_code == 429 or resp.status_code >= 500:  # rate limit or server error: back off
                if attempt < self.max_retries:
                    time.sleep(float(resp.headers.get("Retry-After", 2 ** attempt)))
                    continue
            if resp.status_code >= 400:
                raise HubSpotError(f"{method} {path} failed: {resp.status_code} {resp.text[:200]}")
            return resp.json() if resp.content else {}
        raise HubSpotError(f"{method} {path} failed after retries")

    def find_company_by_domain(self, domain):
        body = {"filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}],
                "properties": ["name", "domain"], "limit": 1}
        results = self._request("POST", "/crm/v3/objects/companies/search", json=body).get("results", [])
        return results[0] if results else None

    def upsert_company(self, domain, properties):
        """Update the company if the domain exists, otherwise create it. Returns (action, id)."""
        props = {**properties, "domain": domain}
        existing = self.find_company_by_domain(domain)
        if self.dry_run:
            return ("would_update" if existing else "would_create", existing["id"] if existing else None)
        if existing:
            self._request("PATCH", f"/crm/v3/objects/companies/{existing['id']}", json={"properties": props})
            return ("updated", existing["id"])
        created = self._request("POST", "/crm/v3/objects/companies", json={"properties": props})
        return ("created", created["id"])
