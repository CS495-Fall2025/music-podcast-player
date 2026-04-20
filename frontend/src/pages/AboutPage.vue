<script setup>
import { ref, onMounted } from "vue";
import { getPageContent, putPageContent } from "../controllers/pageContentApi";
import { useAuth } from "../auth/authStore";

const { currentUserIsAdmin } = useAuth();

const isEditing = ref(false);
const savedContent = ref("");
const editContent = ref("");
const loadError = ref("");
const saveError = ref("");
const isSaving = ref(false);

const startEditing = () => {
  editContent.value = savedContent.value;
  saveError.value = "";
  isEditing.value = true;
};

const saveContent = async () => {
  isSaving.value = true;
  saveError.value = "";
  try {
    const confirmed = await putPageContent("about", editContent.value);
    savedContent.value = confirmed;
    isEditing.value = false;
  } catch (e) {
    saveError.value = e.message ?? "Failed to save content.";
  } finally {
    isSaving.value = false;
  }
};

const cancelEdit = () => {
  isEditing.value = false;
  editContent.value = "";
  saveError.value = "";
};

onMounted(async () => {
  try {
    const html = await getPageContent("about");
    savedContent.value = html;
  } catch (e) {
    loadError.value = "Failed to load page content.";
  }
});
</script>
<template>
  <div class="about-container">
    <div v-if="loadError" class="load-error">{{ loadError }}</div>
    <div class="edit-button" v-if="currentUserIsAdmin">
      <button v-if="!isEditing" @click="startEditing">Edit</button>
    </div>
    <div v-if="!isEditing" class="about-content">
      <div v-html="savedContent"></div>
    </div>
    <div v-else class="about-edit-container">
      <textarea
        v-model="editContent"
        class="editor"
        placeholder="Edit the content here..."
        rows="15"
      ></textarea>
      <div v-if="saveError" class="save-error">{{ saveError }}</div>
      <div class="content-control-buttons">
        <button @click="saveContent" :disabled="isSaving">{{ isSaving ? 'Saving...' : 'Save' }}</button>
        <button @click="cancelEdit" :disabled="isSaving">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style src="./aboutPage.css"></style>
<style src="../style.css"></style>
