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
    let browserURL = new URL(window.location.href)
    browserURL.port = '9090'
    browserURL.pathname = '/vnc_auto.html'
    browserURL.search = ''
    browserURL.hash = ''

    if (!window.localStorage.getItem('vncpwd')) {
      let pwd = prompt('Please enter the noVNC password')
      window.localStorage.setItem('vncpwd', pwd)
    }
    let vncpwd = window.localStorage.getItem('vncpwd')
    browserURL.searchParams.set('password', vncpwd)

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
