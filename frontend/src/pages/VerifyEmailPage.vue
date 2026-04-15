<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import loadConfig from "../config";

const route = useRoute();
const router = useRouter();

const email = ref(route.query.email ? String(route.query.email) : "");
const code = ref("");
const loading = ref(false);
const resendLoading = ref(false);
const error = ref("");
const info = ref("");
const success = ref(false);

const isCodeValid = computed(() => /^\d{6}$/.test(code.value));

const handleVerify = async (e) => {
  e.preventDefault();
  error.value = "";
  info.value = "";

  if (!email.value || !code.value) {
    error.value = "Please enter both email and verification code.";
    return;
  }

  if (!isCodeValid.value) {
    error.value = "Verification code must be exactly 6 digits.";
    return;
  }

  loading.value = true;

  try {
    const config = await loadConfig();

    const response = await fetch(`${config.backendUrl}/auth/verify-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        email: email.value,
        code: code.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || "Invalid or expired verification code.");
    }

    success.value = true;
    info.value = "Email verified. You can now sign in.";

    setTimeout(() => {
      router.push("/login");
    }, 1500);
  } catch (err) {
    error.value = err.message || "Verification failed.";
  } finally {
    loading.value = false;
  }
};

const handleResend = async () => {
  error.value = "";
  info.value = "";

  if (!email.value) {
    error.value = "Enter your email first to resend a code.";
    return;
  }

  resendLoading.value = true;

  try {
    const config = await loadConfig();

    const response = await fetch(
      `${config.backendUrl}/auth/resend-verification`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email: email.value,
        }),
      },
    );

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || "Could not resend verification code.");
    }

    info.value =
      "If your account exists, a new verification code has been sent.";
  } catch (err) {
    error.value = err.message || "Could not resend verification code.";
  } finally {
    resendLoading.value = false;
  }
};
</script>

<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>Verify Email</h1>

      <form @submit="handleVerify">
        <div class="form-group">
          <label for="verify-email">Email</label>
          <input
            id="verify-email"
            v-model="email"
            type="email"
            placeholder="Enter your email"
            :disabled="loading || resendLoading"
            required
          />
        </div>

        <div class="form-group">
          <label for="verify-code">Verification Code</label>
          <input
            id="verify-code"
            v-model="code"
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="6-digit code"
            :disabled="loading || resendLoading"
            required
          />
          <small class="hint">Check your inbox for a 6-digit code.</small>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="info" class="success-message">
          {{ info }}
        </div>

        <div class="auth-flow-actions">
          <button
            type="submit"
            :disabled="loading || resendLoading || !isCodeValid"
            class="submit-button"
          >
            {{ loading ? "Verifying..." : "Verify Email" }}
          </button>

          <button
            type="button"
            class="submit-button secondary-button"
            :disabled="loading || resendLoading"
            @click="handleResend"
          >
            {{ resendLoading ? "Sending..." : "Resend Code" }}
          </button>
        </div>
      </form>

      <p class="login-link">
        Already verified?
        <router-link to="/login">Login here</router-link>
      </p>

      <p class="login-link">
        Need a password reset instead?
        <router-link to="/forgot-password">Reset password</router-link>
      </p>

      <p v-if="success" class="flow-link-row">Redirecting to login...</p>
    </div>
  </div>
</template>

<style src="../style.css"></style>
<style src="./signupPage.css"></style>
<style src="./authFlowPage.css"></style>
