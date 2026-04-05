from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SadalesTiklsCoordinator


@dataclass(frozen=True)
class SensorDescription:
    key: str
    name: str
    icon: str
    is_total: bool = False


SENSORS = [
    SensorDescription("total", "Yesterday Total", "mdi:lightning-bolt", True),
    *[
        SensorDescription(f"h{i:02d}", f"Hour {i:02d}", "mdi:chart-line")
        for i in range(1, 25)
    ],
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SadalesTiklsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SadalesTiklsSensor(coordinator, entry, description) for description in SENSORS)


class SadalesTiklsSensor(CoordinatorEntity[SadalesTiklsCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: SadalesTiklsCoordinator,
        entry: ConfigEntry,
        description: SensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_name = description.name
        self._attr_icon = description.icon

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Sadales tikls",
            manufacturer="Sadales tikls",
            model="M2M consumption API",
        )

    @property
    def native_value(self) -> float:
        data = self.coordinator.data or {}
        if self.entity_description.is_total:
            return float(data.get("total", 0))
        return float((data.get("hours") or {}).get(self.entity_description.key, 0))

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        if self.entity_description.is_total:
            return {
                "mp_nr": data.get("mp_nr"),
                "m_nr": data.get("m_nr"),
                "row_count": data.get("row_count"),
                "source_url": data.get("source_url"),
                "hours": data.get("hours"),
                "rows": data.get("rows"),
            }
        return None
