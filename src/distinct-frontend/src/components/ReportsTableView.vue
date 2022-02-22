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

        <tr>
          <th scope="row">0</th>
          <td>1645520560.0830138</td>
          <td>top</td>
          <td>https://example.com/index.html?q=1#r=2</td>
          <td>documentinteractive</td>
          <td>foobar</td>
        </tr>
        <tr>
          <th scope="row">0</th>
          <td>1645520560.0830138</td>
          <td>top</td>
          <td>https://example.com/index.html?q=1#r=2</td>
          <td>documentinteractive</td>
          <td>foo</td>
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
