import { currentTrack } from "./localFeedStore.js";

export default {
  name: "userTrack",

  props: {
    track: {
      type: Object,
      required: true,
    },
  },

  methods: {
    selectTrack() {
      currentTrack = this.currentTrack;
    },
  },
};
