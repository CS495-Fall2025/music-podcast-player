<template>
  <div>
    <button @click="openModal">
      Boost!
    </button>

    <div v-if="isOpen">
    
      <div @click="closeModal"></div>

      <div>
        <div>
          <h3>Send a Boost</h3>
          <button @click="closeModal">Close</button>
        </div>

        <div>
          <button @click="toggleWallet">
            {{ walletConnected ? "Wallet connected" : "Connect Lightning Wallet" }}
          </button>

          <div>
            <label>Amount (sats)</label>
            <input type="number" min="0" v-model="sats" />

            <div>
              <span>{{ priceMessage }}</span>
              <span v-if="usdEquivalent > 0">
                ${{ usdEquivalent.toFixed(2) }} USD
              </span>
            </div>

            <p v-if="satsError">{{ satsError }}</p>
          </div>

          <div>
            <label>Message (optional)</label>
            <textarea
              v-model="message"
              maxlength="255"
              rows="3"
              placeholder="Say something nice... (max 255 chars)"
            ></textarea>

            <div>
              <span>{{ message.length }}/255</span>
            </div>

            <p v-if="messageError">{{ messageError }}</p>
          </div>

          <div>
            You must connect your wallet before you can send a boost.
          </div>

          <div>
            <button @click="closeModal">Close</button>
            <button @click="sendBoost">Send Boost!</button>
          </div>
        </div>
      </div>
    </div>
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
const messageError = ref("");

const openModal = async () => {
  isOpen.value = true;
  await fetchPrice();
};

const closeModal = () => {
  isOpen.value = false;
  sats.value = 0;
  message.value = "";
  satsError.value = "";
  messageError.value = "";
};

const toggleWallet = () => {
  walletConnected.value = !walletConnected.value;
};

const fetchPrice = async () => {
  loadingPrice.value = true;
  try {
    const res = await fetch(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
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
  messageError.value = "";

  if (!Number.isInteger(Number(sats.value)) || sats.value <= 0) {
    satsError.value = "Enter a positive integer amount of sats.";
    valid = false;
  }
  if (message.value.length > 255) {
    messageError.value = "Message must be 255 characters or fewer.";
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
    })
  );

  closeModal();
};
</script>
