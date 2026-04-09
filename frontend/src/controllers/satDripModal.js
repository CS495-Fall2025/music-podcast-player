import { ref } from "vue";
import { drippingState } from "../controllers/drippingState.js";

export default function useSatDripModal() {
  const currentSatDripRate = ref(drippingState.dripRate);
  const currentSatDripEnabled = ref(drippingState.enabled);

  const saveSatDripSettings = () => {
    // satDripEnabled.value is used here as opposed to satDripEnabled so that this only
    // updates on saving.
    drippingState.enabled = currentSatDripEnabled.value;
    drippingState.dripRate = currentSatDripRate.value;
  };

  return {
    currentSatDripRate,
    currentSatDripEnabled,
    saveSatDripSettings,
  };
}
