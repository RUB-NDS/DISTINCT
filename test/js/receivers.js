/* process the received data sent by the initiator */
const processReceivedData = (data) => {
  document.querySelector('#receivedData').innerText = data.toString()
  Prism.highlightAll()
}

/* execute the selected receiver */
const execSelectedReceiver = () => {
  const receiver = getSelectedReceiver()
  receiver(window, processReceivedData)
}

/* get selected receiver from local storage */
const getSelectedReceiver = () => {
  const technique = localStorage['selectedReceiverTechnique']
  const type = localStorage['selectedReceiverType']
  return receivers[technique][type]
}

/* store selected receiver in local storage and display receiver code */
const selectReceiver = (selectedReceiver) => {
  const selectedReceiverSplitted = selectedReceiver.split(' | ')
  const technique = selectedReceiverSplitted[0]
  const type = selectedReceiverSplitted[1]
  const receiverFunction = receivers[technique][type]
  localStorage['selectedReceiverTechnique'] = technique
  localStorage['selectedReceiverType'] = type
  updateSelectedReceiverCode()
}

const updateSelectedReceiverCode = () => {
  const technique = localStorage['selectedReceiverTechnique']
  const type = localStorage['selectedReceiverType']
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

  /* postmessage */
  pm: {
    // insecure
    pmOriginMissing: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        processData(e.data)
      })
    },
    // insecure
    pmOriginIncludesLocationOrigin: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin.includes(location.origin)) {
          processData(e.data)
        }
      })
    },
    // secure
    pmOriginFixed: (receiverWindow, processData) => {
      receiverWindow.addEventListener('message', (e) => {
        if (e.origin === 'https://test.distinct-sso.com') {
          processData(e.data)
        }
      })
    }
  },

}
