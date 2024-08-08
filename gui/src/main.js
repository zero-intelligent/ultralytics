import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import videojs from 'video.js'
import 'element-ui/lib/theme-chalk/index.css';

Vue.use(ElementUI);
Vue.prototype.$videoJS = videojs;
Vue.config.productionTip = false
new Vue({
  render: h => h(App),
}).$mount('#app')
