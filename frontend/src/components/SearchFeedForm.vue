<style src="../style.css"></style>

<script setup>
import { ref } from "vue";
import {
  canSubmit,
  onUserInputBlur,
  onUserInputInput,
  onUserFormSubmit,
} from "../controllers/searchFeedForm.js";

import SearchHistory from "./SearchHistory.vue";
const showHistory = ref(false);

function handleHistorySelect(value) {
  const input = document.getElementById("query-input");
  input.value = value;

  onUserInputInput({ target: input });

  const form = input.closest("form");
  form.dispatchEvent(new Event("submit", { cancelable: true }));

  showHistory.value = false;
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
        @blur="onUserInputBlur"
        @input="onUserInputInput"
      />
      <button
        type="button"
        class="history-button"
        @click="showHistory = !showHistory"
      >
        🕘
      </button>
      <SearchHistory v-if="showHistory" @select="handleHistorySelect" />
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
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
}
.input-div {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-bottom: 2px;
}
.history-button {
  background: transparent;
  border: none;
  cursor: pointer;
}
</style>
