import FeedCard from "../components/FeedCard.vue";
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
