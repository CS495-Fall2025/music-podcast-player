<style src="./StatusPage.css"></style>

<script setup>
import { computed } from "vue";
import emptyFeedIcon from "../assets/images/empty-feed-error.svg";
import offlineIcon from "../assets/images/no-connection.svg";
import errorIcon from "../assets/images/error.svg";
import externalErrorIcon from "../assets/images/external-error.svg";
import feedErrorIcon from "../assets/images/feed-error.svg";

const props = defineProps({
  isLoading: { type: Boolean, default: false },
  useSkeleton: { type: Boolean, default: false },
  type: { type: String, default: "error" },
  title: { type: String, required: true },
  message: { type: String, default: "" },
  actionText: { type: String, default: "" },
});

defineEmits(["action"]);

// Map error types to their icon imports
const iconMap = {
  "offline": offlineIcon,
  "empty-feed-error": emptyFeedIcon,
  "external-error": externalErrorIcon,
  "feed-error": feedErrorIcon,
  "error": errorIcon,
};

const currentIcon = computed(() => iconMap[props.type] || errorIcon);
</script>

<template>
  <div class="status-wrapper">
    <div v-if="isLoading" class="status-content">
      <div v-if="useSkeleton" class="skeleton-container">
        <div class="skeleton-box" v-for="n in 3" :key="n"></div>
      </div>
      <div v-else class="spinner"></div>
      <h2 class="status-title">{{ title || "Loading..." }}</h2>
      <p class="status-message" v-if="message">{{ message }}</p>
    </div>

    <div v-else class="status-content">
      <div class="status-icon">
        <img v-if="currentIcon" :src="currentIcon" :alt="props.type" />
      </div>

      <h2 class="status-title">{{ title }}</h2>
      <p class="status-message">{{ message }}</p>

      <button v-if="actionText" @click="$emit('action')" class="action-button">
        {{ actionText }}
      </button>
    </div>
  </div>
</template>
