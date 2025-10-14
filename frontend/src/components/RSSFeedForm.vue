<style src="../style.css"></style>

<script setup>
import {
  canSubmit,
  onUserFeedInputBlur,
  onUserFeedInputInput,
  onUserFeedFormSubmit,
} from "./rssFeedForm.js";
</script>

<template>
  <form class="user-feed-form" @submit="onUserFeedFormSubmit">
    <div class="input-div">
      <label for="user-feed-input" class="input-label">
        Input a URL to an RSS Feed:
      </label>
      <input
        type="text"
        id="user-feed-input"
        name="userFeedUrl"
        placeholder="https://example.com/feed.rss"
        @blur="onUserFeedInputBlur"
        @input="onUserFeedInputInput"
      />
      <span class="error-message" v-if="!canSubmit"
        >Please enter a valid URL.</span
      >
    </div>
    <button class="submit-button" :disabled="!canSubmit">Read RSS Feed</button>
  </form>
</template>

<style scoped>
.user-feed-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
}
</style>
