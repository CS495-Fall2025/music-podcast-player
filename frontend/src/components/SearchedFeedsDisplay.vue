<style src="../style.css"></style>

<script src="./searchedFeedsDisplay.js"></script>

<template>
  <div class="feeds">
    <FeedCard
      v-for="(item, index) in searchedFeeds"
      :key="index"
      :feed="item"
    />
  </div>
</template>

<style scoped>
.feeds {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 10px;
}
</style>
