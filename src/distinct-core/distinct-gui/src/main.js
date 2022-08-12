import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'bootstrap-icons/font/bootstrap-icons.css'

import App from './App.vue'
import InfoView from './components/InfoView.vue'
import HandlersView from './components/HandlersView.vue'
import BrowserView from './components/BrowserView.vue'

const routes = [
  {
    path: '/',
    component: InfoView,
    meta: {title: 'DISTINCT'}
  },
  {
    path: '/handlers',
    component: HandlersView,
    meta: {title: 'DISTINCT - Handlers'}
  },
  {
    path: '/browser',
    component: BrowserView,
    meta: {title: 'DISTINCT - Browser'}
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

createApp(App)
  .use(router)
  .mount('#app')
