<template>
  <div>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark mb-4">
      <div class="container-fluid">
        <a class="navbar-brand">DISTINCT</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
          <ul class="navbar-nav me-auto mb-2 mb-md-0">
            <li class="nav-item">
              <a class="nav-link" href="/" @click.prevent="go">Report Handlers</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">
      <ReportHandlers />
    </div>
  </div>
</template>

<script>
import ReportHandlers from './components/ReportHandlers.vue'

export default {
  name: 'App',
  data: () => {
    return {
      'reporthandlers': []
    }
  },
  components: {
    ReportHandlers
  },
  methods: {
    go: (event) => {
      let href = event.target.attributes["href"].value
      alert(`going to ${href}`)
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
