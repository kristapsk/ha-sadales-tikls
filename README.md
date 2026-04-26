[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![hassfest](https://github.com/kristapsk/ha-sadales-tikls/actions/workflows/hassfest.yml/badge.svg)](https://github.com/kristapsk/ha-sadales-tikls/actions/workflows/hassfest.yml)
[![HACS validation](https://github.com/kristapsk/ha-sadales-tikls/actions/workflows/hacs.yml/badge.svg)](https://github.com/kristapsk/ha-sadales-tikls/actions/workflows/hacs.yml)

# Home Assistant integration for Sadales Tīkls 

Home Assistant custom integration for **Sadales tikls** M2M API hourly electricity consumption data.

This integration fetches the previous day's electricity consumption from the Sadales tikls M2M API and exposes it as Home Assistant sensors.

## Features

- Yesterday's total consumption sensor
- 24 hourly consumption sensors
- Config flow setup from Home Assistant UI
- Copy/paste-safe input cleanup for API key, oEIC, mpNr and mNr
- Uses Home Assistant `DataUpdateCoordinator`
- HACS custom repository compatible

## Entities

After setup, the integration creates:

- `sensor.sadales_tikls_yesterday_total`
- `sensor.sadales_tikls_hour_01`
- `sensor.sadales_tikls_hour_02`
- ...
- `sensor.sadales_tikls_hour_24`

All values are reported in `kWh`.

`hour_24` corresponds to the API row ending with `T00:00:00`, which represents the final hour of the previous day.

## Requirements

You need Sadales tikls M2M API access and the following values:

- API key
- Object EIC (`oEIC`)
- Metering point number (`mpNr`)
- Meter number (`mNr`)

These values are available from Sadales tikls / e-st.lv object and meter information.

## Installation

### HACS custom repository

1. Open HACS.
2. Go to **Integrations**.
3. Open **Custom repositories**.
4. Add this repository URL.
5. Select category **Integration**.
6. Install **Sadales tikls**.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add integration**.
9. Search for **Sadales tikls**.
10. Enter API key, oEIC, mpNr and mNr.

### Manual installation

Copy this folder:

```text
custom_components/sadales_tikls
```

into your Home Assistant config directory:

```text
/config/custom_components/sadales_tikls
```

Then restart Home Assistant and add the integration from the UI.

## API details

The integration uses the Sadales tikls M2M API consumption endpoint:

```text
https://services.e-st.lv/m2m/services/get-object-consumption
```

Authentication:

```text
Authorization: Bearer <API_KEY>
```

The query window is:

- `dF` = yesterday `01:00:00`
- `dT` = today `00:00:00`

The integration uses the `cVR` field as the active energy consumption value.

## Troubleshooting

Useful log command:

```bash
ha core logs | grep -i sadales
```

Common API errors:

- `APIKey format is not valid` — check that the API key was copied correctly.
- `Parameter "oEIC" is not in the correct format` — check the Object EIC value and hidden whitespace.
- `Invalid authentication` — check API key access to the selected object / meter.

All input values are stripped and cleaned from common hidden copy/paste characters before being saved.

## HACS notes

This repository follows the standard HACS integration layout:

```text
custom_components/sadales_tikls/manifest.json
custom_components/sadales_tikls/*.py
hacs.json
README.md
```

For HACS default repository submission, the repository should also have:

- public GitHub repository
- repository description
- repository topics
- issues enabled
- at least one GitHub release
- passing HACS and Hassfest GitHub Actions
- Home Assistant brand assets if submitting to the default HACS repository list

## License

MIT
