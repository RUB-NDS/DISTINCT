<template>
  <div class="table-responsive">
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">ID</th>
          <th scope="col">Timestamp</th>
          <th scope="col">Hierarchy</th>
          <th scope="col">Href</th>
          <th scope="col">Key</th>
          <th scope="col">Value</th>
        </tr>
      </thead>
      <tbody>

        <tr v-for="report in reports" v-bind:key="report.id">
          <th scope="row">{{report.id}}</th>
          <td>{{report.timestamp}}</td>
          <td>{{report.val.hierarchy}}</td>
          <td>{{report.val.href}}</td>
          <td>{{report.key}}</td>
          <td>{{report.val}}</td>
        </tr>
      </tbody>
      <tfoot>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tfoot>
    </table>
  </div>
</template>

<script>
export default {
  name: 'ReportsTableView',
  props: ['reports'],
}
</script>

<style>

</style>
