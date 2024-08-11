import Vue from 'vue'
import Router from 'vue-router'
// import Layout from '@/layout'
Vue.use(Router)
let prefix = ''
// let layout = Layout;

const routes = [
  {
    path: prefix + '/',
    // component: layout,
    redirect: prefix + '/home',
  },
  {
    path: prefix + '/home',
    component: () => import('@/views/home.vue'),
    hidden: true
  },
]

const router = new Router({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes
})

export default router
