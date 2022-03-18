import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'bootstrap-icons/font/bootstrap-icons.css'

import App from './App.vue'
import HandlersView from './components/HandlersView.vue'
import ReportsView from './components/ReportsView.vue'
import LogsView from './components/LogsView.vue'
import SettingsView from './components/SettingsView.vue'
import BrowserView from './components/BrowserView.vue'
import AboutView from './components/AboutView.vue'

const routes = [
  { path: '/', component: HandlersView },
  { path: '/handlers', component: HandlersView },
  { path: '/reports/:handler_uuid', component: ReportsView },
  { path: '/logs', component: LogsView },
  { path: '/browser', component: BrowserView },
  { path: '/settings', component: SettingsView },
  { path: '/about', component: AboutView }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

createApp(App)
  .use(router)
  .mount('#app')
