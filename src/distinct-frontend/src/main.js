import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import App from './App.vue'
import HandlersView from './components/HandlersView.vue'
import ReportsView from './components/ReportsView.vue'

const routes = [
  { path: '/', component: HandlersView },
  { path: '/handlers', component: HandlersView },
  { path: '/reports', component: ReportsView }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

createApp(App)
  .use(router)
  .mount('#app')
