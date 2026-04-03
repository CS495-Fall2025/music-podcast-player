<script setup>
import RSSFeedForm from "../components/RSSFeedForm.vue";
import StatusPage from "./StatusPage.vue";
import { statusState } from "../controllers/statusStore.js";
</script>

<template>
  <StatusPage
    v-if="statusState.isLoading || statusState.error"
    :isLoading="statusState.isLoading"
    :type="statusState.error?.type"
    :title="statusState.error?.title || 'Loading...'"
    :message="statusState.error?.message"
    :actionText="statusState.error?.actionText"
    @action="statusState.error?.onAction"
  />
  <template v-else>
    <RSSFeedForm />
  </template>
</template>

<style scoped></style>
