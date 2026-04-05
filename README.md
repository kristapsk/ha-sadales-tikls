# ha-sadales-tikls

Home Assistant custom integration for **Sadales tīkls** hourly electricity consumption API.

It creates:
- 1 sensor for yesterday total consumption
- 24 sensors for hourly consumption (`h01` ... `h24`)

## Install

### Option A: local repo / manual copy
1. Copy `custom_components/sadales_tikls` to your Home Assistant config dir:
   - `/config/custom_components/sadales_tikls`
2. Restart Home Assistant.
3. Go to **Settings -> Devices & services -> Add integration**.
4. Search for **Sadales tīkls**.
5. Enter:
   - API key
   - oEIC
   - mpNr
   - mNr

### Option B: own GitHub repo + HACS custom repository
1. Push this repo to GitHub.
2. In HACS add a custom repository:
   - Type: **Integration**
   - URL: your repo URL
3. Install **Sadales tīkls** from HACS.
4. Restart Home Assistant.
5. Add integration from UI.

## Notes
- API auth: `Authorization: Bearer <APIKEY>`
- Endpoint used:
  - primary: `https://services.e-st.lv/m2m/services/getobject-consumption`
  - fallback: `https://services.e-st.lv/m2m/services/get-objectconsumption`
  - legacy fallback: `https://services.e-st.lv/m2m/get-object-consumption`
- Query window:
  - `dF = yesterday 01:00:00`
  - `dT = today 00:00:00`
- Data source field used for active energy consumption: `cVR`

## Entities
- `sensor.<name>_yesterday_total`
- `sensor.<name>_hour_01`
- ...
- `sensor.<name>_hour_24`

`hour_24` corresponds to the API row where `cDt` ends with `T00:00:00`, i.e. the last hour of the day.
