class ClimateStateManagerCard extends HTMLElement {
    set hass(hass) {
      if (!this.content) {
        const card = document.createElement('ha-card');
        card.header = 'Climate State Manager';
        this.content = document.createElement('div');
        this.content.style.padding = '0 16px 16px';
        card.appendChild(this.content);
        this.appendChild(card);
        this.createUI();
      }
    }
  
    async createUI() {
      const entities = await this.getClimateEntities();
      this.content.innerHTML = `
        <div>
          <label for="entities">Entities:</label>
          <div id="entity-list">
            ${entities.map(e => `
              <div>
                <input type="checkbox" id="${e}" name="${e}" value="${e}">
                <label for="${e}">${e}</label>
              </div>
            `).join('')}
          </div>
        </div>
        <div>
          <label for="operation">Operation:</label>
          <select id="operation">
            <option value="save">Save</option>
            <option value="restore">Restore</option>
          </select>
        </div>
        <button id="execute">Execute</button>
      `;
      this.content.querySelector('#execute').addEventListener('click', this.executeAction.bind(this));
    }
  
    async getClimateEntities() {
      const entities = await this.callWS({ type: "climate_state_manager/get_options" });
      return entities;
    }
  
    async executeAction() {
      const entityCheckboxes = this.content.querySelectorAll('#entity-list input[type="checkbox"]:checked');
      const entityIds = Array.from(entityCheckboxes).map(cb => cb.value);
      const operationSelect = this.content.querySelector('#operation');
      const operation = operationSelect.value;
      await this.callService('climate_state_manager', 'save_restore_climate_state', { entity_id: entityIds, operation });
    }
  
    async callService(domain, service, serviceData) {
      return await this.callWS({
        type: 'call_service',
        domain,
        service,
        service_data: serviceData,
      });
    }
  
    async callWS(msg) {
      return await this.hass.connection.sendMessagePromise(msg);
    }
  
    setConfig(config) {
      // You can use the config to customize the card if needed
    }
  
    getCardSize() {
      return 3;
    }
  }
  
  customElements.define('climate-state-manager-card', ClimateStateManagerCard);
  