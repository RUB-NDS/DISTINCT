<template>
  <div class="container">
    <h1>Report Handlers</h1>
    <div class="btn-toolbar">
      <div class="btn-group me-2">
        <button class="btn btn-primary" v-on:click="getHandlers()">Update All</button>
      </div>
      <div class="btn-group me-2">
        <button class="btn btn-primary" v-on:click="newHandler()">New Handler</button>
      </div>
    </div>
    <p></p>

    <div class="row row-cols-1 row-cols-xl-2 row-cols-xxl-4 g-4">
      <div class="col" v-for="reporthandler in this.reporthandlers" v-bind:key="reporthandler">
        <ReportHandlerCard
          :reporthandler="reporthandler"
          v-on:update-reporthandlers="getHandlers()"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { getHandlers, newHandler } from '../api/connector.js'
import ReportHandler from '../model/ReportHandler.js'
import ReportHandlerCard from './ReportHandlerCard.vue'

export default {
  name: 'ReportHandlers',
  components: {
    ReportHandlerCard
  },
  data: () => {
    return {
      'reporthandlers': []
    }
  },
  methods: {
    'getHandlers': function() {
      getHandlers().then((r) => {
        if (r.success) {
          this.reporthandlers = r.data.map((r) => {
            return new ReportHandler(r.uuid, r.running)
          })
        } else {
           alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'newHandler': function() {
      newHandler().then((r) => {
        if (r.success) {
          this.getHandlers()
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
