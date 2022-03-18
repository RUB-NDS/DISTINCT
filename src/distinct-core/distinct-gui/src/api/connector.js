
const endpoint = `http://localhost:8080/api`

const getHandlers = () => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers`).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const newHandler = (initURL) => {
  return new Promise((resolve, reject) => {
    let config = {};
    if (initURL) {
      config['initurl'] = initURL
    }
    fetch(`${endpoint}/handlers`, {
      method: 'POST',
      body: JSON.stringify(config),
      headers: {
        'Content-Type': 'application/json'
      }
    }).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const stopHandler = (handler_uuid) => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers/${handler_uuid}/stop`, {method: 'POST'}).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const getSVG = (handler_uuid) => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers/${handler_uuid}/svg`).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const getReports = (handler_uuid) => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers/${handler_uuid}/reports`).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const getStatements = (handler_uuid) => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers/${handler_uuid}/statements`).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const startBrowser = (handler_uuid) => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/browsers/${handler_uuid}/start`, {method: 'POST'}).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const stopBrowser = (handler_uuid) => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/browsers/${handler_uuid}/stop`, {method: 'POST'}).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const exportProfile = (handler_uuid) => {
  return new Promise((resolve) => {
    window.open(`${endpoint}/browsers/${handler_uuid}/profile`, "_blank")
    resolve({'success': true, 'error': null, 'data': null})
  })
}

const exportStream = (handler_uuid) => {
  return new Promise((resolve) => {
    window.open(`${endpoint}/proxies/${handler_uuid}/stream`, "_blank")
    resolve({'success': true, 'error': null, 'data': null})
  })
}

const exportHAR = (handler_uuid) => {
  return new Promise((resolve) => {
    window.open(`${endpoint}/proxies/${handler_uuid}/har`, "_blank")
    resolve({'success': true, 'error': null, 'data': null})
  })
}

export {
  getHandlers,
  newHandler,
  stopHandler,
  getSVG,
  getReports,
  getStatements,
  startBrowser,
  stopBrowser,
  exportProfile,
  exportStream,
  exportHAR
}
