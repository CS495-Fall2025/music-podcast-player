import { currentTrack as currentTrackRef } from "./localFeedStore.js";

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
      currentTrackRef.value = this.track.audio;
    },
  },
};
