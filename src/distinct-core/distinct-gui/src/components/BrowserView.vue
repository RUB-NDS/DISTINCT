<template>
  <div class="container-fluid">
    <h1>Browser</h1>

    <iframe id="browserFrame" src="http://localhost:9090/vnc_auto.html?password=changeme"></iframe>
  </div>
</template>

<script>
export default {
  name: 'BrowserView',

}
</script>

<style scoped>
  #browserFrame {
    width: 100%;
    height: 100vh;
    border: none;
  }
</style>
