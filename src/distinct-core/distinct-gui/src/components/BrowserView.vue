<template>
  <div class="container-fluid">
    <h1>Browser</h1>

    <iframe id="browserFrame"></iframe>
  </div>
</template>

<script>
export default {
  name: 'BrowserView',
  mounted() {
    let currentURL = new URL(window.location.href)
    let browserURL = new URL()
    browserURL.protocol = currentURL.protocol
    browserURL.host = currentURL.host
    browserURL.port = '9090'
    browserURL.pathname = '/vnc_auto.html'
    // browserURL.searchParams.set('password', 'changeme')

    let browserFrame = document.getElementById('browserFrame')
    browserFrame.src = browserURL.href
  }
}
</script>

<style scoped>
  #browserFrame {
    width: 100%;
    height: 100vh;
    border: none;
  }
</style>
