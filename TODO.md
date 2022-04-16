# TODOs

## Next Up
- [] In postmessagereceived report, hightlight corresponding message event handler that *could* be responsible for handling this event
  - Search for keywords appearing in postmessage data in all message event handler callbacks recorded before postmessage is received
- [] Check security of message event handler callback
  - Search for keywords like origin, and if no origin appears, this is a bad sign, mark as red
  - If origin appears, add the line in which it appears to report and mark in orange
  - Check for patterns like `.origin.startsWith`, `.origin.match`, ...
- [] Preconfigured filters like `type = postmessagereceived and content.check = *`
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
