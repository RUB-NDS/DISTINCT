/* execute the selected initiator */
const execSelectedInitiator = () => {
  const initiator = getSelectedInitiator()
  initiator(window.opener, new URL(location.href).search)
}

/* get selected initiator from local storage */
const getSelectedInitiator = () => {
  const technique = localStorage['selectedInitiatorTechnique']
  const type = localStorage['selectedInitiatorType']
  return initiators[technique][type]
}

/* store selected initiator in local storage and display initiator code */
const selectInitiator = (selectedInitiator) => {
  const selectedInitiatorSplitted = selectedInitiator.split(' | ')
  const technique = selectedInitiatorSplitted[0]
  const type = selectedInitiatorSplitted[1]
  const initiatorFunction = initiators[technique][type]
  localStorage['selectedInitiatorTechnique'] = technique
  localStorage['selectedInitiatorType'] = type
  updateSelectedInitiatorCode()
}

const updateSelectedInitiatorCode = () => {
  const technique = localStorage['selectedInitiatorTechnique']
  const type = localStorage['selectedInitiatorType']
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

  /* postmessage */
  pm: {
    // insecure
    pmWildcard: (receiverWindow, data) => {
      receiverWindow.postMessage(data, '*')
      self.close()
    },
    // insecure
    pmWindowOrigin: (receiverWindow, data) => {
      receiverWindow.postMessage(data, window.origin)
      self.close()
    },
    // secure
    pmLocationOrigin: (receiverWindow, data) => {
      receiverWindow.postMessage(data, location.origin)
      self.close()
    },
    // secure
    pmFixedOrigin: (receiverWindow, data) => {
      receiverWindow.postMessage(data, 'https://test.distinct-sso.com')
      self.close()
    }
  },

  /* js navigate */
  jsnav: {
    // insecure
    jsnavRelativeLocation: (receiverWindow, data) => {
      receiverWindow.location = `/index.html${data}`
      self.close()
    }
  }

}
