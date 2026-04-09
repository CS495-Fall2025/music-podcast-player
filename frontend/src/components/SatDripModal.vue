<template>
  <div class="sat-drip-modal-overlay">
    <div class="sat-drip-modal">
      <h2 class="sat-drip-title">Sat Drip Settings</h2>
      <div class="sat-drip-wallet-row">
        <button @click="connectWallet">
          {{ walletConnected ? "Disconnect Wallet" : "Connect Wallet" }}
        </button>
      </div>

      <div class="sat-drip-field">
				<div class="sat-drip-label-row">
					<label for="sat-rate">Sats per {{ useMinutes ? "minute" : "hour" }}</label>
					<button @click=onFlipUnitClick>
						Use {{ useMinutes ? "hours" : "minutes" }}
					</button>
				</div>
        <input
          id="sat-rate"
          v-model.number="currentSatDripRate"
          class="sat-drip-input"
          type="number"
          min="0"
        />
      </div>

      <div class="sat-drip-toggle-row">
        <label for="sat-drip-enabled">Enable Sat Dripping</label>
        <label class="sat-toggle">
          <input
            id="sat-drip-enabled"
            v-model="currentSatDripEnabled"
            type="checkbox"
            :disabled="!walletConnected"
          />
          <span class="sat-toggle-slider"></span>
        </label>
      </div>

      <div class="sat-drip-actions">
        <button class="sat-drip-cancel" @click="onCancel">Cancel</button>
        <button class="sat-drip-save" @click="onSave">Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import useSatDripModal from "../controllers/satDripModal.js";
import useSatDripping from "../controllers/satDripping.js";
import {
  walletConnected,
  connectWallet,
} from "../controllers/lightningPayments.js";

useSatDripping();

const {
	currentSatDripRate,
	useMinutes,
	currentSatDripEnabled,
	onFlipUnitClick,
	saveSatDripSettings,
} = useSatDripModal();

const emit = defineEmits(["close"]);

function onSave() {
  saveSatDripSettings();
  emit("close");
}

function onCancel() {
  emit("close");
}
</script>

<style src="../style.css" />
<style scoped>
.sat-drip-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.sat-drip-modal {
  background-color: var(--nav-bg);
  color: var(--light-blue);
  border: 1px solid var(--orange);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  width: 320px;
  padding: 1.5rem;
}

.sat-drip-title {
  margin: 0 0 1rem 0;
  color: var(--light-orange);
}

.sat-drip-wallet-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  color: var(--light-blue);
}

.sat-drip-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.sat-drip-label-row {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: space-between;
}

.sat-drip-label-row button {
	padding: 2px 6px;
}

.sat-drip-label-row label,
.sat-drip-toggle-row label {
  color: var(--light-blue);
}

.sat-drip-input {
  padding: 0.65rem 0.8rem;
  background-color: var(--dark-navy);
  color: var(--white);
  border: 1px solid var(--light-blue);
  border-radius: var(--border-radius);
}

.sat-drip-input:focus {
  outline: none;
  border-color: var(--light-orange);
}

.sat-drip-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: var(--light-blue);
}

.sat-toggle {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 28px;
}

.sat-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.sat-toggle-slider {
  position: absolute;
  inset: 0;
  cursor: pointer;
  background-color: var(--dark-navy);
  border: 1px solid var(--light-blue);
  border-radius: 999px;
  transition: 0.25s ease;
}

.sat-toggle-slider::before {
  content: "";
  position: absolute;
  height: 20px;
  width: 20px;
  left: 3px;
  top: 3px;
  background-color: var(--white);
  border-radius: 50%;
  transition: 0.25s ease;
}

.sat-toggle input:checked + .sat-toggle-slider {
  background-color: var(--light-orange);
  border-color: var(--light-orange);
}

.sat-toggle input:checked + .sat-toggle-slider::before {
  transform: translateX(24px);
}

.sat-drip-actions {
  display: flex;
  justify-content: space-between;
}

.sat-drip-save {
  background-color: var(--light-orange);
  color: var(--dark-text);
  border: none;
  border-radius: var(--border-radius);
  padding: 0.6rem 1rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.sat-drip-save:hover,
.sat-drip-save:focus {
  opacity: 0.92;
  transform: scale(1.02);
}

.sat-drip-cancel {
  background-color: var(--disabled-text);
  color: var(--dark-text);
  border: none;
  border-radius: var(--border-radius);
  padding: 0.6rem 1rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.sat-drip-cancel:hover,
.sat-drip-cancel:focus {
  opacity: 0.92;
  transform: scale(1.02);
}
</style>
