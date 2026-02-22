import router from "../router";

import { requestLinkedFeeds } from "./backendLinkParser.js";

export default {
  name: "feedCard",

  props: {
    feed: {
      type: Object,
      required: true,
    },
  },

  methods: {
    selectTrack() {
      requestLinkedFeeds(this.feed.url);
      router.push("/view");
    },
  },
};
