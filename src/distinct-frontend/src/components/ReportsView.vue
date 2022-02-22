<template>
  <div class="container-fluid">
    <h1>Reports</h1>
    <h5>Handler: {{ this.$route.params.handler_uuid }}</h5>

    <ReportsTableView :reports="reports" />
  </div>
</template>

<script>
import { getReports } from '../api/connector.js'

import ReportsTableView from './ReportsTableView.vue'

export default {
  name: "ReportsView",
  components: {
    ReportsTableView
  },
  data: () => {
    return {
      reports: []
    }
  },
  created() {
    if (this.$route.params.handler_uuid) {
      getReports(this.$route.params.handler_uuid).then((r) => {
        if (r.success) {
          this.reports = r.data.reports
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
