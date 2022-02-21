
const endpoint = 'http://localhost:20200/api'

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

export {
  getHandlers,
  newHandler,
  stopHandler
}
