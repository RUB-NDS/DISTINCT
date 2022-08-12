<template>
  <div class="container-fluid">
    <div class="container">
      <h1><span style="font-variant: small-caps">Live-Monitor</span></h1>
      <p>In this interface, you can control the browser to navigate to the target website and execute its Single Sign-On login.</p>
      <form v-if="appMode == 'prod'" class="mb-4">
        <div class="form-group">
          <label for="vncpwd">Configure noVNC Password:</label>
          <div class="input-group">
            <input type="text" class="form-control me-2" id="vncpwd" ref="vncpwd">
            <div class="input-group-append">
              <button type="submit" class="btn btn-primary" @click.prevent="changeVNCPWD(this.$refs.vncpwd.value)">Store</button>
            </div>
          </div>
        </div>
      </form>
    </div>
    <iframe v-if="appMode == 'prod'" id="browserFrame"></iframe>
  </div>
</template>

<script>
export default {
  name: 'BrowserView',
  data: function() {
    return {
      'appMode': process.env['VUE_APP_MODE']
    }
  },
  methods: {
    'changeVNCPWD': function(vncpwd) {
      window.localStorage.setItem('vncpwd', vncpwd)
      window.location.reload()
    }
  },
  mounted() {
    if (this.$data['appMode'] == 'prod') {
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

      this.$refs.vncpwd.value = window.localStorage.getItem('vncpwd')
    }
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
