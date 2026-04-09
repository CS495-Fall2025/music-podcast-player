<style src="../style.css"></style>
<script src="../controllers/dripIndicator.js"></script>

<template>
	<div
		class="dripping-indicators"
		v-if="drippingEnabled"
	>
		<div
			class="dripping-indicator"
			:class="{ active: isDripping }"
			v-html="hourglassIconRaw"
		/>
		<span>{{ totalSats }} Sats</span>
	</div>
</template>

<style scoped>
.dripping-indicators {
  display: inline-flex;
  align-items: center;
  justify-content: center;
	margin: 0px 8px;
}

.dripping-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: var(--disabled-text);
	margin: 0px 8px;
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
