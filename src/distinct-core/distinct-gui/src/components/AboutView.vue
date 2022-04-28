<template>
  <div class="container">
    <h1>DISTINCT: Dynamic In-Browser Single Sign-On Tracer Inspecting Novel Communication Techniques</h1>
    <p>DISTINCT is an analysis framework for modern communication techniques that was developed for the paper "DISTINCT: Identity Theft using Cross-Window Communications in Modern Single Sign-On".</p>

    <h3>Settings</h3>
    <form class="mb-4">
      <div class="form-group">
        <label for="vncpwd">noVNC Password:</label>
        <div class="input-group">
          <input type="text" class="form-control me-2" id="vncpwd" ref="vncpwd">
          <div class="input-group-append">
            <button type="submit" class="btn btn-primary" @click.prevent="changeVNCPWD(this.$refs.vncpwd.value)">Store</button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AboutView',
  mounted: function() {
    this.$refs.vncpwd.value = window.localStorage.getItem('vncpwd')
  },
  methods: {
    'changeVNCPWD': function(vncpwd) {
      window.localStorage.setItem('vncpwd', vncpwd)
    }
  }
}
</script>

<style>

</style>
