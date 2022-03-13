class Handler {
  constructor(uuid, running, starttime, reportsCount, queueSize, browser, proxy, reports=[], svg=null) {
    this.uuid = uuid
    this.running = running
    this.starttime = starttime
    this.reportsCount = reportsCount
    this.queueSize = queueSize
    this.browser = browser
    this.proxy = proxy

    this.reports = reports
    this.svg = svg
  }
}

export default Handler
