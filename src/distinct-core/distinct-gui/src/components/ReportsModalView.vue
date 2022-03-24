<template>
  <div class="modal fade" tabindex="-1" id="reportsModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{handler_uuid}}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <!-- Modal Body Start -->

          <!-- Filter Reports View -->
          <form class="mb-4">
            <div class="form-group mb-2">
              <input type="text" class="form-control" id="sq" placeholder="Enter search query" ref="sq">
              <small class="form-text text-muted">
                Operators: <code>=</code>, <code>!=</code>, <code>&gt;=</code>, <code>&lt;=</code>, <code>&gt;</code>, <code>&lt;</code>, <code>CONTAINS</code>, <code>STARTS WITH</code>, <code>ENDS WITH</code>, <code>DOES NOT CONTAIN</code>
              </small>
              <br />
              <small class="form-text text-muted">
                Logical: <code>AND</code>, <code>OR</code>
              </small>
              <br />
              <small class="form-text text-muted">
                Fields: <code>id</code>, <code>timestamp</code>, <code>type</code>, <code>hierarchy</code>, <code>url</code>, <code>content.&lt;key&gt;</code>
              </small>
            </div>
            <button type="submit" class="btn btn-primary" @click.prevent="applyFilter(this.$refs.sq.value)">Apply Filter</button>
          </form>

          <!-- Pretty Print HTML -->
          <div class="form-check">
            <input class="form-check-input" type="checkbox" id="prettyPrintHTMLCheckbox" @change="prettyPrintClicked($event)">
            <label class="form-check-label" for="prettyPrintHTMLCheckbox">
              Pretty Print HTML
            </label>
          </div>

          <!-- Reports Table View -->
          <ReportsTableView :reports="filteredReportsForCurrentPage" :prettyPrintHTML="prettyPrintHTML" />

          <!-- Table Pagination View -->
          <nav>
            <ul class="pagination">
              <li class="page-item">
                <a class="page-link" @click.prevent="changePage(this.currentPage-1)" href="#">&laquo;</a>
              </li>
              <li :class="(pageIndex == this.currentPage) ? 'page-item active' : 'page-item'" v-for="pageIndex in numberPages" v-bind:key="pageIndex">
                <a class="page-link" @click.prevent="changePage(pageIndex)" href="#">{{pageIndex}}</a>
              </li>
              <li class="page-item">
                <a class="page-link" @click.prevent="changePage(this.currentPage+1)" href="#">&raquo;</a>
              </li>
            </ul>
            Total: {{this.filteredReports.length}}
          </nav>

        <!-- Modal Body End -->
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
import { filterReports } from '../helpers.js'

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
      filteredReports: [],
      filteredReportsForCurrentPage: [],
      reportsPerPage: 50,
      currentPage: 1,
      prettyPrintHTML: false
    }
  },
  computed: {
    numberPages: function() {
      return Math.ceil(this.filteredReports.length / this.reportsPerPage)
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
          this.currentPage = 1
          this.reports = r.data.reports
          this.filteredReports = this.reports
          this.filteredReportsForCurrentPage = this.filteredReports.slice(0, this.reportsPerPage)
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
      this.filteredReports = []
      this.filteredReportsForCurrentPage = []
    })
  },
  methods: {
    'applyFilter': function(sq) {
      // console.log(this.reports)
      try {
        this.currentPage = 1
        this.filteredReports = filterReports(this.reports, sq)
        this.filteredReportsForCurrentPage = this.filteredReports.slice(
          (this.currentPage - 1) * this.reportsPerPage,
          this.currentPage * this.reportsPerPage
        )
      } catch (e) {
        alert(`Error: ${e['message']}`)
        console.error(e)
      }
    },
    'changePage': function(page) {
      if (page < 1 || page > this.numberPages) {
        return
      }
      this.currentPage = page
      this.filteredReportsForCurrentPage = this.filteredReports.slice(
        (this.currentPage - 1) * this.reportsPerPage,
        this.currentPage * this.reportsPerPage
      )
    },
    'prettyPrintClicked': function(event) {
      this.prettyPrintHTML = event.target.checked
    }
  }

  // Filter for reports based on key
  // this.filteredReports = this.reports.filter((r) => {
  //   return r.key == sq
  // })
}
</script>

<style>

</style>
