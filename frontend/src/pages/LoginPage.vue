<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { completeLogin } from "../auth/authService";
import * as pkce from "../auth/pkce";
import loadConfig from "../config";

const router = useRouter();
const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");
const showVerifyPrompt = ref(false);

let codeVerifier = "";
let codeChallenge = "";

onMounted(async () => {
  // initialize PKCE flow
  try {
    const { verifier, challenge } = await pkce.generatePKCE();
    codeVerifier = verifier;
    codeChallenge = challenge;

    sessionStorage.setItem("pkce_verifier", codeVerifier);

    // notify backend of PKCE challenge
    const config = await loadConfig();
    const response = await fetch(
      `${config.backendUrl}/auth/?code_challenge=${encodeURIComponent(codeChallenge)}`,
      {
        method: "GET",
        credentials: "include",
      },
    );

    if (!response.ok) {
      throw new Error("Failed to initialize auth session");
    }

    console.log("Auth session initialized with challenge");
  } catch (err) {
    console.error("Error initializing auth:", err);
    error.value = "Failed to initialize login. Please refresh and try again.";
  }
});

const handleLogin = async (e) => {
  e.preventDefault();
  showVerifyPrompt.value = false;

  if (!username.value || !password.value) {
    error.value = "Please enter both username and password";
    return;
  }

  loading.value = true;
  error.value = "";

  try {
    // getting the stored verifier
    const storedVerifier = sessionStorage.getItem("pkce_verifier");
    if (!storedVerifier) {
      throw new Error("PKCE verifier not found. Please refresh the page.");
    }

    const config = await loadConfig();
    const response = await fetch(`${config.backendUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        code_verifier: storedVerifier,
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));

      if (response.status === 403 && data.error === "EmailNotVerified") {
        showVerifyPrompt.value = true;
        error.value =
          "Your account is not verified yet. Verify your email to continue.";
        return;
      }

      const errorMessage = data.message || "Login failed";
      throw new Error(errorMessage);
    }

    // Authentication successful - cookies are set by backend
    sessionStorage.removeItem("pkce_verifier");

    // Verify authentication and load user data
    await completeLogin();

    // Redirect to home page
    router.push("/");
  } catch (err) {
    console.error("Login error:", err);
    error.value = err.message || "Login failed. Please try again.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Login</h1>

      <form @submit="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter your username"
            :disabled="loading"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            :disabled="loading"
            required
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" :disabled="loading" class="submit-button">
          {{ loading ? "Logging in..." : "Login" }}
        </button>
      </form>

      <p class="signup-link">
        Don't have an account?
        <router-link to="/signup">Sign up here</router-link>
      </p>

      <p class="signup-link">
        Forgot your password?
        <router-link to="/forgot-password">Reset it here</router-link>
      </p>

      <p v-if="showVerifyPrompt" class="signup-link">
        Need a verification code?
        <router-link :to="{ path: '/signup', query: { step: 'verify' } }"
          >Verify your email</router-link
        >
      </p>
    </div>
  </div>
</template>

<style src="../style.css"></style>
<style src="./loginPage.css"></style>
