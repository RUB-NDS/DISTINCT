class ReportHandler {
  constructor(uuid, running, reports=[], svg=null) {
    this.uuid = uuid
    this.running = running
    this.reports = reports
    this.svg = svg
  }
}

export default ReportHandler
