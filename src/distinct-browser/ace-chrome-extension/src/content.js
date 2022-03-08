const content = (config) => {

  const sleep = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  window.addEventListener("load", async () => {

    // give the page 1 more second to be safe that everything is ready
    await sleep(1000);

    /* GOOGLE LOGIN */
    if (
      location.host === "accounts.google.com"
      && location.pathname.endsWith("/identifier")
    ) {
      let emailField = document.querySelector("#identifierId");
      emailField.value = config.googleUsername;
      emailField.dispatchEvent(new Event("input"));
      await sleep(200);

      let continueButton = document.querySelectorAll("button[jsaction]:not([data-third-party-email])")[0];
      continueButton.click();
      await sleep(2000);

      let passwordField = document.querySelector("input[name='password']");
      passwordField.value = config.googlePassword;
      passwordField.dispatchEvent(new Event("input"));
      await sleep(200);

      let submitButton = document.querySelectorAll("button[jsaction]:not([data-third-party-email])")[0];
      submitButton.click();
      await sleep(2000);
    }

    /* GOOGLE CONSENT */
    if (
      location.host === "accounts.google.com"
      && location.pathname.endsWith("/oauthchooseaccount")
    ) {
      document.getElementsByTagName("li")[0].childNodes[0].childNodes[0].click();
    }

    /* GOOGLE CONSENT (SiwG) */
    if (
      location.host === "accounts.google.com"
      && location.pathname === "/gsi/select"
    ) {
      let continueButton = document.querySelectorAll("[role=link]")[0];
      if (continueButton) {
        continueButton.click();
        await sleep(1000);
      }
      document.getElementById("confirm_yes").click();
    }

    /* FACEBOOK LOGIN */
    if (
      location.host.endsWith("facebook.com")
      && location.pathname.endsWith("/login.php")
    ) {
      let emailField = document.querySelector("#email");
      let passField = document.querySelector("#pass");

      emailField.value = config.facebookUsername;
      emailField.dispatchEvent(new Event("input"));
      await sleep(200);

      passField.value = config.facebookPassword;
      passField.dispatchEvent(new Event("input"));
      await sleep(200);

      let loginButton = document.querySelector("#loginbutton");
      loginButton.click();
    }

    /* FACEBOOK CONSENT */
    if (
      location.host.endsWith("facebook.com")
      && location.pathname.includes("/dialog/oauth")
    ) {
      let confirmButton = document.querySelector("button[name='__CONFIRM__']");
      let grantButton = document.querySelectorAll("[aria-label]")[0];
      let cancelButton = document.querySelectorAll("[aria-label]")[1];

      if (confirmButton) {
        confirmButton.click();
      } else if (grantButton) {
        grantButton.click();
      }

    }

    /* APPLE LOGIN & CONSENT */
    if (
      location.host === "appleid.apple.com"
      && location.pathname.includes("/auth/authorize")
    ) {
      // bypass 2fa
      document.cookie = `${config.apple2FA}; Secure; path=/; domain=.appleid.apple.com;`;

      // fill out username and password
      let appleIDField = document.querySelector("#account_name_text_field");
      appleIDField.value = config.appleUsername;
      appleIDField.dispatchEvent(new Event("input"));
      await sleep(200);

      document.querySelector("#sign-in").click();
      await sleep(2000);

      let passwordField = document.querySelector("#password_text_field");
      passwordField.value = config.applePassword;
      passwordField.dispatchEvent(new Event("input"));
      await sleep(200);

      document.querySelector("#sign-in").click();
      await sleep(2000);

      // click consent button
      let consentButton = document.querySelectorAll("button.nav-action")[0];
      if (!consentButton) {
        alert("2FA");
      } else {
        consentButton.click();
      }
    }
  });

  console.info("ace extension initialized");
}

const initContent = (content, config) => {
  const contentText = `(` + content.toString() + `)(${JSON.stringify(config)})`;
  const contentScript = document.createElement("script");
  contentScript.appendChild(document.createTextNode(contentText));
  document.documentElement.appendChild(contentScript);
}

let configURL = chrome.runtime.getURL("config/config.json");
fetch(configURL).then((config) => config.json()).then((config) => {
  initContent(content, config);
});
