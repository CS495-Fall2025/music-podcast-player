<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import loadConfig from "../config";

const route = useRoute();
const router = useRouter();
const pendingResetEmailKey = "pending_reset_email";
const pendingResetCodeKey = "pending_reset_code";

const resetEmail = ref("");
const resetCode = ref("");
const codeInput = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");
const success = ref(false);

const isCodeStep = computed(() => route.query.step !== "new-password");
const isNewPasswordStep = computed(() => route.query.step === "new-password");

onMounted(() => {
  resetEmail.value = sessionStorage.getItem(pendingResetEmailKey) || "";
  resetCode.value = sessionStorage.getItem(pendingResetCodeKey) || "";
});

const isCodeValid = computed(() => /^\d{6}$/.test(codeInput.value));

const passwordRequirements = {
  length: (password) => password.length >= 12,
  hasLetter: (password) => /[a-zA-Z]/.test(password),
  hasDigit: (password) => /\d/.test(password),
  hasSpecial: (password) =>
    /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password),
};

const isPasswordValid = computed(() => {
  return Object.values(passwordRequirements).every((check) =>
    check(newPassword.value),
  );
});

const handleCodeSubmit = async (e) => {
  e.preventDefault();
  error.value = "";

  if (!resetEmail.value) {
    error.value = "No pending reset found. Start from forgot password.";
    return;
  }

  if (!isCodeValid.value) {
    error.value = "Reset code must be exactly 6 digits.";
    return;
  }

  resetCode.value = codeInput.value;
  sessionStorage.setItem(pendingResetCodeKey, codeInput.value);

  router.push({
    path: "/reset-password",
    query: { step: "new-password" },
  });
};

const handleResetPassword = async (e) => {
  e.preventDefault();
  error.value = "";

  if (!resetEmail.value || !resetCode.value) {
    error.value = "Reset session expired. Please request a new code.";
    return;
  }

  if (!newPassword.value || !confirmPassword.value) {
    error.value = "Please complete all fields.";
    return;
  }

  if (!isPasswordValid.value) {
    error.value =
      "Password must be at least 12 characters and include a letter, digit, and special character.";
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    error.value = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    const config = await loadConfig();

    const response = await fetch(`${config.backendUrl}/auth/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        email: resetEmail.value,
        code: resetCode.value,
        new_password: newPassword.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || "Could not reset password.");
    }

    success.value = true;
    sessionStorage.removeItem(pendingResetEmailKey);
    sessionStorage.removeItem(pendingResetCodeKey);

    setTimeout(() => {
      router.push("/login");
    }, 1500);
  } catch (err) {
    error.value = err.message || "Could not reset password.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>{{ isCodeStep ? "Enter Reset Code" : "Reset Password" }}</h1>

      <form v-if="isCodeStep" @submit="handleCodeSubmit">
        <div class="form-group">
          <label for="reset-code">Reset Code</label>
          <input
            id="reset-code"
            v-model="codeInput"
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="Enter your 6-digit reset code"
            :disabled="loading"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading || !isCodeValid"
          class="submit-button"
        >
          Continue
        </button>
      </form>

      <form v-else-if="isNewPasswordStep" @submit="handleResetPassword">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-group">
          <label for="new-password">New Password</label>
          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            placeholder="Enter your new password"
            :disabled="loading"
            required
          />
          <div class="password-requirements">
            <div :class="{ met: passwordRequirements.length(newPassword) }">
              ✓ At least 12 characters
            </div>
            <div :class="{ met: passwordRequirements.hasLetter(newPassword) }">
              ✓ Contains a letter
            </div>
            <div :class="{ met: passwordRequirements.hasDigit(newPassword) }">
              ✓ Contains a digit
            </div>
            <div :class="{ met: passwordRequirements.hasSpecial(newPassword) }">
              ✓ Contains a special character (!@#$%^&* etc.)
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="confirm-new-password">Confirm New Password</label>
          <input
            id="confirm-new-password"
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your new password"
            :disabled="loading"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="success" class="success-message">
          Password reset successful. Redirecting to login...
        </div>

        <button
          type="submit"
          :disabled="loading || !isPasswordValid"
          class="submit-button"
        >
          {{ loading ? "Resetting password..." : "Reset Password" }}
        </button>
      </form>

      <p v-if="isCodeStep" class="login-link">
        Didn't get a code?
        <router-link to="/forgot-password">Send a new reset code</router-link>
      </p>

      <p v-if="isNewPasswordStep" class="login-link">
        Need to re-enter your code?
        <router-link :to="{ path: '/reset-password', query: { step: 'code' } }"
          >Back to code entry</router-link
        >
      </p>

      <p class="login-link">
        Back to sign in?
        <router-link to="/login">Login</router-link>
      </p>
    </div>
  </div>
</template>

<style src="../style.css"></style>
<style src="./signupPage.css"></style>
<style src="./authFlowPage.css"></style>
