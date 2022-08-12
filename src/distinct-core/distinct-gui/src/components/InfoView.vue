<template>
  <div class="container">
    <div class="row">
      <div class="col border border-1 bg-light rounded-3">
        <h1><b><span style="font-variant: small-caps">Distinct</span></b></h1>
        <h5>is a <b>D</b>ynamic <b>I</b>n-Browser <b>S</b>ingle Sign-On <b>T</b>racer <b>I</b>nspecting <b>N</b>ovel <b>C</b>ommunication <b>T</b>echniques.</h5>
        <p><span style="font-variant: small-caps">Distinct</span> provides a fully fledged Single Sign-On security analysis framework for modern communication techniques. It was developed for the paper <a href="/paper.pdf"><i class="bi bi-file-earmark-pdf"></i></a> <i>DISTINCT: Identity Theft using In-Browser Communications in Dual-Window Single Sign-On</i>. <span style="font-variant: small-caps">Distinct's</span> dynamic analysis approach automates the (1) capturing, (2) detection, (3) visualization, (4) security analysis, and (5) exploitation of Single Sign-On flows relying on novel in-browser communication techniques.</p>
        <p>Check out the paper <a href="/paper.pdf"><i class="bi bi-file-earmark-pdf"></i></a> or the source code <a href="https://github.com/RUB-NDS/DISTINCT"><i class="bi bi-github"></i></a> to find out more.</p>
        <h5>Abstract</h5>
        <p>Single Sign-On (SSO) protocols like OAuth 2.0 and OpenID Connect 1.0 are cornerstones of modern web security, and have received much academic attention. Users sign in at a trusted Identity Provider (IdP) that subsequently allows many Service Providers (SPs) to verify the users' identities. Previous research concentrated on the standardized — called <i>textbook</i> SSO in this paper — authentication flows, which rely on HTTP redirects to transfer identity tokens between the SP and IdP. However, modern web applications like single page applications may not be able to execute the textbook flow because they lose the local state in case of any HTTP redirects. By using novel browser technologies, such as <i>postMessage</i>, developers designed and implemented SSO protcols that were neither documented nor analyzed thoroughly. We call these implementations <i>dual-window</i> SSO flows.</p>
        <p>In this paper, we provide the first comprehensive evaluation of dual-window SSO flows and their unique requirements in comparison to textbook SSO. In particular, we focus on the In-Browser Communication (InBC) used to exchange authentication tokens between SPs and IdPs in iframes and popups. We automate our analysis by developing <span style="font-variant: small-caps">Distinct</span> — a tool that dynamically analyzes the in-browser JavaScript code executing as part of the SSO flow. <span style="font-variant: small-caps">Distinct</span> translates the flow into a sequence diagram depicting all communicating entities and their exchanged messages, highlights insecure communication channels, and quantifies novel threats in dual-window SSO flows. We found that 56% of the SPs in the Tranco top 1k list support dual-window SSO. Surprisingly, 28% of them implemented dual-window SSO without using official SDKs, leading to identity theft and XSS in 31% of these self-implemented SPs.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InfoView'
}
</script>

<style>

</style>
