import { ref, computed } from "vue";

import {
  connectWallet,
  walletConnected,
  makeBoostMeta,
  makeValueMeta,
  sendBoost,
} from "../controllers/lightningPayments.js";
import { currentTrack } from "../controllers/localFeedStore.js";

export function useBoostModal() {
  const isOpen = ref(false);
  const sats = ref(0);
  const message = ref("");
  const satPrice = ref(null);
  const loadingPrice = ref(false);
  const satsError = ref("");
  const recipients = ref([]);

  const openModal = async () => {
    isOpen.value = true;
    // Will be [] if no recipients or recipients with unsupported payment methods.
    recipients.value = currentTrack.value;
    await fetchPrice();
  };

  const closeModal = () => {
    isOpen.value = false;
    sats.value = 0;
    message.value = "";
    satsError.value = "";
  };

  const onConnectWallet = async () => {
    await connectWallet();
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

  const onSendBoost = () => {
    if (!validate()) return;

    const boostMeta = makeBoostMeta(
      currentTrack.value.feedTitle,
      currentTrack.value.feedGuid,
      currentTrack.value.title,
      currentTrack.value.guid,
      message.value,
    );

    // To clarify, the first .value is to get the object from the reference, the second
    // is to get the value attribute.
    const valueMeta = makeValueMeta(
      Number(sats.value),
      currentTrack.value.value,
    );

    sendBoost(boostMeta, valueMeta);

    closeModal();
  };

  return {
    isOpen,
    sats,
    message,
    satsError,
    recipients,
    walletConnected,
    priceMessage,
    usdEquivalent,
    openModal,
    closeModal,
    onConnectWallet,
    onSendBoost,
  };
}
