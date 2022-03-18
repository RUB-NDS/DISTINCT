<template>
  <div class="modal fade" tabindex="-1" id="statementsModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title"></h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" v-on:click="clearModal()"></button>
        </div>
        <div class="modal-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">Key</th>
                  <th scope="col">Value</th>
                </tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" v-on:click="clearModal()">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatementsModalView',
  methods: {
    'clearModal': function() {
      const modal = document.getElementById('statementsModal')
      const modalTitle = modal.querySelector('.modal-title')
      const tbody = modal.querySelector('tbody')
      modalTitle.textContent = ''
      tbody.innerHTML = ''
    }
  }
}
</script>

<style>

</style>
