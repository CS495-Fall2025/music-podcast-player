<template>
  <div>
    <button @click="openModal">Boost</button>

    <teleport to="body">
      <div class="modal" v-if="isOpen">
        <div>
          <h3>Send a Boost</h3>

          <button @click="onConnectWallet">
            {{
              walletConnected ? "Wallet connected" : "Connect Lightning Wallet"
            }}
          </button>

          <label>Amount (sats)</label>
          <input type="number" min="0" step="100" v-model="sats" />

					<SatUsd :satCount="sats"/>

          <p class="error-message" v-if="satsError">{{ satsError }}</p>

          <label>Message ({{ message.length }}/255)</label>
          <textarea
            v-model="message"
            maxlength="255"
            rows="3"
            placeholder="Say something nice! (max 255 chars)"
          ></textarea>

          <div class="button-row">
            <button @click="closeModal">Close</button>
            <button
              @click="onSendBoost"
              :disabled="!walletConnected || recipients.value.length === 0"
            >
              Send Boost!
            </button>
          </div>

          <p class="error-message" v-if="recipients.value.length === 0">
            Unable to boost this feed.
          </p>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { useBoostModal } from "../controllers/boostModal.js";
import SatUsd from "../components/SatUsd.vue";

const {
  isOpen,
  sats,
  message,
  satsError,
  recipients,
  walletConnected,
  openModal,
  closeModal,
  onConnectWallet,
  onSendBoost,
} = useBoostModal();
</script>

<style scoped>
.modal {
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.25);
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--modal-z);
}

.modal > div {
  background-color: var(--body-background);
  padding: 16px;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.button-row {
  display: flex;
  gap: 16px;
  margin: 4px;
}
</style>
