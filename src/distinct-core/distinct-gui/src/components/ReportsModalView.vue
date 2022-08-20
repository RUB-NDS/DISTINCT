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
            <div class="form-group">

              <!-- Custom Search Query -->
              <label for="sq">Submit a custom Search Query:</label>
              <div class="input-group">
                <input type="text" class="form-control me-2" id="sq" placeholder='type = "postmessagereceived" and content.data_type = "string" ...' ref="sq">
                <div class="input-group-append">
                  <button type="submit" class="btn btn-primary" @click.prevent="applyFilter(this.$refs.sq.value)">Apply Filter</button>
                </div>
              </div>
              <small class="form-text text-muted">
                Compare Operators: <code>=</code>, <code>!=</code>, <code>&gt;=</code>, <code>&lt;=</code>, <code>&gt;</code>, <code>&lt;</code>, <code>CONTAINS</code>, <code>STARTS WITH</code>, <code>ENDS WITH</code>, <code>DOES NOT CONTAIN</code>
              </small>
              <br />
              <small class="form-text text-muted">
                Logical Operators: <code>AND</code>, <code>OR</code>
              </small>
              <br />
              <small class="form-text text-muted">
                Fields: <code>id</code>, <code>timestamp</code>, <code>type</code>, <code>hierarchy</code>, <code>url</code>, <code>content.&lt;key&gt;</code>
              </small>
              <br />

              <!-- Suggested Search Query -->
              <label class="mt-2" for="exampleQueries">Select a suggested Search Query:</label>
              <select id="exampleQueries" class="form-select" size="6" @change="selectExampleQuery($event)">
                <option value='' selected></option>

                <option value='type = "documentinit" or type = "documentinteractive"'>Show all documents</option>
                <option value='hierarchy = "top" and (type = "documentinit" or type = "documentinteractive")'>Show all documents in primary window</option>
                <option value='hierarchy contains "popups" and (type = "documentinit" or type = "documentinteractive")'>Show all documents in popup</option>
                <option value='type = "windowopen" or type = "windowclose"'>Show all popup openings and closings</option>

                <option value='type = "httpredirect" or type = "formsubmit" or type = "metaredirect" or type = "metareload" or type = "refreshredirect" or type = "refreshreload"'>Show all URL Redirects</option>
                <option value='type = "windowpropnew" or type = "windowpropchanged"'>Show all JS Direct Accesses</option>
                <option value='type = "closedaccessed"'>Show all JS Properties</option>
                <option value='type = "localstorageset" or type = "sessionstorageset" or type = "cookieset" or type = "idbadd" or type = "idbput"'>Show all JS Storage Accesses</option>

                <option value='type = "customeventreceived"'>Show all Custom Events</option>
                <option value='type = "customeventreceived" and content.source_frame contains "popups"'>Show all Custom Events sent from popup</option>
                <option value='type = "channelmessagereceived"'>Show all Channel Messages</option>
                <option value='type = "channelmessagereceived" and content.source_frame contains "popups"'>Show all Channel Messages sent from popup</option>
                <option value='type = "broadcastmessagereceived"'>Show all Broadcast Messages</option>
                <option value='type = "broadcastmessagereceived" and content.source_frame contains "popups"'>Show all Broadcast Messages sent from popup</option>

                <option value='type = "postmessagereceived"'>Show all postMessages</option>
                <option value='type = "postmessagereceived" and content.sso_params = true'>Show all postMessages with SSO parameters</option>
                <option value='type = "postmessagereceived" and content.data contains "token"'>Show all postMessages with string "token" in data</option>
                <option value='type = "postmessagereceived" and content.source_frame contains "popups"'>Show all postMessages sent from popup</option>
                <option value='type = "postmessagereceived" and content.target_origin_check = "*"'>Show all postMessages with wildcard <code>*</code></option>
                <option value='type = "postmessagereceived" and content.target_origin_check = "*" and content.source_frame contains "popups"'>Show all postMessages sent from popup with wildcard <code>*</code></option>
                <option value='type = "postmessagereceived" and content.data contains "token" and content.target_origin_check = "*"'>Show all postMessages with string "token" in data and wildcard <code>*</code></option>
                <option value='type = "addeventlistener" and content.type = "message"'>Show all postMessage Event Listeners</option>

                <option value='type = "locationset"'>Show all JS Navigates</option>
                <option value='type = "locationset" and content.relative_redirect = false'>Show all JS Navigates with absolute URLs</option>
                <option value='type = "locationset" and content.relative_redirect = true'>Show all JS Navigates with relative URLs</option>
              </select>

              <!-- Pretty Print -->
              <div class="mt-2">
                <label class="form-check-label me-2" for="prettyPrintHTMLCheckbox">Pretty Print HTML:</label>
                <input class="form-check-input" type="checkbox" id="prettyPrintHTMLCheckbox" @change="prettyPrintClicked($event)">
              </div>
            </div>
          </form>

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
    },
    'selectExampleQuery': function(event) {
      let exampleQuery = event.target.value
      this.$refs.sq.value = exampleQuery
      this.applyFilter(this.$refs.sq.value)
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
