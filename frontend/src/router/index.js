import { createRouter, createWebHistory } from 'vue-router';
import InputFeedPage from '../pages/InputFeedPage.vue';
import SearchFeedPage from '../pages/SearchFeedPage.vue';
import ViewFeedPage from '../pages/ViewFeedPage.vue';

const routes = [
  { path: '/', component: InputFeedPage },
  { path: '/search', component: SearchFeedPage},
  { path: '/view', component: ViewFeedPage},
];

const router = createRouter({
  history: createWebHistory(), // Uses history mode (clean URLs)
  routes,
});

export default router;
