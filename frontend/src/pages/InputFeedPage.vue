<script setup>
import RSSFeedForm from "../components/RSSFeedForm.vue";
import LoadingComponent from "../components/LoadingComponent.vue";
import { statusState } from "../controllers/statusStore.js";
</script>

<template>
  <LoadingComponent v-if="statusState.isLoading" />
  <RSSFeedForm v-else />
</template>

<style scoped></style>
