import Track from "../components/UserTrack.vue";
import { feed } from "./localFeedStore.js";

export default {
  name: "UserFeed",
  components: { Track },

  computed: {
    feed() {
      return feed;
    },
    feedImage() {
      // not yet working, i think it's a parsing thing, will likely need to change some calls
      return this.feed.image?.trim() || "/src/assets/images/default-image.jpg";
    },
    feedTitle() {
      // not yet working, i think it's a parsing thing, will likely need to change some calls
      return this.feed.title?.trim() || "Untitled Feed";
    },
    feedArtist() {
      // not yet working, i think it's a parsing thing, will likely need to change some calls
      return this.feed.artist?.trim() || "Feed artist not found";
    },
  },
};
