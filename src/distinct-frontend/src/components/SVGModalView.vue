<template>
  <div class="modal fade" tabindex="-1" id="svgModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title"></h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" v-on:click="clearModal()"></button>
        </div>
        <div class="modal-body">
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
  name: 'SVGModalView',
  methods: {
    'clearModal': function() {
      const modal = document.getElementById('svgModal')
      const modalTitle = modal.querySelector('.modal-title')
      const modalBody = modal.querySelector('.modal-body')
      modalTitle.textContent = ''
      modalBody.innerHTML = ''
    }
  }
}
</script>

<style>

</style>
