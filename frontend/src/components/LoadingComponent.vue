<template>
    <div class="loading-content">
      <div class="spinner"></div>
      <h2 class="status-title">Loading...</h2>
    </div>
</template>

<style scoped>
.loading-overlay {
  background-color: rgba(255, 255, 255, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.status-title {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

/* Mobile responsiveness */
@media (max-width: 480px) {
  .spinner {
    width: 35px;
    height: 35px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #007bff;
  }

  .status-title {
    font-size: 1rem;
  }
}
</style>
