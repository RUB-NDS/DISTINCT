class Report {
  constructor(id, timestamp, key, val) {
    this.id = id
    this.timestamp = timestamp
    this.key = key
    this.val = val

    this.hierarchy = val['hierarchy']
    this.href = val['href']
    this.protocol = val['hrefparts']['protocol']
    this.hostname = val['hrefparts']['hostname']
    this.port = val['hrefparts']['port']
    this.pathname = val['hrefparts']['pathname']
    this.query = val['hrefparts']['query']
    this.hash = val['hrefparts']['hash']
    this.origin = val['hrefparts']['origin']
  }
}

export default Report
