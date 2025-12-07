<template>
  <div>
    <button @click="openModal">Boost</button>

		<teleport to="body">
			<div class="modal" v-if="isOpen">
				<div>
					<h3>Send a Boost</h3>

					<button @click="toggleWallet">
						{{
							walletConnected ? "Wallet connected" : "Connect Lightning Wallet"
						}}
					</button>

					<label>Amount (sats)</label>
					<input type="number" min="0" step="100" v-model="sats" />

					<div>
						<span>{{ priceMessage }}</span>
						<span v-if="usdEquivalent > 0">
							${{ usdEquivalent.toFixed(2) }} USD
						</span>
					</div>

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
						<button @click="sendBoost" :disabled="!walletConnected">Send Boost!</button>
					</div>
				</div>
			</div>
		</teleport>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const isOpen = ref(false);
const sats = ref(0);
const message = ref("");
const walletConnected = ref(false);
const satPrice = ref(null);
const loadingPrice = ref(false);
const satsError = ref("");

const openModal = async () => {
  isOpen.value = true;
  await fetchPrice();
};

const closeModal = () => {
  isOpen.value = false;
  sats.value = 0;
  message.value = "";
  satsError.value = "";
};

const toggleWallet = () => {
  walletConnected.value = !walletConnected.value;
};

const fetchPrice = async () => {
  loadingPrice.value = true;
  try {
    const res = await fetch(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
    );
    const data = await res.json();
    satPrice.value = data.bitcoin.usd / 100000000;
  } catch (e) {
    console.error("Error fetching BTC price:", e);
  } finally {
    loadingPrice.value = false;
  }
};

const priceMessage = computed(() => {
  if (loadingPrice.value) return "Loading price...";
  if (!satPrice.value) return "Price unavailable";
  return `1 sat ≈ ${satPrice.value.toFixed(8)} USD`;
});

const usdEquivalent = computed(() => {
  return satPrice.value && sats.value > 0 ? sats.value * satPrice.value : 0;
});

const validate = () => {
  let valid = true;
  satsError.value = "";

  if (!Number.isInteger(Number(sats.value)) || sats.value <= 0) {
    satsError.value = "Enter a positive integer amount of sats.";
    valid = false;
  }

  return valid;
};

const sendBoost = () => {
  if (!validate()) return;

  console.log(
    JSON.stringify({
      amount_sats: Number(sats.value),
      message: message.value,
      timestamp: new Date().toISOString(),
    }),
  );

  closeModal();
};
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
