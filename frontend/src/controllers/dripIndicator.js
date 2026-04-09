import { drippingState } from "./drippingState.js";
import hourglassIconRaw from "../assets/images/hourglass.svg?raw";

export default {
  name: "drippingIndicator",
  data() {
    return {
      hourglassIconRaw,
    };
  },
  computed: {
    drippingEnabled() {
      return drippingState.enabled;
    },
    isDripping() {
      return drippingState.active;
    },
  },
};
