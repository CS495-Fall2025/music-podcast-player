<style src="../style.css"></style>

<script src="./searchedFeedsDisplay.js"></script>

<template>
  <div class="user-feed">
    <FeedCard v-for="(item, index) in searchedFeeds" :key="index" :feed="item" />
  </div>
</template>
