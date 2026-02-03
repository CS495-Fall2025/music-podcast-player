import { ref, onMounted, onBeforeUnmount } from "vue";
import { startLogin, logout, useAuth } from "../auth/authService";

export default function useNavbar() {
  const isOpen = ref(false);
  const dropdownOpen = ref(false);
  const dropdownRef = ref(null);

  // Use the reactive auth store
  const { isAuthenticated, currentUser } = useAuth();

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

  const handleSignup = () => {
    dropdownOpen.value = false;
    window.location.href = "/signup";
  };

  const handleLogout = async () => {
    dropdownOpen.value = false;
    await logout();
    window.location.reload();
  };

  return {
    isOpen,
    dropdownOpen,
    dropdownRef,
    isAuthenticated,
    currentUser,
    handleLogin,
    handleSignup,
    handleLogout,
  };
}
