import { reactive } from "vue";

export const drippingState = reactive({
	// True when the user has configured dripping to be on.
  enabled: false,

	// True when the application is running a timer to send sats. (When a track is
	// playing.)
	active: false,
});
