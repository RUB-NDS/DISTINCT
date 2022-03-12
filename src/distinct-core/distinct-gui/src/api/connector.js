
const endpoint = `${location.origin}/api`

const getHandlers = () => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers`).then((r) => r.json()).then((r) => {
      resolve(r)
    }).catch((e) => {
      reject({'success': false, 'error': e, 'data': null})
    })
  })
}

const newHandler = () => {
  return new Promise((resolve, reject) => {
    fetch(`${endpoint}/handlers`, {method: 'POST'}).then((r) => r.json()).then((r) => {
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

export {
  getHandlers,
  newHandler,
  stopHandler,
  getSVG,
  getReports,
  startBrowser,
  stopBrowser
}
