/* execute the selected initiator */
const execSelectedInitiator = () => {
  const initiator = getSelectedInitiator()
  initiator(window.opener, new URL(location.href).search)
}

/* get selected initiator from local storage */
const getSelectedInitiator = () => {
  const technique = getCookie('selectedInitiatorTechnique')
  const type = getCookie('selectedInitiatorType')
  return initiators[technique][type]
}

/* store selected initiator in local storage and display initiator code */
const selectInitiator = (selectedInitiator) => {
  const selectedInitiatorSplitted = selectedInitiator.split(' | ')
  const technique = selectedInitiatorSplitted[0]
  const type = selectedInitiatorSplitted[1]
  const initiatorFunction = initiators[technique][type]
  document.cookie = `selectedInitiatorTechnique=${technique}; domain=.distinct-sso.com`
  document.cookie = `selectedInitiatorType=${type}; domain=.distinct-sso.com`
  updateSelectedInitiatorCode()
}

const updateSelectedInitiatorCode = () => {
  const technique = getCookie('selectedInitiatorTechnique')
  const type = getCookie('selectedInitiatorType')
  const initiatorFunction = initiators[technique][type]
  document.querySelector('#initiatorSelectionCode').innerHTML = beautifyJS(initiatorFunction.toString())
  Prism.highlightAll()
}

/* add initiator selection list to dom */
const initiatorSelectionList = () => {
  const selectList = document.createElement('select')
  selectList.classList = 'form-select'
  selectList.setAttribute('multiple', '')
  selectList.setAttribute('onchange', 'selectInitiator(value)')
  for (let technique in initiators) {
    for (let type in initiators[technique]) {
      const selectOption = document.createElement('option')
      selectOption.setAttribute('value', `${technique} | ${type}`)
      selectOption.innerText = `${technique} | ${type}`
      selectList.appendChild(selectOption)
    }
  }
  document.querySelector('#initiatorSelectionList').appendChild(selectList)
}

const initiators = {

  /* unsafe cross-origin: web messaging - postmessage */

  pm: {
    // insecure
    wildcard: (receiverWindow, data) => {
      receiverWindow.postMessage(data, '*')
      self.close()
    },
    // insecure
    windowOrigin: (receiverWindow, data) => {
      receiverWindow.postMessage(data, window.origin)
      self.close()
    },
    // secure
    locationOrigin: (receiverWindow, data) => {
      receiverWindow.postMessage(data, location.origin)
      self.close()
    },
    // secure
    fixedOrigin: (receiverWindow, data) => {
      receiverWindow.postMessage(data, 'https://test.distinct-sso.com/callback.html')
      self.close()
    },
  },

  /* unsafe cross-origin: web messaging - channel messaging */

  cm: {
    // insecure
    wildcard: (receiverWindow, data) => {
      let channel = new MessageChannel()
      receiverWindow.postMessage(null, '*', [channel.port2])
      setTimeout(() => {
        channel.port1.postMessage(data)
        self.close()
      }, 1000)
    },
    // insecure
    windowOrigin: (receiverWindow, data) => {
      let channel = new MessageChannel()
      receiverWindow.postMessage(null, window.origin, [channel.port2])
      setTimeout(() => {
        channel.port1.postMessage(data)
        self.close()
      }, 1000)
    },
    // secure
    locationOrigin: (receiverWindow, data) => {
      let channel = new MessageChannel()
      receiverWindow.postMessage(null, location.origin, [channel.port2])
      setTimeout(() => {
        channel.port1.postMessage(data)
        self.close()
      }, 1000)
    },
    // secure
    fixedOrigin: (receiverWindow, data) => {
      let channel = new MessageChannel()
      receiverWindow.postMessage(null, 'https://test.distinct-sso.com/callback.html', [channel.port2])
      setTimeout(() => {
        channel.port1.postMessage(data)
        self.close()
      }, 1000)
    },
  },

  /* unsafe cross-origin: js navigate */

  jsnav: {
    // insecure
    relative: (receiverWindow, data) => {
      receiverWindow.location = `/index.html${data}`
      self.close()
    },
    // insecure
    hash: (receiverWindow, data) => {
      receiverWindow.location.href = `https://test.distinct-sso.com#${data}`
      self.close()
    },
    // secure
    absolute: (receiverWindow, data) => {
      receiverWindow.location = `https://test.distinct-sso.com/index.html${data}`
      self.close()
    },
    // secure
    absoluteSlashSlash: (receiverWindow, data) => {
      receiverWindow.location = `//test.distinct-sso.com/index.html${data}`
      self.close()
    },
    // secure
    absoluteLocationOrigin: (receiverWindow, data) => {
      receiverWindow.location = `${location.origin}/index.html${data}`
      self.close()
    },
  },

  /* safe cross-origin: js reload */

  jsreload: {
    reload: (receiverWindow, data) => {
      receiverWindow.location.reload()
      self.close()
    },
  },

  /* safe cross-origin: js properties */

  jsprop: {
    close: (receiverWindow, data) => {
      setTimeout(() => {
        self.close()
      }, 5000)
    },
  },

  /* safe same-origin: js direct access */

  jsdirect: {
    callback: (receiverWindow, data) => {
      receiverWindow.callback(data)
      self.close()
    },
    prop: (receiverWindow, data) => {
      receiverWindow.prop = data
      self.close()
    },
  },

  /* safe same-origin: js storage */

  jsstore: {
    localstorage: (receiverWindow, data) => {
      self.localStorage['data'] = data
      self.localStorage.setItem('data', data)
      self.close()
    },
    sessionstorage: (receiverWindow, data) => {
      self.sessionStorage['data'] = data
      self.sessionStorage.setItem('data', data)
      setTimeout(()=> {
        self.close()
      }, 2000)
    },
    cookie: (receiverWindow, data) => {
      self.document.cookie = `data=${data}`
      self.close()
    },
    idb: (receiverWindow, data) => {
      var open = indexedDB.open("MyDatabase", 1)
      open.onupgradeneeded = () => {
        var db = open.result
        var store = db.createObjectStore("MyObjectStore", {keyPath: "id", autoIncrement: true})
      }
      open.onsuccess = function() {
        var db = open.result
        var tx = db.transaction("MyObjectStore", "readwrite")
        var store = tx.objectStore("MyObjectStore")

        store.put({key: 'data', value: data})
        store.add({key: 'data', value: data})

        tx.oncomplete = function() {
          db.close()
          self.close()
        }
      }
    },
  },

  /* safe same-origin: web messaging - broadcast messaging */

  bm: {
    bm: (receiverWindow, data) => {
      let channel = new BroadcastChannel('MyChannel')
      channel.postMessage(data)
      self.close()
    },
  },

  /* safe same-origin: web messaging - custom events */

  ce: {
    ce: (receiverWindow, data) => {
      let customEvent = new CustomEvent('MyCustomEvent', {
        detail: { data: data }
      })
      receiverWindow.dispatchEvent(customEvent)
      self.close()
    },
  },

}
