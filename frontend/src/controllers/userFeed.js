import Track from "../components/UserTrack.vue";
import { feed } from "./localFeedStore.js";

export default {
  name: "UserFeed",
  components: { Track },

  computed: {
    feed() {
      return feed;
    },
  },
};
