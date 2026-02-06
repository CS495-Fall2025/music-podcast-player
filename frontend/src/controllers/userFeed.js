import Track from "../components/UserTrack.vue";
import { feed, feedTracks } from "./localFeedStore.js";

export default {
  name: "UserFeed",
  components: { Track },

  computed: {
    feed() {
      return feed.length ? feed[0] : {
        image: "",
        title: "",
        artist: ""
      };
    },
    feedTracks() {
      return feedTracks;
    },
    feedImage() {
      return this.feed.image || "/src/assets/images/default-image.jpg";
    },
    feedTitle() {
      return this.feed.title || "Untitled Feed";
    },
    feedArtist() {
      return this.feed.artist || "Feed artist not found";
    },
  },
};
