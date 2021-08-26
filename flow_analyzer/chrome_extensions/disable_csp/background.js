let isCSPDisabled = true

const onHeadersReceived = function(details) {
  if (!isCSPDisabled) return

  for (let i = 0; i < details.responseHeaders.length; i++)
    if (details.responseHeaders[i].name.toLowerCase() === "content-security-policy")
      details.responseHeaders[i].value = ""

  return {
    responseHeaders: details.responseHeaders,
  }
}

const updateUI = function() {
  const iconName = isCSPDisabled ? "on" : "off"
  const title = isCSPDisabled ? "disabled" : "enabled"

  chrome.browserAction.setIcon({ path: "images/icon38-" + iconName + ".png" })
  chrome.browserAction.setTitle({ title: "Content-Security-Policy headers are " + title })
}

const filter = {
  urls: ["*://*/*"],
  types: ["main_frame", "sub_frame"],
}

chrome.webRequest.onHeadersReceived.addListener(onHeadersReceived, filter, [
  "blocking",
  "responseHeaders",
])

chrome.browserAction.onClicked.addListener(function() {
  isCSPDisabled = !isCSPDisabled

  if (isCSPDisabled) chrome.browsingData.remove({}, { serviceWorkers: true }, () => null)

  updateUI()
})

updateUI()
