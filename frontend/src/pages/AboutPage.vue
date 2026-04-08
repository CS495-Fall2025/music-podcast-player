<script setup>
import { ref, onMounted } from "vue";
import { sanitizeText } from "../controllers/textSanitizer";

const isEditing = ref(false);
const savedContent = ref("");
const editContent = ref("");
const isAdmin = ref(false);

const startEditing = () => {
  editContent.value = savedContent.value;
  isEditing.value = true;
};

const checkAdmin = () => {
  // const { currentUser } = useAuth();
  // Line above should check actual user role,
  // but for testing just setting to admin.
  const testUser = "admin";
  if (testUser == "admin") {
    isAdmin.value = true;
  }
  return isAdmin.value;
};

const saveContent = () => {
  savedContent.value = sanitizeText(editContent.value);
  isEditing.value = false;
};

const cancelEdit = () => {
  isEditing.value = false;
  editContent.value = "";
};

onMounted(() => {
  checkAdmin();
});

// hardcoded for now, should check backend database for html string
savedContent.value =
  "<h1>Welcome to the About Page</h1><p>This is some <strong>editable</strong> content. Click the edit button to modify it.</p>";
</script>
<template>
  <div class="about-container">
    <div class="edit-button" v-if="isAdmin">
      <button v-if="!isEditing" @click="startEditing">Edit</button>
    </div>
    <div v-if="!isEditing" class="about-content">
      <div v-html="sanitizeText(savedContent)"></div>
    </div>
    <div v-else class="about-edit-container">
      <textarea
        v-model="editContent"
        class="editor"
        placeholder="Edit the content here..."
        rows="15"
      ></textarea>
      <div class="content-control-buttons">
        <button @click="saveContent">Save</button>
        <button @click="cancelEdit">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style src="./aboutPage.css"></style>
<style src="../style.css"></style>
