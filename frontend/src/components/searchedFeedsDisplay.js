import FeedCard from "./FeedCard.vue";
import { searchedFeeds } from "./localFeedStore.js";

export default {
  name: "SearchedFeedsDisplay",
  components: { FeedCard },

  computed: {
    searchedFeeds() {
      return searchedFeeds;
    },
  },
};
