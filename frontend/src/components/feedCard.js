import router from "../router";

import { requestFeedFromURL } from "./rssParsing.js";

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
      requestFeedFromURL(this.feed.url);
      router.push("/view");
    },
  },
};
