import { ref, computed } from "vue";

import {
  connectWallet,
  walletConnected,
  makeBoostMeta,
  makeValueMeta,
  sendBoost,
} from "../controllers/lightningPayments.js";
import { currentTrack, feed } from "../controllers/localFeedStore.js";

export function useBoostModal() {
  const isOpen = ref(false);
  const sats = ref(0);
  const message = ref("");
  const satsError = ref("");
  const recipients = ref([]);

  const openModal = async () => {
    isOpen.value = true;
    // Will be [] if no recipients or recipients with unsupported payment methods.
    recipients.value = currentTrack.value;
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
      feed[0].title,
      feed[0].guid,
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
    openModal,
    closeModal,
    onConnectWallet,
    onSendBoost,
  };
}
