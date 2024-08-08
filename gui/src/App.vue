<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
  // import Router from 'vue-router'
  // const router = Router
  import router from './router';
  export default {
    name: 'App',
    router,
    methods: {

    }
  }

</script>

<style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #fff;
    width: 100%;
    height: 100%;
    overflow: hidden;
    box-sizing: border-box;
  }
</style>