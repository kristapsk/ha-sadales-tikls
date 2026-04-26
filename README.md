# ha-sadales-tikls

Home Assistant custom integration for **Sadales tīkls** M2M API (hourly electricity consumption).

## Features

- Yesterday total consumption
- 24 hourly sensors (01–24)
- Automatic data fetch via API
- Clean Home Assistant sensor entities

---

## Installation

### Option A: Manual

1. Copy folder:
   custom_components/sadales_tikls

   into your Home Assistant config directory:
   /config/custom_components/sadales_tikls

2. Restart Home Assistant

3. Go to:
   Settings → Devices & Services → Add Integration

4. Search for:
   Sadales tīkls

5. Enter:
   - API key
   - oEIC
   - mpNr
   - mNr

---

### Option B: HACS (custom repo)

1. Push repo to GitHub
2. HACS → Integrations → Custom repositories
3. Add:
   - Type: Integration
   - URL: your repo
4. Install integration
5. Restart HA
6. Add via UI

---

## Configuration values

### API key
Sadales tīkls M2M API key

### oEIC
Object EIC (from Sadales tīkls portal)

### mpNr
Metering point number

### mNr
Meter number

All values are automatically trimmed (copy/paste safe)

---

## API details

Auth:
Authorization: Bearer <API_KEY>

Endpoint:
https://services.e-st.lv/m2m/services/get-object-consumption

Query window:
- dF = yesterday 01:00:00
- dT = today 00:00:00

---

## Entities

Total:
sensor.sadales_tikls_yesterday_total

Hourly:
sensor.sadales_tikls_hour_01
...
sensor.sadales_tikls_hour_24

- Values in kWh
- hour_24 = last hour of day (T00:00:00 in API)

---

## Notes

- Sensors do NOT use state_class (to avoid HA warnings)
- API input values are sanitized (trim + whitespace cleanup)
- Integration uses DataUpdateCoordinator

---

## Debugging

Logs:
ha core logs | grep sadales

Typical issues:
- "APIKey format is not valid" → wrong key or formatting
- "oEIC format invalid" → incorrect value or whitespace

---

## License

MIT
