<style src="../style.css"></style>

<script setup>
import { ref } from "vue";
import {
  canSubmit,
  onUserFeedInputBlur,
  onUserFeedInputInput,
  onUserFeedFormSubmit,
} from "../controllers/rssFeedForm.js";

const feedUrl = ref("");
</script>

<template>
  <form class="user-feed-form" @submit="onUserFeedFormSubmit">
    <div class="input-div">
      <label for="user-feed-input" class="input-label">
        Provide a URL for an RSS Feed:
      </label>

      <input
        type="text"
        id="user-feed-input"
        class="input-label"
        name="userFeedUrl"
        placeholder="https://example.com/feed.rss"
        v-model="feedUrl"
        @blur="onUserFeedInputBlur"
        @input="onUserFeedInputInput"
      />

      <span class="error-message" v-if="!canSubmit && feedUrl.length > 0">
        Please enter a valid URL.
      </span>
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

.input-label {
  font-size: 16px;
}
</style>
