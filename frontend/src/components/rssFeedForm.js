import { computed, reactive } from "vue";

import router from "../router";

import { requestFeedFromURL } from "./rssParsing.js";

// true for a given input's name when the value inside it is valid, false otherwise.
// We assume everything is correct until the user clicks off the input for the first
// time. We will also check validation on submitting.
const formValidation = reactive({
  userFeedUrl: true,
});

// true when all inputs to the form are valid, allows the user to submit the form.
export const canSubmit = computed(() => checkCanSubmit(formValidation));

export function onUserFeedInputBlur(event) {
  if (!canSubmit.value) {
    return;
  }

  let valid = validateUserRSSFeed(event.target.value);
  formValidation.userFeedUrl = valid;
}

export function onUserFeedInputInput(event) {
  if (canSubmit.value) {
    return;
  }

  let valid = validateUserRSSFeed(event.target.value);
  formValidation.userFeedUrl = valid;
}

export function onUserFeedFormSubmit(event) {
  event.preventDefault();
  let data = new FormData(event.target);

  validateAll(data);

  if (canSubmit.value) {
    event.target.reset();
    requestFeedFromURL(data.get("userFeedUrl"));
		router.push("/view");
  }
}

// Checks that the feed (string) is a URL using HTTP/HTTPS. Does not check if the URL is
// reachable or points to a valid RSS feed.
function validateUserRSSFeed(feed) {
  return /(http|https):\/\/[\w-]+\.[\w-]+(\/.*)?/.test(feed);
}

function checkCanSubmit(validationData) {
  for (let name in validationData) {
    if (!validationData[name]) {
      return false;
    }
  }

  return true;
}

// When more inputs are added to this form, this can check all of them.
function validateAll(formData) {
  formValidation.userFeedUrl = validateUserRSSFeed(formData.get("userFeedUrl"));
}
