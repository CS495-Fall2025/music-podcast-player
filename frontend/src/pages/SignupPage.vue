<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import loadConfig from "../config";

const router = useRouter();
const route = useRoute();
const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const verificationCode = ref("");
const loading = ref(false);
const error = ref("");
const success = ref(false);
const info = ref("");

const verificationEmail = ref("");

const pendingVerificationEmailKey = "pending_verification_email";

const isVerificationStep = computed(() => route.query.step === "verify");

const isVerificationCodeValid = computed(() =>
  /^\d{6}$/.test(verificationCode.value),
);

onMounted(() => {
  const queryEmail = route.query.email ? String(route.query.email) : "";
  if (queryEmail) {
    verificationEmail.value = queryEmail;
    sessionStorage.setItem(pendingVerificationEmailKey, queryEmail);
    return;
  }

  verificationEmail.value =
    sessionStorage.getItem(pendingVerificationEmailKey) || "";
});

const passwordRequirements = {
  length: (password) => password.length >= 12,
  hasLetter: (password) => /[a-zA-Z]/.test(password),
  hasDigit: (password) => /\d/.test(password),
  hasSpecial: (password) =>
    /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password),
};

const isPasswordValid = () => {
  const pass = password.value;
  return Object.values(passwordRequirements).every((check) => check(pass));
};

const handleSignup = async (e) => {
  e.preventDefault();
  error.value = "";
  success.value = false;
  info.value = "";

  // client-side validation
  if (
    !username.value ||
    !email.value ||
    !password.value ||
    !confirmPassword.value
  ) {
    error.value = "Please fill in all fields";
    return;
  }

  if (username.value.length < 6) {
    error.value = "Username must be at least 6 characters";
    return;
  }

  if (!/^[a-zA-Z0-9]\w*[a-zA-Z0-9]$/.test(username.value)) {
    error.value = "Username must start and end with alphanumeric characters";
    return;
  }

  if (!isPasswordValid()) {
    error.value =
      "Password must be at least 12 characters and include a letter, digit, and special character";
    return;
  }

  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }

  loading.value = true;

  try {
    const config = await loadConfig();

    const response = await fetch(`${config.backendUrl}/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Include cookies in request
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json();

      // Set error message based on error type
      if (data.error === "ValueNotUnique") {
        if (data.field === "username") {
          error.value = "Username already taken";
        } else if (data.field === "email") {
          error.value = "Email already registered";
        } else {
          error.value = "Value already exists";
        }
      } else if (data.error === "InvalidArgument") {
        error.value = "Invalid input. Please check your entries.";
      } else if (data.message) {
        error.value = data.message;
      } else {
        error.value = "Signup failed. Please try again.";
      }

      return;
    }

    success.value = true;
    verificationEmail.value = email.value;
    sessionStorage.setItem(pendingVerificationEmailKey, email.value);

    username.value = "";
    email.value = "";
    password.value = "";
    confirmPassword.value = "";

    // Move the user directly into verification step on this same page.
    setTimeout(() => {
      router.push({
        path: "/signup",
        query: { step: "verify" },
      });
    }, 2000);
  } catch (err) {
    console.error("Signup error:", err);
    error.value = "Network error. Please try again.";
  } finally {
    loading.value = false;
  }
};

const handleVerification = async (e) => {
  e.preventDefault();
  error.value = "";
  success.value = false;
  info.value = "";

  if (!verificationEmail.value) {
    error.value = "No pending signup found. Please register first.";
    return;
  }

  if (!isVerificationCodeValid.value) {
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
        email: verificationEmail.value,
        code: verificationCode.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || "Invalid or expired verification code");
    }

    success.value = true;
    info.value = "Email verified successfully. Redirecting to login...";
    sessionStorage.removeItem(pendingVerificationEmailKey);
    verificationCode.value = "";

    setTimeout(() => {
      router.push("/login");
    }, 1500);
  } catch (err) {
    error.value = err.message || "Verification failed. Please try again.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>{{ isVerificationStep ? "Verify Email" : "Create Account" }}</h1>

      <form v-if="!isVerificationStep" @submit="handleSignup">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Choose a username (6+ chars)"
            :disabled="loading"
            required
          />
          <small class="hint">
            Must start and end with alphanumeric characters
          </small>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="Enter your email"
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
            placeholder="Enter a strong password"
            :disabled="loading"
            required
          />
          <div class="password-requirements">
            <div :class="{ met: passwordRequirements.length(password) }">
              ✓ At least 12 characters
            </div>
            <div :class="{ met: passwordRequirements.hasLetter(password) }">
              ✓ Contains a letter
            </div>
            <div :class="{ met: passwordRequirements.hasDigit(password) }">
              ✓ Contains a digit
            </div>
            <div :class="{ met: passwordRequirements.hasSpecial(password) }">
              ✓ Contains a special character (!@#$%^&* etc.)
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            :disabled="loading"
            required
          />
          <small
            v-if="password && confirmPassword !== password"
            class="hint error"
          >
            Passwords do not match
          </small>
          <small
            v-else-if="password && confirmPassword === password"
            class="hint success"
          >
            Passwords match ✓
          </small>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="success" class="success-message">
          Account created successfully! Redirecting to verification...
        </div>

        <button
          type="submit"
          :disabled="loading || !isPasswordValid()"
          class="submit-button"
        >
          {{ loading ? "Creating account..." : "Sign Up" }}
        </button>
      </form>

      <form v-else @submit="handleVerification">
        <div class="form-group">
          <label for="verification-code">Verification Code</label>
          <input
            id="verification-code"
            v-model="verificationCode"
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="Enter your 6-digit code"
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

        <button
          type="submit"
          :disabled="loading || !isVerificationCodeValid"
          class="submit-button"
        >
          {{ loading ? "Verifying..." : "Verify" }}
        </button>
      </form>

      <p v-if="!isVerificationStep" class="login-link">
        Already have an account?
        <router-link to="/login">Login here</router-link>
      </p>

      <p v-else class="login-link">
        Need to create an account first?
        <router-link to="/signup">Back to sign up</router-link>
      </p>
    </div>
  </div>
</template>

<style src="../style.css"></style>
<style src="./signupPage.css"></style>
