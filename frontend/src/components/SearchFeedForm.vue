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

			<div class="input-wrap">
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

        <span
          v-if="isFocused && query.length"
          role="button"
          class="clear-button"
          aria-label="Clear search"
          @mousedown.prevent="clearQuery"
        >
          ✕
        </span>
      </div>

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
.input-wrap {
  position: relative;
}
.input-wrap input {
  padding-right: 36px;
  box-sizing: border-box;
}
.clear-button {
  position: absolute;
  right: 12px;
  top: 55%;
  transform: translateY(-50%);
  background: transparent;
  font-size: 12px;
  cursor: pointer;
  line-height: 1;
}
</style>
