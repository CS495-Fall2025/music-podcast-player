<style src="../style.css"></style>

<template>
  <aside class="transcript-sidebar">
    <div class="transcript-header">
      <h3 class="transcript-title">Transcript</h3>

      
      <button class="media-button" @click="$emit('close')">✕</button>
    </div>

    <div v-if="loading" class="transcript-status">Loading…</div>

    <div v-else-if="error" class="transcript-error">
      {{ error }}
    </div>

    <pre v-else class="transcript-body">{{ text }}</pre>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
  track: {
    type: Object,
    required: false,
    default: null,
  },
});

defineEmits(["close"]);

const loading = ref(false);
const error = ref("");
const text = ref("");

const transcriptUrl = computed(() => props.track?.transcript || "");

function isSupportedTranscript(url, contentType) {
  const ct = (contentType || "").toLowerCase();
  if (ct.includes("text/vtt") || ct.includes("text/plain")) return true;

  const lower = (url || "").toLowerCase();
  return lower.endsWith(".vtt") || lower.endsWith(".txt");
}

async function loadTranscript() {
  error.value = "";
  text.value = "";

  const url = transcriptUrl.value;
  if (!url) {
    text.value = "No transcript available for this track.";
    return;
  }

  loading.value = true;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Transcript request failed (${resp.status})`);

    const contentType = resp.headers.get("content-type") || "";
    if (!isSupportedTranscript(url, contentType)) {
      throw new Error("Unsupported transcript format. Only VTT and plain text are supported.");
    }

    text.value = await resp.text();
  } catch (e) {
    error.value = e?.message || "Failed to load transcript.";
  } finally {
    loading.value = false;
  }
}

watch(transcriptUrl, () => loadTranscript(), { immediate: true });
</script>

<style scoped>

.transcript-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: min(420px, 92vw);
  height: 100vh;

  background-color: var(--player-background);
  border-left: 2px solid var(--orange);

  padding: clamp(10px, 1.5vh, 16px);
  overflow: auto;

  z-index: calc(var(--player-z) + 1);
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
  font-size: clamp(1rem, 2.4vw, 1.25rem);
  font-weight: bold;
}


.media-button {
  padding: 0;

  width: clamp(2.5em, 3.5vw, 3.25em);
  height: clamp(2.5em, 2vw, 3.25em);

  font-size: clamp(1em, 2.2vw, 1.1em);
  line-height: 1;

  display: flex;
  align-items: center;
  justify-content: center;
}

.media-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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