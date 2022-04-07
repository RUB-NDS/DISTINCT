<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#/">DISTINCT</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/handlers">
                <i class="bi bi-folder"></i>
                Handlers
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/browser">
                <i class="bi bi-window"></i>
                Browser
              </router-link>
            </li>
            <!-- <li class="nav-item">
              <router-link class="nav-link" to="/logs">
                <i class="bi bi-body-text"></i>
                Logs
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/settings">
                <i class="bi bi-gear"></i>
                Settings
              </router-link>
            </li> -->
            <li class="nav-item">
              <router-link class="nav-link" to="/about">
                <i class="bi bi-info-circle"></i>
                About
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <router-view
      :appconfig="this.appconfig"
      v-on:updateConfig="updateConfig"
    />
  </div>
</template>

<script>
export default {
  name: 'App',
  data: () => {
    return {
      'appconfig': {}
    }
  },
  methods: {
    'updateConfig': function(event) {
      this.appconfig[event.key] = event.val
    }
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
