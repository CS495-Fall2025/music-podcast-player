import { currentTrack, feedTracks } from "./localFeedStore.js";
import { sanitizeText } from "./textSanitizer.js";

export default {
  name: "userTrack",

  emits: ["add-to-playlist"],

  props: {
    track: {
      type: Object,
      required: true,
    },
  },

  methods: {
    // Sets the currentTrack variable to this track.
    selectTrack() {
      const selected = this.track;
      const matched = feedTracks.find((track) => {
        if (selected?.id && track?.id) return track.id === selected.id;
        if (selected?.track_url && track?.track_url) {
          return track.track_url === selected.track_url;
        }
        if (selected?.audio && track?.audio)
          return track.audio === selected.audio;
        return false;
      });

      currentTrack.value = matched || selected;
    },

    addToPlaylist(event) {
      const buttonRect = event.currentTarget.getBoundingClientRect();
    
      this.$emit("add-to-playlist", {
        track: this.track,
        anchor: {
          top: buttonRect.bottom + window.scrollY,
          left: buttonRect.left + window.scrollX,
          width: buttonRect.width,
          height: buttonRect.height,
        },
      });
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
    // Returns the track's (sanitized) description, if there's no description, returns placeholder.
    trackDescription() {
      return (
        sanitizeText(this.trackObj.description) || "Track description not found"
      );
    },
  },
};
