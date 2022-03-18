<template>
  <div class="container mb-4">
    <h1>Handlers</h1>
    <div class="btn-toolbar mb-2">
      <div class="btn-group me-2">
        <button class="btn btn-primary" v-on:click="getHandlers()">
          <i class="bi bi-arrow-clockwise"></i>
          Update All
        </button>
      </div>
      <div class="input-group">
        <div class="input-group-text">
          <i class="bi bi-clock-history me-2"></i>
          Interval
        </div>
        <input type="number" class="form-control" min="0" max="60" v-on:input="startIntervalUpdater(this.$refs.updateInterval.value)" ref="updateInterval">
        <div class="input-group-text">s</div>
      </div>
    </div>
    <div class="btn-toolbar mb-4">
      <div class="btn-group me-2">
        <button class="btn btn-primary" v-on:click="newHandler()">
          <i class="bi bi-plus-circle"></i>
          New Handler
        </button>
      </div>
      <div class="input-group">
        <div class="input-group-text">
          <i class="bi bi-cursor me-2"></i>
          URL Preload
        </div>
        <input type="text" class="form-control" ref="preloadURL">
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
  </div>
</template>

<script>
import { getHandlers, newHandler } from '../api/connector.js'
import Handler from '../model/Handler.js'

import HandlerCardView from './HandlerCardView.vue'
import SVGModalView from './SVGModalView.vue'
import ReportsModalView from './ReportsModalView.vue'

export default {
  name: 'HandlersView',
  components: {
    HandlerCardView, SVGModalView, ReportsModalView
  },
  data: () => {
    return {
      'reporthandlers': [],
      'intervalUpdater': undefined
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
