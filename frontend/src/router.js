import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Quiz from './views/Quiz.vue'
import Review from './views/Review.vue'
import Experiences from './views/Experiences.vue'
import ExperienceDetail from './views/ExperienceDetail.vue'
import Search from './views/Search.vue'
import Settings from './views/Settings.vue'

// file:// 协议（APK 离线包）只能用 hash 路由
const history = location.protocol === 'file:' ? createWebHashHistory() : createWebHistory()

export const router = createRouter({
  history,
  routes: [
    { path: '/', component: Home },
    { path: '/quiz', component: Quiz },
    { path: '/review', component: Review },
    { path: '/experiences', component: Experiences },
    { path: '/experiences/:id', component: ExperienceDetail },
    { path: '/search', component: Search },
    { path: '/settings', component: Settings },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
