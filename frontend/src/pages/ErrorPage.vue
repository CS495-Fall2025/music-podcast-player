<script setup>
import StatusPage from "./StatusPage.vue";
import { statusState } from "../controllers/statusStore.js";
</script>

<template>
  <StatusPage
    :isLoading="statusState.isLoading"
    :type="statusState.error?.type"
    :title="statusState.error?.title || 'Error'"
    :message="statusState.error?.message"
    :actionText="statusState.error?.actionText"
    @action="statusState.error?.onAction"
  />
</template>

<style scoped></style>
