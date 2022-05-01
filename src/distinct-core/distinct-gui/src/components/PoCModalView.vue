<template>
  <div class="modal fade" tabindex="-1" id="pocModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title"></h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" v-on:click="clearModal()"></button>
        </div>
        <div class="modal-body">
          <p>PoC deployed on <a id="deployURL" href="" target="_blank"></a>.</p>
          <pre class="language-html"><code></code></pre>
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
  name: 'PoCModalView',
  methods: {
    'clearModal': function() {
      const modal = document.getElementById('pocModal')
      const modalTitle = modal.querySelector('.modal-title')
      const modalBody = modal.querySelector('.modal-body')
      const modalCode = modalBody.querySelector('code')
      modalTitle.textContent = ''
      modalCode.innerHTML = ''
    }
  }
}
</script>

<style>
</style>
