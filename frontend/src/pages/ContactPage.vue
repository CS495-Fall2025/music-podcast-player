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
    const confirmed = await putPageContent("contact", editContent.value);
    savedContent.value = confirmed;
    isEditing.value = false;
  } catch (e) {
    saveError.value = e.message ?? "Failed to save content.";
  } finally {
    isSaving.value = false;
  }
};

const cancelEditing = () => {
  isEditing.value = false;
  editContent.value = "";
  saveError.value = "";
};

onMounted(async () => {
  try {
    const html = await getPageContent("contact");
    savedContent.value = html;
  } catch {
    loadError.value = "Failed to load page content.";
  }
});
</script>

<template>
  <div class="contact-container">
    <div v-if="loadError" class="load-error">{{ loadError }}</div>
    <div class="edit-button" v-if="currentUserIsAdmin">
      <button v-if="!isEditing" @click="startEditing">Edit</button>
    </div>
    <div v-if="!isEditing" class="contact-content">
      <div v-html="savedContent"></div>
    </div>
    <div v-else class="contact-edit-container">
      <textarea
        v-model="editContent"
        class="editor"
        placeholder="Edit Here..."
        rows="15"
      ></textarea>
      <div v-if="saveError" class="save-error">{{ saveError }}</div>
      <div class="edit-actions">
        <button @click="saveContent" :disabled="isSaving">
          {{ isSaving ? "Saving..." : "Save" }}
        </button>
        <button @click="cancelEditing" :disabled="isSaving">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style src="./contactPage.css"></style>
