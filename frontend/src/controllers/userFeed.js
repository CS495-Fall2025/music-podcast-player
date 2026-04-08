import Track from "../components/UserTrack.vue";
import { feed, feedTracks } from "./localFeedStore.js";

export default {
  name: "UserFeed",
  components: { Track },

  methods: {
    handleAddToPlaylist(track) {
      console.log("Add to playlist clicked for track", track);
    },
  },

  computed: {
    // Returns feed if a feed is loaded. If a feed is not loaded, returns mock empty feed (until a feed is loaded) to prevent crashing.
    feed() {
      return feed.length
        ? feed[0]
        : {
            image: "",
            title: "",
            artist: "",
          };
    },
    // Returns the list of track objects within the feed. Each object holds its own data.
    feedTracks() {
      return feedTracks;
    },
    // Returns the feed's image, if there's no image, returns placeholder.
    feedImage() {
      return this.feed.image || "/src/assets/images/default-image.jpg";
    },
    // Returns the feed's title, if there's no title, returns empty.
    feedTitle() {
      if (this.feed.title === "Unknown") return "";
      return this.feed.title;
    },
    // Returns the feed's artist, if there's no artist, returns empty.
    feedArtist() {
      if (this.feed.artist === "Unknown") return "";
      return this.feed.artist;
    },
  },
};
