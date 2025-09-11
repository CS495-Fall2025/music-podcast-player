import { localFeedStore } from "./localFeedStore.js";

export default {
  name: "Track",

  props: {
    track: {
      type: Object,
      required: true,
    },
  },

  methods: {
    selectTrack() {
      localFeedStore.currentTrack = this.currentTrack;
    },
  },
};
