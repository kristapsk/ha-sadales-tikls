from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.util import dt as dt_util

PRIMARY_URL = "https://services.e-st.lv/m2m/services/getobject-consumption"
FALLBACK_URLS = [
    "https://services.e-st.lv/m2m/services/get-objectconsumption",
    "https://services.e-st.lv/m2m/get-object-consumption",
]


class SadalesTiklsApiError(Exception):
    pass


class SadalesTiklsApiAuthError(SadalesTiklsApiError):
    pass


@dataclass
class SadalesTiklsApiClient:
    api_key: str
    oeic: str
    mp_nr: str
    m_nr: str
    session: aiohttp.ClientSession

    async def async_fetch_yesterday_consumption(self) -> dict[str, Any]:
        now = dt_util.now()
        yesterday = now - timedelta(days=1)

        params = {
            "oEIC": self.oeic,
            "mpNr": self.mp_nr,
            "mNr": self.m_nr,
            "dF": yesterday.strftime("%Y-%m-%dT01:00:00"),
            "dT": now.strftime("%Y-%m-%dT00:00:00"),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        errors: list[str] = []
        for url in [PRIMARY_URL, *FALLBACK_URLS]:
            try:
                async with self.session.get(url, params=params, headers=headers, timeout=60) as resp:
                    text = await resp.text()
                    if resp.status in (401, 403):
                        raise SadalesTiklsApiAuthError("Invalid API key or access denied")
                    if resp.status >= 400:
                        errors.append(f"{url} -> HTTP {resp.status}: {text[:200]}")
                        continue
                    payload = await resp.json(content_type=None)
                    return self._normalize_payload(payload, url)
            except SadalesTiklsApiAuthError:
                raise
            except aiohttp.ClientError as err:
                errors.append(f"{url} -> {err}")

        raise SadalesTiklsApiError("; ".join(errors) if errors else "Unknown API error")

    def _normalize_payload(self, payload: Any, source_url: str) -> dict[str, Any]:
        if not isinstance(payload, list) or not payload:
            raise SadalesTiklsApiError("Unexpected payload: expected non-empty list")

        obj = payload[0]
        meters = obj.get("mList") or []
        if not meters:
            raise SadalesTiklsApiError("Unexpected payload: missing mList")

        meter = meters[0]
        rows = meter.get("cList") or []

        hours: dict[str, float] = {f"h{i:02d}": 0.0 for i in range(1, 25)}
        rows_out: list[dict[str, Any]] = []
        total = 0.0

        for row in rows:
            dt_raw = row.get("cDt", "")
            value = float(row.get("cVR", 0) or 0)
            hour_key = self._hour_key_from_cdt(dt_raw)
            if hour_key:
                hours[hour_key] = value
            total += value
            rows_out.append({"cDt": dt_raw, "cVR": value})

        return {
            "mp_nr": obj.get("mpNr"),
            "m_nr": meter.get("mNr", self.m_nr),
            "hours": hours,
            "total": round(total, 3),
            "rows": rows_out,
            "row_count": len(rows_out),
            "source_url": source_url,
        }

    @staticmethod
    def _hour_key_from_cdt(cdt: str) -> str | None:
        if "T" not in cdt:
            return None
        hour = cdt.split("T", 1)[1][0:2]
        if hour == "00":
            return "h24"
        if hour.isdigit() and 1 <= int(hour) <= 23:
            return f"h{int(hour):02d}"
        return None
