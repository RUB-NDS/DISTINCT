<template>
  <div class="container mb-4">
    <h1 style="display: flex;">
      <span style="font-variant: small-caps">Communication-Inspector </span>
      <span v-if="appMode == 'demo'" class="badge bg-secondary rounded-pill" style="font-size: .5em; margin: auto .5em;">Demo Mode</span>
    </h1>
    <p>In this interface, you can start a new analysis run and inspect the analysis results.</p>
    <div class="btn-toolbar mb-2">
      <div class="btn-group me-2">
        <button class="btn btn-primary" v-on:click="getHandlers()">
          <i class="bi bi-arrow-clockwise"></i>
          Update
        </button>
      </div>
      <div class="input-group">
        <div class="input-group-text">
          <i class="bi bi-clock-history me-2"></i>
          <span>Update Interval</span>
        </div>
        <input type="number" class="form-control" min="0" max="60" v-on:input="startIntervalUpdater(this.$refs.updateInterval.value)" ref="updateInterval" :disabled="appMode == 'demo'">
        <div class="input-group-text">seconds</div>
      </div>
    </div>
    <div class="btn-toolbar mb-4">
      <div class="btn-group me-2">
        <button class="btn btn-primary" v-on:click="newHandler(this.$refs.initURL.value)" :disabled="appMode == 'demo'">
          <i class="bi bi-plus-circle"></i>
          New Analysis Run
        </button>
      </div>
      <div class="input-group">
        <div class="input-group-text">
          <i class="bi bi-cursor me-2"></i>
          <span>URL <i>(optional)</i></span>
        </div>
        <input type="text" class="form-control" ref="initURL" placeholder="https://example.com" size=30 :disabled="appMode == 'demo'">
      </div>
    </div>

    <div class="row row-cols-1 row-cols-xl-2 row-cols-xxl-4 g-4">
      <div class="col" v-for="reporthandler in this.reporthandlers" v-bind:key="reporthandler">
        <HandlerCardView
          :reporthandler="reporthandler"
          v-on:update-reporthandlers="getHandlers()"
        />
      </div>
    </div>

    <SVGModalView />
    <ReportsModalView />
    <StatementsModalView />
    <PoCModalView />
  </div>
</template>

<script>
import { getHandlers, newHandler } from '../api/connector.js'
import Handler from '../model/Handler.js'

import HandlerCardView from './HandlerCardView.vue'
import SVGModalView from './SVGModalView.vue'
import ReportsModalView from './ReportsModalView.vue'
import StatementsModalView from './StatementsModalView.vue'
import PoCModalView from './PoCModalView.vue'

export default {
  name: 'HandlersView',
  components: {
    HandlerCardView, SVGModalView, ReportsModalView, StatementsModalView,
    PoCModalView
  },
  data: () => {
    return {
      'reporthandlers': [],
      'intervalUpdater': undefined,
      'appMode': process.env['VUE_APP_MODE']
    }
  },
  methods: {
    'getHandlers': function() {
      getHandlers().then((r) => {
        if (r.success) {
          this.reporthandlers = r.data.map((r) => {
            return new Handler(
              r.uuid, r.running, r.starttime, r.reportsCount, r.queueSize,
              r.browser, r.proxy
            )
          })
        } else {
           alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'newHandler': function(initURL) {
      newHandler(initURL).then((r) => {
        if (r.success) {
          this.getHandlers()
        } else {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    },
    'startIntervalUpdater': function(seconds) {
      console.info(`Updating report handlers every ${seconds} seconds`)
      if (this.intervalUpdater) {
        clearInterval(this.intervalUpdater)
      }
      if (seconds > 0) {
        this.intervalUpdater = setInterval(() => {
          this.getHandlers()
        }, seconds * 1000)
      }
    },
  },
  mounted: function() {
    this.getHandlers()
  },
  beforeUnmount: function() {
    if (this.intervalUpdater) {
      clearInterval(this.intervalUpdater)
    }
  }
}
</script>

<style>

</style>
