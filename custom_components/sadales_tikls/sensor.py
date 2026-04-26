from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SadalesTiklsCoordinator


@dataclass(frozen=True, kw_only=True)
class SadalesTiklsSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[SadalesTiklsSensorDescription, ...] = (
    SadalesTiklsSensorDescription(
        key="total",
        translation_key="total",
        name="Sadales tikls yesterday total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.get("total"),
    ),
    *(
        SadalesTiklsSensorDescription(
            key=f"h{i:02d}",
            translation_key=f"h{i:02d}",
            name=f"Sadales tikls hour {i:02d}",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
                value_fn=lambda data, hour=f"h{i:02d}": data.get("hours", {}).get(hour),
        )
        for i in range(1, 25)
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SadalesTiklsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SadalesTiklsSensor(coordinator, entry, description)
        for description in SENSORS
    )


class SadalesTiklsSensor(CoordinatorEntity[SadalesTiklsCoordinator], SensorEntity):
    entity_description: SadalesTiklsSensorDescription

    def __init__(
        self,
        coordinator: SadalesTiklsCoordinator,
        entry: ConfigEntry,
        description: SadalesTiklsSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data or {})
