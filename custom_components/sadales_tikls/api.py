from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

import aiohttp
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


URLS = [
    "https://services.e-st.lv/m2m/services/get-object-consumption",
]


class SadalesTiklsApiError(Exception):
    pass


class SadalesTiklsApiAuthError(SadalesTiklsApiError):
    pass


def _clean(value: str) -> str:
    return value.strip().replace("\u00a0", "").replace("\u200b", "").replace("\ufeff", "")


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

        api_key = _clean(self.api_key)
        oeic = _clean(self.oeic)
        mp_nr = _clean(self.mp_nr)
        m_nr = _clean(self.m_nr)

        params = {
            "oEIC": oeic,
            "mpNr": mp_nr,
            "mNr": m_nr,
            "dF": yesterday.strftime("%Y-%m-%dT01:00:00"),
            "dT": now.strftime("%Y-%m-%dT00:00:00"),
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        auth_errors: list[str] = []
        other_errors: list[str] = []

        for url in URLS:
            try:
                async with self.session.get(url, params=params, headers=headers, timeout=60) as resp:
                    text = await resp.text()

                    if resp.status in (401, 403):
                        auth_errors.append(f"{url} -> HTTP {resp.status}: {text[:500]}")
                        continue

                    if resp.status >= 400:
                        other_errors.append(f"{url} -> HTTP {resp.status}: {text[:500]}")
                        continue

                    payload = await resp.json(content_type=None)
                    return self._normalize_payload(payload, url)

            except aiohttp.ClientError as err:
                other_errors.append(f"{url} -> {type(err).__name__}: {err}")

        if auth_errors and not other_errors:
            raise SadalesTiklsApiAuthError("; ".join(auth_errors))

        raise SadalesTiklsApiError("; ".join(auth_errors + other_errors) or "Unknown API error")

    def _normalize_payload(self, payload: Any, source_url: str) -> dict[str, Any]:
        if not isinstance(payload, list) or not payload:
            raise SadalesTiklsApiError(f"Unexpected payload from {source_url}: expected non-empty list")

        obj = payload[0]
        meters = obj.get("mList") or []
        if not meters:
            raise SadalesTiklsApiError(f"Unexpected payload from {source_url}: missing mList")

        meter = meters[0]
        rows = meter.get("cList") or []

        if not rows:
            raise SadalesTiklsApiError(
                f"No consumption rows returned by API from {source_url} "
                f"for mpNr={obj.get('mpNr')} mNr={meter.get('mNr', self.m_nr)}"
            )

        # there can be 23/25 hours in a day due to daylight saving time changes
        if len(rows) < 23:
            raise SadalesTiklsApiError(
                f"Incomplete consumption rows returned by API: got {len(rows)}, expected at least 23"
            )

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

        _LOGGER.debug("Sadales tikls API rows=%s total=%s", len(rows_out), round(total, 3))

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
