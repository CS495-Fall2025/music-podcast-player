import { reactive, ref } from "vue";

// This feed will be populated with objects containing a type, title, image url, and
// audio url.
export const feed = reactive([]);

// This will be updated with a url to fetch the audio currently being streamed. When
// this is an empty string, no audio is being streamed.
export const currentTrack = ref("");
