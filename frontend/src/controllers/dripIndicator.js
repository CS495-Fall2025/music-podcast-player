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
    isDripping() {
      return drippingState.enabled;
    },
  },
};
