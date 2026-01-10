<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { completeLogin } from "../auth/authService";

const router = useRouter();

onMounted(() => {
    // gets JWT from query, ex: /auth/callback?token=JWT_HERE
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
        completeLogin(token);
        router.replace("/");
    } else {
        alert("Login failed: no token received.");
        router.replace("/");
    }
});
</script>

<template>
    <div class="container">
        <h2>Logging in...</h2>
        <p>Please wait while we process your login.</p>
    </div>
</template>

<style scoped>
.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 70vh;
    color: var(--dark-text);
}
</style>
