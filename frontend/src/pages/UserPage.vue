<script setup>
const user = {
    name: "John Doe",
    email: "john.doe@example.com",
    createdAt: "2023-01-01T00:00:00Z"
}
</script>

<template>
    <div class="profile-container">
        <div class="profile-card">
            <h2>{{ user.name }}</h2>
            <p>Email: {{ user.email }}</p>
            <p>Joined: {{ new Date(user.createdAt).toLocaleDateString() }}</p>
        </div>
    </div>
</template>

<style src="../style.css"></style>
<style src="./userPage.css"></style>