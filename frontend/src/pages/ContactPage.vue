<script setup>
import { sanitizeText } from "../controllers/textSanitizer";
import { ref } from "vue";

const isEditing = ref(false);
const savedContent = ref("");
const editContent = ref("");
// This should be set based on actual user role
const isAdmin = ref(false);

const startEditing = () => {
  editContent.value = savedContent.value;
  isEditing.value = true;
};

const saveContent = () => {
  savedContent.value = sanitizeText(editContent.value);
  isEditing.value = false;
};

const checkAdmin = () => {
  // const { currentUser } = useAuth();
  // Line abbove should check for actual user role
  const testUser = "admin";
  if (testUser === "admin") {
    isAdmin.value = true;
  }
  return isAdmin.value;
};

const cancelEditing = () => {
  isEditing.value = false;
};

savedContent.value =
  "<h1>This is the contact page.</h1> <p>Please reach out to us at <strong>contact@example.com</strong>.</p>";
</script>

<template>
  <div class="contact-container">
    <div class="edit-button">
      <button v-if="checkAdmin()" @click="startEditing">Edit</button>
    </div>
    <div v-if="!isEditing" class="contact-content">
      <div v-html="sanitizeText(savedContent)"></div>
    </div>
    <div v-else class="contact-edit-container">
      <textarea
        v-model="editContent"
        class="editor"
        placeholder="Edit Here..."
        rows="15"
      ></textarea>
      <div class="edit-actions">
        <button @click="saveContent">Save</button>
        <button @click="cancelEditing">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style src="./contactPage.css"></style>
