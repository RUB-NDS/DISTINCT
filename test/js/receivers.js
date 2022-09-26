/* process the received data sent by the initiator */
const processReceivedData = (data) => {
  document.querySelector('#receivedData').innerText = `${JSON.stringify(data)}`
  Prism.highlightAll()
}

/* execute the selected receiver */
const execSelectedReceiver = () => {
  const receiver = getSelectedReceiver()
  receiver(window, processReceivedData)
}

/* get selected receiver from local storage */
const getSelectedReceiver = () => {
  const technique = getCookie('selectedReceiverTechnique')
  const type = getCookie('selectedReceiverType')
  return receivers[technique][type]
}

/* store selected receiver in local storage and display receiver code */
const selectReceiver = (selectedReceiver) => {
  const selectedReceiverSplitted = selectedReceiver.split(' | ')
  const technique = selectedReceiverSplitted[0]
  const type = selectedReceiverSplitted[1]
  const receiverFunction = receivers[technique][type]
  document.cookie = `selectedReceiverTechnique=${technique}; domain=.distinct-sso.com`
  document.cookie = `selectedReceiverType=${type}; domain=.distinct-sso.com`
  updateSelectedReceiverCode()
}

const updateSelectedReceiverCode = () => {
  const technique = getCookie('selectedReceiverTechnique')
  const type = getCookie('selectedReceiverType')
  const receiverFunction = receivers[technique][type]
  document.querySelector('#receiverSelectionCode').innerHTML = beautifyJS(receiverFunction.toString())
  Prism.highlightAll()
}

/* add receiver selection list to dom */
const receiverSelectionList = () => {
  const selectList = document.createElement('select')
  selectList.classList = 'form-select'
  selectList.setAttribute('multiple', '')
  selectList.setAttribute('onchange', 'selectReceiver(value)')
  for (let technique in receivers) {
    for (let type in receivers[technique]) {
      const selectOption = document.createElement('option')
      selectOption.setAttribute('value', `${technique} | ${type}`)
      selectOption.innerText = `${technique} | ${type}`
      selectList.appendChild(selectOption)
    }
  }
  document.querySelector('#receiverSelectionList').appendChild(selectList)
}

const receivers = {

  /* idle */

  idle: {
    idle: (receiverWindow, processData) => {
      // do nothing
    },
  },

  /* unsafe cross-origin: web messaging - postmessage */

  pm: {
    // insecure
    originMissing: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        processData(e.data)
      })
    },
    // insecure
    originIncludesLocationOrigin: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin.includes(location.origin)) {
          processData(e.data)
        }
      })
    },
    // insecure
    originStartsWithLocationOrigin: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin.startsWith(location.origin)) {
          processData(e.data)
        }
      })
    },
    // secure
    originEqualsFixed: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin === 'https://test.distinct-sso.com') {
          processData(e.data)
        }
      })
    },
    // secure
    originEqualsFixedAlt: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin === 'https://test-alt.distinct-sso.com') {
          processData(e.data)
        }
      })
    },
  },

  /* unsafe cross-origin: web messaging - channel messaging */

  cm: {
    // insecure
    originMissing: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.ports[0]) {
          e.ports[0].onmessage = (e) => {
            processData(e.data)
          }
        }
      })
    },
    // secure
    originEqualsFixed: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin === 'https://test.distinct-sso.com' && e.ports[0]) {
          e.ports[0].onmessage = (e) => {
            processData(e.data)
          }
        }
      })
    },
    // secure
    originEqualsFixedAlt: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin === 'https://test-alt.distinct-sso.com' && e.ports[0]) {
          e.ports[0].onmessage = (e) => {
            processData(e.data)
          }
        }
      })
    }
  },

  /* unsafe cross-origin: js navigate */

  jsnav: {
    // insecure
    hashChanged: (receiverWindow, processData) => {
      receiverWindow.addEventListener('hashchange', () => {
        processData(location.hash)
      })
    },
  },

  /* safe cross-origin: js reload */

  // nothing to receive here

  /* safe cross-origin: js properties */

  jsprop: {
    // secure
    closedPoll: (receiverWindow, processData) => {
      setInterval(() => {
        if (receiverWindow.popup.closed === true) {
          processData('popup was closed')
        }
      }, 1000);
    },
  },

  /* safe same-origin: js direct access */

  jsdirect: {
    callback: (receiverWindow, processData) => {
      receiverWindow.callback = (data) => {
        processData(data)
      }
    },
    prop: (receiverWindow, processData) => {
      setInterval(() => {
        if (receiverWindow.prop) processData(self.prop)
      }, 1000)
    },
  },

  /* safe same-origin: js storage */

  jsstore: {
    localstorage: (receiverWindow, processData) => {
      setTimeout(() => {
        processData(receiverWindow.localStorage['data'])
      }, 1000)
    },
    sessionstorage: (receiverWindow, processData) => {
      setTimeout(() => {
        processData(popup.sessionStorage['data'])
      }, 1000)
    },
    cookie: (receiverWindow, processData) => {
      setTimeout(() => {
        processData(receiverWindow.document.cookie)
      }, 1000)
    },
    idb: (receiverWindow, processData) => {
      setTimeout(() => {
        var open = indexedDB.open("MyDatabase", 1)
        open.onupgradeneeded = () => {
          var db = open.result
          var store = db.createObjectStore("MyObjectStore", {keyPath: "id", autoIncrement: true})
        }
        open.onsuccess = function() {
          var db = open.result
          var tx = db.transaction("MyObjectStore", "readwrite")
          var store = tx.objectStore("MyObjectStore")

          var req = store.getAll()

          tx.oncomplete = function() {
            processData(req.result)
            db.close()
            self.close()
          }
        }
      }, 1000)
    },
  },

  /* safe same-origin: web messaging - broadcast messaging */

  bm: {
    bm: (receiverWindow, processData) => {
      let channel = new BroadcastChannel('MyChannel')
      channel.onmessage = (e) => {
        processData(e.data)
      }
    },
  },

  /* safe same-origin: web messaging - custom events */

  ce: {
    ce: (receiverWindow, processData) => {
      receiverWindow.addEventListener('MyCustomEvent', (e) => {
        processData(e.detail.data)
      })
    },
  },

}
