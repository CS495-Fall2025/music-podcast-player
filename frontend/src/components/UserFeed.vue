<style src="../style.css"></style>

<script src="./userFeed.js"></script>

<template>
  <div class="user-feed">
    <Track v-for="(item, index) in feed" :key="index" :track="item" />
  </div>
</template>