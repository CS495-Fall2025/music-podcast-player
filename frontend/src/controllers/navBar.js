import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import {
  startLogin,
  logout,
  isAuthenticated,
  getCurrentUser,
} from "../auth/authService";

export default function useNavbar() {
  const isOpen = ref(false);
  const dropdownOpen = ref(false);
  const dropdownRef = ref(null);

  const loggedIn = computed(() => isAuthenticated());
  const currentUser = computed(() => getCurrentUser());

  const handleClickOutside = (event) => {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
      dropdownOpen.value = false;
    }
  };

  onMounted(() => {
    document.addEventListener("click", handleClickOutside);
  });

  onBeforeUnmount(() => {
    document.removeEventListener("click", handleClickOutside);
  });

  const handleLogin = () => {
    dropdownOpen.value = false;
    startLogin();
  };


  const handleLogout = () => {
    dropdownOpen.value = false;
    logout();
    window.location.reload();
  };

  return {
    isOpen,
    dropdownOpen,
    dropdownRef,
    loggedIn,
    currentUser,
    handleLogin,
    handleLogout,
  };
}