import { reactive, watch } from "vue";

export const drippingState = reactive({
  // True when the user has configured dripping to be on.
  enabled: false,

  // True when the application is running a timer to send sats. (When a track is
  // playing.)
  active: false,

  // Number of sats per minute to drip.
  dripRatePerMinute: 0.0,

  // Current track to send stream payments to, let satDripping update this.
  currentStreamMeta: null,
  currentValueRecipients: null,

  // Current fractional amount of sats to send, let satDripping update this.
  currentFractionalSatsOwed: 0.0,

  // The total number of sats spent on streaming, including ones that will be sent in
  // the next batch payment.
  totalFractionalSats: 0.0,
});

// Automatically stop dripping when dripping is disabled.
watch(
  () => drippingState.enabled,
  (newEnabled) => {
    if (!newEnabled) {
      drippingState.active = false;
      drippingState.totalFractionalSats = 0.0;
    }
  },
);
