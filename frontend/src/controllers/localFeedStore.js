import { reactive, ref } from "vue";

// This feed will be populated with objects containing a type, title, image url, and
// audio url.
export const feed = reactive([]);

// Holds the current track's object (element of feed). If none is selected it will be
// null. Make sure to update the whole object rather than a field.
export const currentTrack = ref("");

// Populate with feeds found using the backend.
export const searchedFeeds = reactive([]);
