import { ref, watch } from "vue";
import { drippingState } from "../controllers/drippingState.js";

const useMinutes = ref(false);

export default function useSatDripModal() {
  const currentSatDripRate = ref(
		useMinutes.value
			? drippingState.dripRatePerMinute
			: drippingState.dripRatePerMinute * 60
	);
  const currentSatDripEnabled = ref(drippingState.enabled);

  const saveSatDripSettings = () => {
    // satDripEnabled.value is used here as opposed to satDripEnabled so that this only
    // updates on saving.
    drippingState.enabled = currentSatDripEnabled.value;

		if (useMinutes.value) {
			drippingState.dripRatePerMinute = currentSatDripRate.value;
		}
		else {
			drippingState.dripRatePerMinute = currentSatDripRate.value / 60.0;
		}
  };

	const onFlipUnitClick = () => {
		useMinutes.value = !useMinutes.value;
	}

	watch(useMinutes, (newUseMinutes) => {
		if (newUseMinutes) {
			currentSatDripRate.value = currentSatDripRate.value / 60;
		}
		else {
			currentSatDripRate.value = currentSatDripRate.value * 60;
		}
	});

  return {
    currentSatDripRate,
		useMinutes,
    currentSatDripEnabled,
		onFlipUnitClick,
    saveSatDripSettings,
  };
}
