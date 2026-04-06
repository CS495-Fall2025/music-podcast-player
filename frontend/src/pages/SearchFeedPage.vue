<script setup>
import SearchFeedForm from "../components/SearchFeedForm.vue";
import SearchedFeedsDisplay from "../components/SearchedFeedsDisplay.vue";
import LoadingComponent from "../components/LoadingComponent.vue";
import { statusState } from "../controllers/statusStore.js";
</script>

<template>
  <LoadingComponent v-if="statusState.isLoading" />
  <template v-else>
    <SearchFeedForm />
    <SearchedFeedsDisplay />
  </template>
</template>

<style scoped></style>
