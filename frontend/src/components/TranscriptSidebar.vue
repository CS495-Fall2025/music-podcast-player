<style src="../style.css"></style>

<template>
  <aside class="transcript-sidebar">
    <div class="transcript-header">
      <h3 class="transcript-title">Transcript</h3>
      <button class="media-button" @click="$emit('close')">✕</button>
    </div>

    <div v-if="loading" class="transcript-status">Loading…</div>
    <div v-else-if="error" class="transcript-error">{{ error }}</div>
    <pre v-else class="transcript-body">{{ text }}</pre>
  </aside>
</template>

<script setup>
import { toRef } from "vue";
import { useTranscriptSidebar } from "../controllers/transcriptSidebar.js";

const props = defineProps({
  track: { type: Object, default: null },
});
defineEmits(["close"]);

const trackRef = toRef(props, "track");

const { loading, error, text } = useTranscriptSidebar(trackRef);
</script>

<style scoped>
.transcript-sidebar {
  position: absolute;
  right: 0;
  bottom: calc(100% + 10px);

  width: min(420px, 92vw);
  max-height: min(60vh, 520px);

  background-color: var(--player-background);
  border: 2px solid var(--orange);
  border-radius: var(--border-radius-lg);

  padding: 12px;
  overflow: auto;

  z-index: calc(var(--player-z) + 1);
}

@media (max-width: 600px) {
  .transcript-sidebar {
    left: 0;
    right: 0;
    width: 100%;
    max-height: 55vh;
  }
}

.transcript-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 183, 128, 0.25);
}

.transcript-title {
  margin: 0;
  color: var(--light-orange);
  font-size: 1.1rem;
  font-weight: bold;
}

.media-button {
  padding: 0;
  width: clamp(2.5em, 3.5vw, 3.25em);
  height: clamp(2.5em, 2vw, 3.25em);
  font-size: clamp(1em, 2.2vw, 1.1em);
  display: flex;
  align-items: center;
  justify-content: center;
}

.transcript-status {
  margin-top: 12px;
  color: var(--light-orange);
}

.transcript-body {
  margin-top: 12px;
  color: var(--light-orange);
  white-space: pre-wrap;
  font-size: 0.95rem;
  line-height: 1.35;
}

.transcript-error {
  margin-top: 12px;
  color: var(--error-red);
}
</style>
