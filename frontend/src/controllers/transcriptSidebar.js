import { ref, computed, watch } from "vue";

export function useTranscriptSidebar(trackRef) {
  const loading = ref(false);
  const error = ref("");
  const text = ref("");

  const transcriptUrl = computed(() => trackRef.value?.transcript || "");

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

  return { loading, error, text, loadTranscript };
}