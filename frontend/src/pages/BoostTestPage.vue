<script setup>
import { onTestBoostSubmitted, onConnectWalletClicked } from "../components/boostTestForm.js";
import { walletConnected } from "../components/lightningPayments.js";
</script>

<template>
	<div>Test Boostagram</div>
	<button @click="onConnectWalletClicked">
		{{ walletConnected ? "Change Wallet" : "Connect Wallet" }}
	</button>
  <form @submit="onTestBoostSubmitted">
    <div class="input-div">
      <label for="recipient-address-input" class="input-label">
        Input the address of the recipient:
      </label>
      <input
        type="text"
        id="recipient-address-input"
        name="recipientAddress"
        placeholder="Public Key"
      />
      <label for="sats-input" class="input-label">
        Input the amount of sats to send:
      </label>
      <input
        type="text"
        id="sats-input"
        name="sats"
        placeholder="500"
      />
      <label for="message-input" class="input-label">
        Input the message to send to the recipient:
      </label>
      <input
        type="text"
        id="message-input"
        name="message"
        placeholder="Great work!"
      />
    </div>
    <button class="submit-button">Send Payment</button>
	</form>
</template>

<style scoped></style>
