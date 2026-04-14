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

const query = ref("");
const isFocused = ref(false);

const showHistory = ref(false);
const historyWrapper = ref(null);

function handleFocus(event) {
  isFocused.value = true;
  if (query.value.length > 0) event.target.select();
}

function handleBlur(event) {
  isFocused.value = false;
  showHistory.value = false;
  onUserInputBlur(event);
}

function clearQuery() {
  query.value = "";
  showHistory.value = false;
  onUserInputInput({ target: { value: "" } });
}

function handleHistorySelect(value) {
  query.value = value;

  const input = document.getElementById("query-input");
  if (input) {
    input.value = value;
    onUserInputInput({ target: input });

    const form = input.closest("form");
    if (form) {
      form.dispatchEvent(
        new Event("submit", { cancelable: true, bubbles: true }),
      );
    }
  } else {
    onUserInputInput({ target: { value } });
  }

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
      <span class="error-message" v-if="!canSubmit"
        >Search query has incorrect length or is using disallowed
        characters.</span
      >
      <label for="query-input" class="input-label">
       SEARCH
      </label>
      <div class="input-row" ref="historyWrapper">
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

        <button
          type="button"
          class="history-button"
          aria-label="Recent searches"
          @mousedown.prevent
          @click.stop="showHistory = !showHistory"
        >
          🕘
        </button>
        <SearchHistory v-if="showHistory" @select="handleHistorySelect" />
      </div>
    </div>
    <button class="submit-button" :disabled="!canSubmit">Search Feeds</button>
  </form>
</template>

<style scoped>
.search-feed-form {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 24px;
  justify-content: center;
}

.input-div {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex: 1;
}

.input-label {
  align-self: flex-start;
  font-size: 50px;
  flex-wrap: wrap;
  color: inherit;
}

.input-row {
  display: flex;
  align-items: center;
  width: 80%;
  max-width: 800px;
  position: relative;
}

.input-wrap {
  position: relative;
  flex: 1;
}

.input-wrap input {
  padding-right: 36px;
  box-sizing: border-box;
  color: inherit;
  border: 2px solid var(--border-color);
  border-right: 0;
  border-radius: 4px 0 0 4px;
  padding: 9.9px;
  width: 100%;
}

.input-wrap input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.history-button {
  cursor: pointer;
  line-height: 1;
  border: 2px solid var(--border-color);
  border-left: 0;
  border-radius: 0 4px 4px 0;
}

.submit-button {
  display: block;
  margin-top: 16px;
  align-self: center;
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
