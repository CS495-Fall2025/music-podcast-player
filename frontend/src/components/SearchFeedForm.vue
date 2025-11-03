<style src="../style.css"></style>

<script setup>
import {
  canSubmit,
  onUserInputBlur,
  onUserInputInput,
  onUserFormSubmit,
} from "../controllers/searchFeedForm.js";
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
</style>
