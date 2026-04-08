<style src="../style.css"></style>
<script src="../controllers/dripIndicator.js"></script>

<template>
  <div
    class="dripping-indicator"
    :class="{ active: isDripping }"
    v-html="hourglassIconRaw"
		v-if="drippingEnabled"
  ></div>
</template>

<style scoped>
.dripping-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--disabled-text);
}

.dripping-indicator svg {
  width: 20px;
  height: 20px;
}

.dripping-indicator.active {
  color: var(--light-orange);
  animation: drip-flash 1.3s ease-in-out infinite;
}

@keyframes drip-flash {
  10%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>
