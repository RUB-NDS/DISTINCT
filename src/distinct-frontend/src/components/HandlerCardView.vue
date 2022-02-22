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
      <li class="list-group-item">Start Time: {{ timestampToDate(this.reporthandler.starttime) }}</li>
      <li class="list-group-item">Reports: {{ this.reporthandler.reportsCount }}</li>
      <li class="list-group-item">Queued: {{ this.reporthandler.queueSize }}</li>
    </ul>
    <div class="card-body">
      <div class="btn-group" role="group">
        <button type="button" class="btn btn-outline-danger" v-on:click="stopHandler(reporthandler.uuid)">Stop</button>
        <button type="button" class="btn btn-outline-primary">Reports</button>
        <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#svgModal" v-on:click="showSVG(reporthandler.uuid)">SVG</button>
        <button type="button" class="btn btn-outline-primary">Proxy</button>
      </div>
    </div>
  </div>
</template>

<script>
import { stopHandler, getSVG } from '../api/connector.js'
import { timestampToDate } from '../helpers.js'

export default {
  name: 'HandlerCardView',
  props: ['reporthandler'],
  methods: {
    'timestampToDate': timestampToDate,
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
    'showSVG': function(handler_uuid) {
      const modal = document.getElementById('svgModal')
      const modalTitle = modal.querySelector('.modal-title')
      const modalBody = modal.querySelector('.modal-body')
      modalTitle.textContent = handler_uuid

      getSVG(handler_uuid).then((r) => {
        if (r.success) {
          modalBody.innerHTML = r.data['svg']
        } else {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    }
  }
}
</script>

<style>

</style>
