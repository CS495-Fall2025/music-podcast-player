import { ref, onMounted } from "vue";
import { getPageContent, putPageContent } from "./pageContentApi";
import { useAuth } from "../auth/authStore";

export default function useEditablePage(page) {
  const { currentUserIsAdmin } = useAuth();

  const isEditing = ref(false);
  const isLoading = ref(false);
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
      const confirmed = await putPageContent(page, editContent.value);
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
    isLoading.value = true;
    try {
      const html = await getPageContent(page);
      savedContent.value = html;
    } catch {
      loadError.value = "Failed to load page content.";
    } finally {
      isLoading.value = false;
    }
  });

  return {
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
  };
}
