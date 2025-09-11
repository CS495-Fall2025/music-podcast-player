import Track from "./Track.vue";
import { localFeedStore } from "./localFeedStore.js";

export default {
  name: "UserFeed",
  components: { Track },

  computed: {
    feed() {
      return localFeedStore.feed;
    },
  },
};
