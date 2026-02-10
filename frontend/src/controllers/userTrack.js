import { currentTrack } from "./localFeedStore.js";
import { sanitizeText } from "./textSanitizer.js";

export default {
  name: "userTrack",

  props: {
    track: {
      type: Object,
      required: true,
    },
  },

  methods: {
    // Sets the currentTrack variable to this track.
    selectTrack() {
      currentTrack.value = this.track;
    },
  },

  computed: {
    // Returns a trackObj if the track exists, otherwise return placeholder values to prevent crashing.
    trackObj() {
      return (
        this.track || {
          image: "",
          artist: "",
          title: "",
          description: "",
        }
      );
    },
    // Returns the track's image, if there's no image, returns placeholder.
    trackImage() {
      return this.trackObj.image || "/src/assets/images/default-image.jpg";
    },
    // Returns the track's artist, if there's no artist, returns placeholder.
    trackArtist() {
      return this.trackObj.artist || "Track artist not found";
    },
    // Returns the track's title, if there's no title, returns placeholder.
    trackTitle() {
      return this.trackObj.title || "Track title not found";
    },
    // Returns the track's description, if there's no description, returns placeholder.
    trackDescription() {
      return (
        sanitizeText(this.trackObj.description) || "Track description not found"
      );
    },
  },
};
