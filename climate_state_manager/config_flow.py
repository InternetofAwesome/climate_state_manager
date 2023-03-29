import logging
from homeassistant import config_entries

DOMAIN = "climate_state_manager"

_LOGGER = logging.getLogger(__name__)

class ClimateStateManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Climate State Manager", data=user_input)

        return self.async_show_form(step_id="user")
