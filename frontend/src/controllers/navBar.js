import { ref, onMounted, onBeforeUnmount } from "vue";

export default function useNavbar() {
  const isOpen = ref(false);
  const dropdownOpen = ref(false);
  const dropdownRef = ref(null);

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
    alert("Login clicked");
    dropdownOpen.value = false;
  };

  const handleLogout = () => {
    alert("Logout clicked");
    dropdownOpen.value = false;
  };

  return {
    isOpen,
    dropdownOpen,
    dropdownRef,
    handleLogin,
    handleLogout,
  };
}
