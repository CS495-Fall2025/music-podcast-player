import { localFeedStore } from "./localFeedStore.js";

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
      localFeedStore.currentTrack = this.currentTrack;
    },
  },
};
