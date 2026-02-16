<style src="../style.css"></style>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import {
  canSubmit,
  onUserInputBlur,
  onUserInputInput,
  onUserFormSubmit,
} from "../controllers/searchFeedForm.js";

import SearchHistory from "./SearchHistory.vue";
const showHistory = ref(false);
const historyWrapper = ref(null);

function handleHistorySelect(value) {
  const input = document.getElementById("query-input");
  input.value = value;

  onUserInputInput({ target: input });

  const form = input.closest("form");
  form.dispatchEvent(new Event("submit", { cancelable: true }));

  showHistory.value = false;
}
function handleClickOutside(event) {
  if (!showHistory.value) return;
  if (historyWrapper.value && !historyWrapper.value.contains(event.target)) {
    showHistory.value = false;
  }
}
onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<template>
  <form class="search-feed-form" @submit="onUserFormSubmit">
    <div class="input-div">
      <label for="query-input" class="input-label">
        Search the PodcastIndex for feeds:
      </label>
      <div class="input-row">
      <input
        type="text"
        id="query-input"
        name="query"
        placeholder="Search"
        @blur="onUserInputBlur"
        @input="onUserInputInput"
      />
      <div class="history-wrapper" ref="historyWrapper">
      <button
        type="button"
        class="history-button"
        aria-label="Recent searches"
        @click.stop="showHistory = !showHistory"
      >
        🕘
      </button>
      <SearchHistory v-if="showHistory" @select="handleHistorySelect" />
      </div>
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
.input-div {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-bottom: 2px;
}
.input-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.history-button {
  background: transparent;
  border: none;
  cursor: pointer;
}
.history-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
</style>
