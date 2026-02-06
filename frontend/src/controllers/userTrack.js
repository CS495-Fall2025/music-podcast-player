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
    trackObj() {
      return this.track || {
        image: "",
        artist: "",
        title: "",
        description: ""
      }
    },
    trackImage() {
      return this.trackObj.image || "/src/assets/images/default-image.jpg";
    },
    trackArtist() {
      return this.trackObj.artist || "Track artist not found";
    },
    trackTitle() {
      return this.trackObj.title || "Track title not found";
    },
    trackDescription() {
      return this.trackObj.description || "Track description not found";
    },
  },
};
