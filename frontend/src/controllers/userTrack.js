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
    // Returns True if this is the currently playing track, false if not.
    isActive() {
      return currentTrack.value === this.track;
    },
    // Returns the track's image, if there's no image, returns placeholder.
    trackImage() {
      return this.trackObj.image || "/src/assets/images/default-image.jpg";
    },
    // Returns the track's artist, if there's no artist, returns empty.
    trackArtist() {
      if (this.trackObj.artist === "Unknown") return "";
      return this.trackObj.artist;
    },
    // Returns the track's title, if there's no title, returns empty.
    trackTitle() {
      if (this.trackObj.title === "Unknown") return "";
      return this.trackObj.title;
    },
    // Returns the track's (sanitized) description, if there's no description, returns empty.
    trackDescription() {
      if (this.trackObj.description === "Unknown") return "";
      return sanitizeText(this.trackObj.description);
    },
    trackNumber() {
      if (this.trackObj.trackNumber)
        return "Track " + this.trackObj.trackNumber;
      return "";
    },
  },
};
