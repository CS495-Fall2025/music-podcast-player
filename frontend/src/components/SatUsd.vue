<style src="../style.css"></style>

<template>
  <span>
    {{ priceMessage }}
  </span>
</template>

<script setup>
import useSatUsd from "../controllers/satUsd";
import { watch } from "vue";

const { sats, fetchPrice, priceMessage } = useSatUsd();

const props = defineProps({
  satCount: Number,
});

watch(
  () => props.satCount,
  (newSatCount) => {
    sats.value = newSatCount;
  },
);

fetchPrice();
</script>
