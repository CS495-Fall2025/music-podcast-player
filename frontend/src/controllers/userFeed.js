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
      return this.feed.image?.trim() || '/src/assets/images/default-image.jpg'
    },
    feedTitle() {
      return this.feed.title?.trim() || 'Unititled Feed'
    },
    feedArtist() {
      return this.feed.artist?.trim() || 'Feed artist not found'
    }
  }
}
