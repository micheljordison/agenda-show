import { createRouter, createWebHistory } from 'vue-router'
import { route } from 'quasar/wrappers'
import { useAuthStore } from '../stores/auth'
import LoginPage from '../pages/LoginPage.vue'
import CalendarPage from '../pages/CalendarPage.vue'

const routes = [
  { path: '/login', component: LoginPage },
  { path: '/', component: CalendarPage, meta: { requiresAuth: true } }
]

export default route(() => {
  const router = createRouter({
    history: createWebHistory(process.env.VUE_ROUTER_BASE),
    routes
  })

  router.beforeEach(async (to) => {
    const auth = useAuthStore()
    if (to.meta.requiresAuth && !auth.token) {
      return '/login'
    }
    if (to.meta.requiresAuth && auth.token && !auth.user) {
      try {
        await auth.fetchMe()
      } catch {
        return '/login'
      }
    }
    if (to.path === '/login' && auth.token) {
      return '/'
    }
  })

  return router
})
