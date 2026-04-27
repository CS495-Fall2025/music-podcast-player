<script setup>
import useEditablePage from "../controllers/editablePage";
import StatusPage from "../pages/StatusPage.vue";

const props = defineProps({
  page: {
    type: String,
    required: true,
  },
});

const {
  currentUserIsAdmin,
  isEditing,
  isLoading,
  savedContent,
  editContent,
  loadError,
  saveError,
  isSaving,
  startEditing,
  saveContent,
  cancelEdit,
} = useEditablePage(props.page);
</script>

<template>
  <StatusPage
    v-if="isLoading"
    :isLoading="true"
    title="Loading..."
  />
  <div v-else class="editable-page-container">
    <div v-if="loadError" class="load-error">{{ loadError }}</div>
    <div v-if="currentUserIsAdmin" class="edit-button">
      <button v-if="!isEditing" @click="startEditing">Edit</button>
    </div>
    <div v-if="!isEditing" class="page-content">
      <div v-html="savedContent"></div>
    </div>
    <div v-else class="edit-container">
      <textarea
        v-model="editContent"
        class="editor"
        placeholder="Edit the content here..."
        rows="15"
      ></textarea>
      <div v-if="saveError" class="save-error">{{ saveError }}</div>
      <div class="edit-actions">
        <button @click="saveContent" :disabled="isSaving">
          {{ isSaving ? "Saving..." : "Save" }}
        </button>
        <button @click="cancelEdit" :disabled="isSaving">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editable-page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}

.page-content {
  align-items: center;
  display: flex;
  justify-content: center;
  background-color: var(--body-background);
  color: var(--text);
  padding: 20px;
  border-radius: 8px;
}

.edit-button {
  align-self: flex-end;
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.edit-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.editor {
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.edit-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 10px;
  resize: none;
}
</style>
