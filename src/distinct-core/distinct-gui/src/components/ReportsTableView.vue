<template>
  <div class="table-responsive">
    <table class="table"> <!--table-striped-->
      <thead>
        <tr>
          <th scope="col">ID</th>
          <th scope="col">Timestamp</th>
          <th scope="col">Report</th>
          <th scope="col">Hierarchy</th>
          <th scope="col">URL</th>
          <th scope="col">Content</th>
        </tr>
      </thead>
      <tbody>

        <tr v-for="report in reports" v-bind:key="report.id">
          <th scope="row">{{report.id}}</th>
          <td>{{report.val.timestamp}}</td>
          <td>{{report.key}}</td>
          <td>{{report.val.hierarchy}}</td>
          <td class="href">{{report.val.href}}</td>
          <td class="td-content">
            <div v-for="(val, key) in this.filterVals(report.val)" v-bind:key="key" class="val">
              <span v-if="key == 'html'">
                <b>{{key}}</b>:
                <pre class="language-html"><code>{{this.beautifyHTML(val)}}</code></pre>
              </span>
              <span v-else>
                <b>{{key}}</b>: {{val}}
              </span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Prism from 'prismjs'
import html_beautify from 'js-beautify'
import 'prismjs/themes/prism.css'

export default {
  name: 'ReportsTableView',
  props: ['reports'],
  computed: {
    numReports: function() {
      return this.reports.length
    }
  },
  methods: {
    'filterVals': function(vals) {
      return Object.fromEntries(Object.entries(vals).filter(([key]) => {
        return (
          key !== 'timestamp'
          && key !== 'hierarchy'
          && key !== 'href'
          && key !== 'hrefparts'
        )
      }))
    },
    'beautifyHTML': function(html) {
      return html_beautify.html(html, {
        "indent_size": 2,
        "indent_char": " ",
        "indent_with_tabs": false,
        "eol": "\n",
        "end_with_newline": false,
        "indent_level": 0,
        "preserve_newlines": true,
        "max_preserve_newlines": 10,
        "space_in_paren": false,
        "space_in_empty_paren": false,
        "jslint_happy": false,
        "space_after_anon_function": false,
        "space_after_named_function": false,
        "brace_style": "collapse",
        "unindent_chained_methods": false,
        "break_chained_methods": false,
        "keep_array_indentation": false,
        "unescape_strings": false,
        "wrap_line_length": 0,
        "e4x": false,
        "comma_first": false,
        "operator_position": "before-newline",
        "indent_empty_lines": false,
        "templating": ["auto"]
      })
    }
  },
  updated() {
    Prism.highlightAll()
  }
}
</script>

<style>
  pre {
    overflow: auto;
    max-height: 50vh;
    max-width: 80vw;
  }

  .val {
    overflow: auto;
    max-height: 50vh;
    max-width: 80vw;
  }

  .href {
    overflow: auto;
    max-width: 30vw;
  }
</style>
