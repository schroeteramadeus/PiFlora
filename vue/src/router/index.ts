import { createRouter, createWebHistory } from 'vue-router'
import MainMenu from '@/views/MainMenu.vue'
/*import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router
*/
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: MainMenu
    },
    {
      path: '/plantmanager',
      name: 'plantmanager',
      component: () => import('@/views/plants/PlantMenu.vue')
    },
    {
      path: '/plantmanager/plants',
      name: 'plantmanager_plants',
      component: () => import('@/views/plants/PlantSetup.vue')
    },
    {
      path: '/plantmanager/sensors',
      name: 'plantmanager_sensors',
      component: () => import('@/views/plants/SensorSetup.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/settings/SettingsMenu.vue')
    },
    {
      path: '/settings/server/log',
      name: 'settings_server_log',
      component: () => import('@/views/settings/ServerLogs.vue')
    },
    {
      path: '/settings/client/log',
      name: 'settings_client_log',
      component: () => import('@/views/settings/ClientLogs.vue')
    },
    {
      path: '/help',
      name: 'help',
      component: () => import('@/views/help/HelpMenu.vue')
    },
    {
      path: '/help/info',
      name: 'help_info',
      component: () => import('@/views/help/Info.vue')
    },
  ]
})

export default router