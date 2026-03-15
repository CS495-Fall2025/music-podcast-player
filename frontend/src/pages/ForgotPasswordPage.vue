<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

import loadConfig from "../config";

const router = useRouter();

const email = ref("");
const loading = ref(false);
const error = ref("");
const info = ref("");

const handleForgotPassword = async (e) => {
  e.preventDefault();
  error.value = "";
  info.value = "";

  if (!email.value) {
    error.value = "Please enter your email.";
    return;
  }

  loading.value = true;

  try {
    const config = await loadConfig();

    const response = await fetch(`${config.backendUrl}/auth/forgot-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        email: email.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || "Could not start password reset.");
    }

    info.value =
      "If your account exists, a reset code has been sent to your email.";

    setTimeout(() => {
      router.push({
        path: "/reset-password",
        query: { email: email.value },
      });
    }, 1200);
  } catch (err) {
    error.value = err.message || "Could not start password reset.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>Forgot Password</h1>

      <form @submit="handleForgotPassword">
        <div class="form-group">
          <label for="forgot-email">Email</label>
          <input
            id="forgot-email"
            v-model="email"
            type="email"
            placeholder="Enter your account email"
            :disabled="loading"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="info" class="success-message">
          {{ info }}
        </div>

        <button type="submit" :disabled="loading" class="submit-button">
          {{ loading ? "Sending code..." : "Send Reset Code" }}
        </button>
      </form>

      <p class="login-link">
        Already have your code?
        <router-link :to="{ path: '/reset-password', query: { email } }"
          >Reset your password</router-link
        >
      </p>

      <p class="login-link">
        Remembered your password?
        <router-link to="/login">Back to login</router-link>
      </p>
    </div>
  </div>
</template>

<style src="../style.css"></style>
<style src="./signupPage.css"></style>
<style src="./authFlowPage.css"></style>
