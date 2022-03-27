# TODOs

## Next Up
- [] Remove sourceoriginaccessed from postmessagereceived report as it can contain false positives
- [] In postmessagereceived report, hightlight corresponding message event handler that *could* be responsible for handling this event
  - Search for keywords appearing in postmessage data in all message event handler callbacks recorded before postmessage is received
- [] Check security of message event handler callback
  - Search for keywords like origin, and if no origin appears, this is a bad sign, mark as red
  - If origin appears, add the line in which it appears to report and mark in orange
  - Check for patterns like `.origin.startsWith`, `.origin.match`, ...
- [] Automatic exploit generation
  - In execution context, build automatic exploit generator
  - Considers information from reports and from statements, i.e., the frame in which the authreq is sent and the authreq itself
  - Exploit: `<html><script>/* 1) addEventListener 2) window.open | window.embed 3) window.postMessage? */</script></html>`
- [] Let user configure google, apple, facebook account for auto consent extension
- [] Update README.md

## Low Prio
- [] Prettify values and data from windowpropnew, postmessagereceived, localstorageset, ...
- [] Let user choose number of reports to display on single page
- [] Make report table columns width to fix on page
- [] Logging to file?
- [] Build logs feature to view all logs from backend in frontend
- [] Build export reports.json feature
- [] Build export all for report handler feature
- [] Build export all for all report handlers feature
- [] More details in about section

## Next Major Version
- [] Store and retrieve reports in / from database