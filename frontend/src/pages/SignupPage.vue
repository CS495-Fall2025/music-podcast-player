<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");
const success = ref(false);

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
    const response = await fetch(
      `${import.meta.env.VITE_AUTH_API}/auth/signup`,
      {
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
      },
    );

    if (!response.ok) {
      const data = await response.json();
      if (data.error) {
        if (data.error.field === "username") {
          error.value = "Username already taken";
        } else if (data.error.field === "email") {
          error.value = "Email already registered";
        } else {
          error.value = data.error.message || "Signup failed";
        }
      } else {
        error.value = "Signup failed. Please try again.";
      }
      return;
    }

    success.value = true;
    username.value = "";
    email.value = "";
    password.value = "";
    confirmPassword.value = "";

    // redirect to login after successful sign-up
    setTimeout(() => {
      router.push("/login");
    }, 2000);
  } catch (err) {
    console.error("Signup error:", err);
    error.value = "Network error. Please try again.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>Create Account</h1>

      <form @submit="handleSignup">
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
          Account created successfully! Redirecting to login...
        </div>

        <button
          type="submit"
          :disabled="loading || !isPasswordValid()"
          class="submit-button"
        >
          {{ loading ? "Creating account..." : "Sign Up" }}
        </button>
      </form>

      <p class="login-link">
        Already have an account?
        <router-link to="/login">Login here</router-link>
      </p>
    </div>
  </div>
</template>

<style src="../style.css"></style>
<style src="./signupPage.css"></style>
