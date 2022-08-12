<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
      <div class="container-fluid">
        <a class="navbar-brand" href="#/"><span style="font-variant: small-caps">Distinct</span></a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-info-circle"></i>
                Info
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/handlers">
                <i class="bi bi-inboxes"></i>
                <span> Communication-Inspector</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/browser">
                <i class="bi bi-window"></i>
                <span style="font-variant: small-caps"> Live-Monitor</span>
              </router-link>
            </li>
          </ul>
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <a class="nav-link" href="https://github.com/RUB-NDS/DISTINCT">
                <i class="bi bi-github"></i>
                Source Code
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/paper.pdf">
                <i class="bi bi-file-earmark-pdf"></i>
                Paper
              </a>
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
  watch: {
    '$route' (to) {
      document.title = to.meta.title || 'DISTINCT'
    }
  }
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
