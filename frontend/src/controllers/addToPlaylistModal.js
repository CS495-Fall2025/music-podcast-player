import { ref, watch } from "vue";

export function useAddToPlaylistModal(props, emit) {
  const newTitle = ref("");
  const newDescription = ref("");
  const submitting = ref(false);

  // Reset submitting state whenever the parent signals loading is done
  watch(
    () => props.loading,
    (val) => {
      if (!val) submitting.value = false;
    },
  );

  const create = () => {
    if (submitting.value || !newTitle.value.trim()) return;
    submitting.value = true;
    emit("create-playlist", {
      title: newTitle.value.trim(),
      description: newDescription.value.trim(),
    });
  };

  const selectPlaylist = (playlist) => {
    if (submitting.value) return;
    submitting.value = true;
    emit("select-playlist", playlist);
  };

  const close = () => {
    submitting.value = false;
    emit("close");
  };

  return {
    newTitle,
    newDescription,
    submitting,
    create,
    selectPlaylist,
    close,
  };
}
