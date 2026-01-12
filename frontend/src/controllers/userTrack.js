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
      currentTrack.value = this.track;
    },
  },

  computed: {
    trackImage() {
      return this.track.image?.trim() || '/src/assets/images/default-image.jpg'
    },
    trackArtist() {
      return this.track.trackArtist?.trim() || 'Track artist not found'
    },
    trackTitle() {
      return this.track.title?.trim() || 'Track title not found'
    },
    trackDescription() {
      return this.track.desc?.trim() || 'Track description not found'
    }
  }
};
