class ReportHandler {
  constructor(uuid, running, starttime, reportsCount, queueSize, reports=[], svg=null) {
    this.uuid = uuid
    this.running = running
    this.starttime = starttime
    this.reportsCount = reportsCount
    this.queueSize = queueSize

    this.reports = reports
    this.svg = svg
  }
}

export default ReportHandler
