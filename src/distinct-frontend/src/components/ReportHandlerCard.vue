<template>
  <div class="card">
    <div class="card-header" v-bind:class="[reporthandler.running ? 'bg-success' : 'bg-danger']">
      Report Handler
    </div>
    <div class="card-body">
      <h5 class="card-title">{{this.reporthandler.uuid}}</h5>
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item">
        <span v-if="this.reporthandler.running">Status: <span style="color: green;">Running</span></span>
        <span v-else>Status: <span style="color: red;">Stopped</span></span>
      </li>
    </ul>
    <div class="card-body">
      <div class="btn-group" role="group">
        <button type="button" class="btn btn-outline-danger" v-on:click="stopHandler(reporthandler.uuid)">Stop</button>
        <button type="button" class="btn btn-outline-primary">Reports</button>
        <button type="button" class="btn btn-outline-primary">SVG</button>
        <button type="button" class="btn btn-outline-primary">Proxy</button>
      </div>
    </div>
  </div>
</template>

<script>
import { stopHandler } from '../api/connector.js'

export default {
  name: 'ReportHandlerCard',
  props: ['reporthandler'],
  methods: {
    'stopHandler': function(handler_uuid) {
      stopHandler(handler_uuid).then((r) => {
        if (r.success) {
          setTimeout(() => {
            this.$emit('update-reporthandlers')
          }, 10000)
        } else {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
  }
}
</script>

<style>

</style>
