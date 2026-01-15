import { ref } from "vue";

import {
  init,
  onConnected,
  onDisconnected,
  launchModal,
} from "@getalby/bitcoin-connect";

export const walletConnected = ref(false);

const initialized = ref(false);
const wallet = ref(null);

onConnected((provider) => {
  wallet.value = provider;
  walletConnected.value = true;
});

onDisconnected(() => {
  wallet.value = null;
  walletConnected.value = false;
});

// This will be called automatically if it is necessary (before connecting a wallet).
function initializeLightning() {
  init({
    appName: "RSS Music Player",
    filters: ["nwc"],
    showBalance: false,
    persistConnection: true,
    providerConfig: {
      nwc: {
        authorizationUrlOptions: {
          requestMethods: ["get_balance", "pay_keysend"],
        },
      },
    },
  });

  initialized.value = true;
}

// Will prompt the user to connect their wallet. Returns true if a wallet was connected.
export async function connectWallet() {
  if (!initialized.value) {
    initializeLightning();
  }

  await launchModal();

  return wallet.value !== null;
}

// Based on fields from https://github.com/lightning/blips/blob/master/blip-0010.md
// Designed specifically for boost payments, use makeStreamMeta for stream payments in
// the future.
export function makeBoostMeta(
  podcastName,
  podcastGuid,
  trackName,
  trackGuid,
  message,
) {
  const boostMeta = {
    podcast: podcastName,
    guid: podcastGuid,
    episode: trackName,
    episode_guid: trackGuid,
    action: "boost",
    app_name: __NAME__,
    app_version: __VERSION__,
    message: message,
  };

  if (podcastGuid) {
    boostMeta.guid = podcastGuid;
  }
  if (trackGuid) {
    boostMeta.episode_guid = trackGuid;
  }

  return boostMeta;
}

// Ensure value type is keysend and recipient type is node before passing recipients
// into this function. This will not check the address for validity.
// Note that this function will give leftover sats from rounding error to the first-
// listed recipient with the largest split.
// Recipients format: [{
//   name: str, address: str, split: str(number), customRecord?: {key(str): value(str)}
// }]
export function makeValueMeta(totalSats, recipients) {
  if (recipients.length === 0) {
    throw RangeError("Must have at least one value recipient to boost");
  }

  let valueSum = 0.0;

  let mainRecipient = 0;
  let largestSplit = Number(recipients[0].split);
  for (let index = 0; index < recipients.length; index++) {
    const recipient = recipients[index];
    const value = Number(recipient.split);

    if (value <= 0) {
      throw RangeError("Recipient cannot have a value split of zero or less");
    }

    valueSum += value;

    if (value > largestSplit) {
      mainRecipient = index;
      largestSplit = value;
    }
  }

  let valueMeta = [];
  let totalSatsAfterTruncation = 0;
  for (let index = 0; index < recipients.length; index++) {
    const recipient = recipients[index];
    let normalizedSplit = Number(recipient.split) / valueSum;
    let truncatedValueRecieved = Math.floor(normalizedSplit * totalSats);

    // It's possible to have multiple entries that are identical, and they're meant to
    // be treated as independent anyways, so we store the index with the address to
    // seperate them.
    valueMeta.push({
      address: recipient.address,
      customRecord: recipient.customRecord,
      meta: {
        name: recipient.name,
        value_msat: truncatedValueRecieved * 1000,
        total_value_msat: totalSats * 1000,
      },
    });

    totalSatsAfterTruncation += truncatedValueRecieved;
  }

  // If we have leftover sats after truncation, give them to the main recipient.
  const extraSats = totalSats - totalSatsAfterTruncation;
  valueMeta[mainRecipient].meta.value_msat += extraSats * 1000;

  // If the payment is small enough, its possible some recipients will not have a large
  // enough split to recieve a sat, so, in the case of a Boost, we prioritize the main
  // recipients.
  for (let index = 0; index < valueMeta.length; index++) {
    const valueMetaEntry = valueMeta[index];
    if (valueMetaEntry.meta.value_msat === 0) {
      valueMeta.splice(index, 1);
      index--;
    }
  }

  return valueMeta;
}

// This function assumes the value described by valueMeta is correct, make sure that it
// is sourced from the makeValueMeta function so that the payment information is
// validated. Returns true if boost is sent.
export function sendBoost(boostMeta, valueMeta) {
  if (!ensureWalletConnected()) {
    return false;
  }

  for (const valueMetaEntry of valueMeta) {
    const metaString = JSON.stringify({ ...boostMeta, ...valueMetaEntry.meta });
    const sats = valueMetaEntry.meta.value_msat / 1000;

    // Sends payment to override address if set. (For testing purposes only!)
    const address = import.meta.env.VITE_LIGHTNING_RECIPIENT_OVERRIDE
      ? import.meta.env.VITE_LIGHTNING_RECIPIENT_OVERRIDE
      : valueMetaEntry.address;

    const payment = {
      destination: address,
      amount: String(sats),
      customRecords: {
        7629169: metaString,
        ...valueMetaEntry.customRecord,
      },
    };

    if (import.meta.env.VITE_BLOCK_LIGHTNING_PAYMENTS === "yes") {
      console.log(payment);
    } else {
      wallet.value.keysend(payment);
    }
  }

  return true;
}

// Prompt the user to connect their wallet only if it isn't already connected. Return
// whether a wallet has been connected by the end of the function.
async function ensureWalletConnected() {
  if (wallet.value === null) {
    await connectWallet();
  }

  return wallet.value !== null;
}
