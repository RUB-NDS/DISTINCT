import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import App from './App.vue'
import HandlersView from './components/HandlersView.vue'
import ReportsView from './components/ReportsView.vue'
import LogsView from './components/LogsView.vue'

const routes = [
  { path: '/', component: HandlersView },
  { path: '/handlers', component: HandlersView },
  { path: '/reports/:handler_uuid', component: ReportsView },
  { path: '/logs', component: LogsView }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

createApp(App)
  .use(router)
  .mount('#app')
