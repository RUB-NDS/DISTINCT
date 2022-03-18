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
      <li class="list-group-item">
        <span v-if="this.reporthandler.browser == null">Browser: <span style="color: orange;">Not started yet</span></span>
        <span v-else-if="this.reporthandler.browser.returncode == null">Browser: <span style="color: green;">Running</span></span>
        <span v-else>Browser: <span style="color: red;">Stopped</span></span>
      </li>
      <li class="list-group-item">
        <span v-if="this.reporthandler.proxy == null">Proxy: <span style="color: orange;">Not started yet</span></span>
        <span v-else-if="this.reporthandler.proxy.returncode == null">Proxy: <span style="color: green;">Running</span></span>
        <span v-else>Proxy: <span style="color: red;">Stopped</span></span>
      </li>
      <li class="list-group-item">Start Time: {{ timestampToDate(this.reporthandler.starttime) }}</li>
      <li class="list-group-item">Reports: {{ this.reporthandler.reportsCount }}</li>
      <li class="list-group-item">Queued: {{ this.reporthandler.queueSize }}</li>
      <li class="list-group-item">
        <div>Show:</div>
        <div class="btn-group" role="group">
          <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#reportsModal" :data-bs-handleruuid="reporthandler.uuid">
            <i class="bi bi-table"></i>
            Reports
          </button>
          <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#svgModal" v-on:click="showSVG(reporthandler.uuid)">
            <i class="bi bi-diagram-2"></i>
            SVG
          </button>
        </div>
      </li>
      <li class="list-group-item">
        <div>Export:</div>
        <div class="btn-group" role="group">
          <button type="button" class="btn btn-outline-primary" v-on:click="exportProfile(reporthandler.uuid)">
            <i class="bi bi-file-zip"></i>
            Profile
          </button>
          <button type="button" class="btn btn-outline-primary" v-on:click="exportStream(reporthandler.uuid)">
            <i class="bi bi-record-circle"></i>
            Stream
          </button>
          <button type="button" class="btn btn-outline-primary" v-on:click="exportHAR(reporthandler.uuid)">
            <i class="bi bi-archive"></i>
            HAR
          </button>
        </div>
      </li>
      <li class="list-group-item">
        <div>Actions:</div>
        <div class="btn-group" role="group">
          <button type="button" class="btn btn-outline-primary" v-on:click="startBrowser(reporthandler.uuid)">Start Browser</button>
          <button type="button" class="btn btn-outline-danger" v-on:click="stopBrowser(reporthandler.uuid)">Stop Browser</button>
          <button type="button" class="btn btn-outline-danger" v-on:click="stopHandler(reporthandler.uuid)">Stop Handler</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import {
  stopHandler, getSVG, startBrowser, stopBrowser,
  exportProfile, exportStream, exportHAR
} from '../api/connector.js'
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
    },
    'startBrowser': function(handler_uuid) {
      startBrowser(handler_uuid).then((r) => {
        if (r.success) {
          this.$router.push('/browser')
        } else {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'stopBrowser': function(handler_uuid) {
      stopBrowser(handler_uuid).then((r) => {
        if (!r.success) {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'exportProfile': function(handler_uuid) {
      exportProfile(handler_uuid).then((r) => {
        if (!r.success) {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'exportStream': function(handler_uuid) {
      exportStream(handler_uuid).then((r) => {
        if (!r.success) {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'exportHAR': function(handler_uuid) {
      exportHAR(handler_uuid).then((r) => {
        if (!r.success) {
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
