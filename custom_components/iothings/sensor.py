import logging
import asyncio
import threading

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
    CONF_RESOURCES
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPTH_SENSOR = SensorEntityDescription(
    key="depth",
    name="Depth",
    device_class=SensorDeviceClass.PRESSURE,
    force_update=True,
    state_class=SensorStateClass.MEASUREMENT,
)

TEMPERATURE_SENSOR = SensorEntityDescription(
    key="temperature",
    name="Temperature",
    device_class=SensorDeviceClass.TEMPERATURE,
    force_update=True,
    state_class=SensorStateClass.MEASUREMENT,
)

SENSORS = (
    DEPTH_SENSOR,
    TEMPERATURE_SENSOR,
)

callback_done = threading.Event()

async def connect(sensors, device_id, db):
    try:
        print(f'about to listen to db {device_id}')
        doc_ref = db.document(f'devices/{device_id}')
        doc_watch = doc_ref.on_snapshot(
            lambda doc_snapshot, changes, read_time: on_snapshot(doc_snapshot, changes, read_time, sensors))
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Caught exception: {e}")

def on_snapshot(doc_snapshot, changes, read_time, sensors):
    for doc in doc_snapshot:
        data = doc.to_dict()
        name = data['name']
        print(f'Received document snapshot: {name}')
        for sensor in sensors:
            sensor.update_data(data)
    callback_done.set()

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    unique_id = config.get(CONF_UNIQUE_ID)
    name = config.get(CONF_NAME)
    sensors = [
        IothingsSensor(unique_id, name, sensor_desc)
        for sensor_desc in SENSORS
    ]
    db = hass.data['iothingsdb']
    add_entities(sensors)
    task = asyncio.create_task(connect(sensors, unique_id, db))

class IothingsSensor(SensorEntity):
    def __init__(self, unique_id, name, sensor_desc):
        self._native_value = 0.1
        self._state = 0
        self._deviceId = unique_id
        self._name = f"{name} {sensor_desc.name}"
        self._unique_id = f"{unique_id}_{sensor_desc.key}"
        self._sensor_desc = sensor_desc

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Io-Things",
        }

    @property
    def unit_of_measurement(self):
        if self._sensor_desc.key == "temperature":
            return "°C"
        elif self._sensor_desc.key == "depth":
            return "m"
        else:
            return None

    @property
    def unique_id(self):
        return self._unique_id
    @property
    def device_id(self):
        return self._deviceId

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update_data(self, data):
        name = data['name']
        self._name = data['name'] + ' (' + self._sensor_desc.key + ')'
        last_message = data['lastMessage']
        payload = last_message['parsedPayload']
        self._state = payload[self._sensor_desc.key]
        self.schedule_update_ha_state()


