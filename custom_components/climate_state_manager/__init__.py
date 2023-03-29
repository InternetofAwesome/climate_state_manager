import logging
import json
from typing import List
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant import config_entries
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .config_flow import ClimateStateManagerConfigFlow
from homeassistant.config_entries import ConfigFlow


DOMAIN = "climate_state_manager"
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

CONF_ENTITY_IDS = "entity_ids"

@config_entries.HANDLERS.register(DOMAIN)
class ClimateStateManagerConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id='user',
                data_schema=vol.Schema({
                    vol.Required(CONF_ENTITY_IDS): cv.multi_select(await async_get_options(self.hass)),
                }),
            )

        return self.async_create_entry(
            title="Climate State Manager Configuration",
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options(hass):
        entities = [
            entity.entity_id for entity in hass.states.async_all()
            if entity.domain == 'climate'
        ]

        return entities

async def async_get_options(hass) -> List:
    entities = [
        entity.entity_id for entity in hass.states.async_all()
        if entity.domain == 'climate'
    ]

    return entities

async def async_save_restore_climate_state(service: ServiceCall):
    hass = service.hass
    operation = service.data.get("operation")
    entity_ids = service.data.get("target")

    # Check if operation is 'save' or 'restore'
    if operation not in ('save', 'restore'):
        return {"result": "error", "message": f"Invalid operation: {operation}. Allowed operations are 'save' or 'restore'."}

    if not entity_ids or not operation:
        return {"result": "error", "message": "entity_id and operation are required"}

    storage_key = "input_text.climate_states"
    storage_state = hass.states.get(storage_key)
    stored_data = json.loads(storage_state.state) if storage_state and storage_state.state else {}

    results = []

    for entity_id in entity_ids:
        climate_state = hass.states.get(entity_id)

        if climate_state is None:
            results.append({"result": "error", "entity_id": entity_id, "message": f"Climate entity {entity_id} not found"})
            continue

        current_temp = climate_state.attributes.get("temperature")
        current_mode = climate_state.state

        if operation == "save":
            stored_data[entity_id] = {"mode": current_mode, "temperature": current_temp}
            results.append({"result": "success", "entity_id": entity_id, "message": f"Saved state for {entity_id}: Mode - {current_mode}, Temperature - {current_temp}"})
        elif operation == "restore":
            saved_state = stored_data.get(entity_id)

            if not saved_state:
                results.append({"result": "error", "entity_id": entity_id, "message": f"No saved state found"})
            else:
                saved_mode = saved_state["mode"]
                saved_temp = saved_state["temperature"]
                await hass.services.async_call("climate", "set_temperature", {"entity_id": entity_id, "temperature": float(saved_temp)})
                await hass.services.async_call("climate", "set_hvac_mode", {"entity_id": entity_id, "hvac_mode": saved_mode})

    return results

async def async_setup(hass: HomeAssistant, config: dict):
    _LOGGER.debug("Starting Climate State Manager setup")
    _LOGGER.info("Setting up Climate State Manager")

    # component = EntityComponent(_LOGGER, DOMAIN, hass)
    _LOGGER.debug("Climate State Manager setup complete")
    # hass.config_entries.async_register_flow(DOMAIN, ClimateStateManagerConfigFlow)
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: config_entries.ConfigEntry):
    hass.data[DOMAIN] = config_entry.data[CONF_ENTITY_IDS]
    hass.services.async_register(
        DOMAIN,
        "save_restore_climate_state",
        async_save_restore_climate_state,
        schema=vol.Schema(
            {
                vol.Required("operation"): vol.In(["save", "restore"]),
                vol.Required("target"): cv.SERVICE_ENTITY_SCHEMA,
            }
        ),
    )

    
    return True