import { reactive, watch } from "vue";

export const drippingState = reactive({
	// True when the user has configured dripping to be on.
  enabled: false,

	// True when the application is running a timer to send sats. (When a track is
	// playing.)
	active: false,
});

// Automatically stop dripping when dripping is disabled.
watch(
	() => drippingState.enabled,
	(newEnabled) => {
		if (!newEnabled) {
			drippingState.active = false;
		}
	}
);
