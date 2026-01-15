<style src="../style.css"></style>

<script setup>
import { ref } from "vue";
import {
  canSubmit,
  onUserInputBlur,
  onUserInputInput,
  onUserFormSubmit,
} from "../controllers/searchFeedForm.js";
const query = ref("");
const isFocused = ref(false);
function handleFocus(event) {
  isFocused.value = true;

  if (query.value.length > 0) {
    event.target.select();
  }
}
function handleBlur(event) {
  isFocused.value = false;
  onUserInputBlur(event);
}
function clearQuery() {
  query.value = "";
  onUserInputInput({ target: { value: "" } });
}
</script>

<template>
  <form class="search-feed-form" @submit="onUserFormSubmit">
    <div class="input-div">
      <label for="query-input" class="input-label">
        Search the PodcastIndex for feeds:
      </label>
      <input
        type="text"
        id="query-input"
        name="query"
        placeholder="Search"
        v-model="query"
        @focus="handleFocus"
        @blur="handleBlur"
        @input="onUserInputInput"
      />
      <button
        v-if="isFocused && query.length"
        type="button"
        class="clear-button"
        aria-label="Clear search"
        @mousedown.prevent="clearQuery"
      >
        ✕
      </button>
      <span class="error-message" v-if="!canSubmit"
        >Search query has incorrect length or is using disallowed
        characters.</span
      >
    </div>
    <button class="submit-button" :disabled="!canSubmit">Search Feeds</button>
  </form>
</template>

<style scoped>
.search-feed-form {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
}
.clear-button {
  position: absolute;
  margin-left: 14%;
  top: 38%;
  transform: translateY(-50%);
  background: white;
  border: none;
  font-size: 12px;
  cursor: pointer;
  color: #666;
}
.clear-button:hover {
  color: #000;
}
</style>
