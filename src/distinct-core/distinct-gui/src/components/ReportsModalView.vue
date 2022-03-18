<template>
  <div class="modal fade" tabindex="-1" id="reportsModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{handler_uuid}}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form class="mb-4">
            <div class="form-group mb-2">
              <input type="text" class="form-control" id="sq" placeholder="Enter search query" ref="sq">
            </div>
            <button type="submit" class="btn btn-primary" @click.prevent="applyFilter(this.$refs.sq.value)">Apply Filter</button>
          </form>
          <ReportsTableView :reports="filteredReports" />
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getReports } from '../api/connector.js'

import ReportsTableView from './ReportsTableView.vue'

export default {
  name: 'ReportsModalView',
  components: {
    ReportsTableView
  },
  data: () => {
    return {
      handler_uuid: "",
      reports: [],
      filteredReports: []
    }
  },
  mounted() {
    const modal = document.getElementById('reportsModal')
    modal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget
      const handler_uuid = button.getAttribute('data-bs-handleruuid')
      this.handler_uuid = handler_uuid

      getReports(handler_uuid).then((r) => {
        if (r.success) {
          // this.reports = r.data.reports
          this.reports = r.data.reports
          this.filteredReports = this.reports
        } else {
          alert(`Error: ${r['error']}`)
        }
      }).catch((e) => {
        alert(`Error: ${e['error']}`)
      })
    })
    modal.addEventListener('hidden.bs.modal', () => {
      this.handler_uuid = ""
      this.reports = []
    })
  },
  methods: {
    'applyFilter': function(sq) {
      // No filter
      if (sq == '') {
        this.filteredReports = this.reports
        return
      }

      // Filter for reports based on key
      this.filteredReports = this.reports.filter((r) => {
        return r.key == sq
      })
    }
  }
}
</script>

<style>

</style>
