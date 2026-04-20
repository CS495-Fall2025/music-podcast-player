import { computed, reactive } from "vue";

import { requestFeeds } from "./backendFeedParser.js";

import { addSearch, loadSearchHistory } from "./searchHistory.js";

loadSearchHistory();
// true for a given input's name when the value inside it is valid, false otherwise.
// We assume everything is correct until the user clicks off the input for the first
// time. We will also check validation on submitting.
const formValidation = reactive({
  query: true,
});

// true when all inputs to the form are valid, allows the user to submit the form.
export const canSubmit = computed(() => checkCanSubmit(formValidation));

export function onUserInputBlur(event) {
  if (!canSubmit.value) {
    return;
  }

  let valid = validateUserSearchQuery(event.target.value);
  formValidation.query = valid;
}

export function onUserInputInput(event) {
  if (canSubmit.value) {
    return;
  }

  let valid = validateUserSearchQuery(event.target.value);
  formValidation.query = valid;
}

export function onUserFormSubmit(event) {
  event.preventDefault();
  let data = new FormData(event.target);

  validateAll(data);

  if (canSubmit.value) {
    event.target.reset();
    addSearch(data.get("query"));
    requestFeeds(data.get("query"));
    // console.log(data.get("query"));
    //router.push("/view");
  }
}

// Limits length to 255 characters, disallows "--", and only allows letters, numbers,
// and simple punctuation.
function validateUserSearchQuery(feed) {
  return /^(?!.*--)[\w !'?.-]{1,255}$/.test(feed);
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
  formValidation.query = validateUserSearchQuery(formData.get("query"));
}
