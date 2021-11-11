/**
 * This background script uses the Chrome DevTools debugger to debug calls to the postMessage API.
 * We use this automated debugging technique to extract the receiver origin check from the
 * postMessage(data, receiver_origin) call.
 */

var attached_tabs = new Set(); // Set(tabId, ...)
var ids = {}; // {tabId: Set(executionContextId, ...)}

chrome.debugger.onEvent.addListener(onevent);
chrome.debugger.onDetach.addListener(ondetach);
chrome.tabs.onUpdated.addListener(onupdated);

function onupdated(tabId, changeInfo, tab) {
    console.log(`Tab #${tabId} updated`);
    console.log(`Attached tabs: ${Array.from(attached_tabs).join(",")}`);

    if (tab.url.startsWith("http") && !attached_tabs.has(tabId)) {
        console.log(`Attaching to tab #${tabId}`);
        
        let debuggeeId = {tabId: tabId};
        attached_tabs.add(tabId);
        chrome.debugger.attach(debuggeeId, "1.0", onattach.bind(this, debuggeeId));
    }
}

function onattach(debuggeeId) {
    let tabId = debuggeeId.tabId;
    console.log(`Attached to tab #${tabId}`);

    chrome.debugger.sendCommand(debuggeeId, "Debugger.enable");
    chrome.debugger.sendCommand(debuggeeId, "Runtime.enable");
    chrome.debugger.sendCommand(debuggeeId, "Debugger.setAsyncCallStackDepth", {maxDepth: 10});
}

function ondetach(debuggeeId) {
    let tabId = debuggeeId.tabId;
    console.log(`Detached from tab #${tabId}`);

    attached_tabs.delete(tabId);
}

function onevent(debuggeeId, method, params) {
    if (method == "Debugger.paused") {
        let tabId = debuggeeId.tabId;
        console.log(`Debugger paused in tab #${tabId}`);
        console.log(params.callFrames);

        // points to postMessage call in source frame
        let sourceCallFrameId = params.callFrames[1].callFrameId;

        // points to event listener in target frame
        let targetCallFrameId = params.callFrames[0].callFrameId;
        
        // Note: sourceCallFrameId must not be in tab that paused
        // If popup (tabId=2) sends postMessage to its opener (tabId=1),
        // the opener (tabId=1) pauses but sourceCallFrameId is inside the popup with (tabId=2).
        
        // If we use evaluateOnCallFrame with sourceCallFrameId and current tabId=1,
        // we get an error because the sourceCallFrame is not present in current tab.

        // We must find the correct tabId that matches the sourceCallFrameId.
        // We must use the dynamic Runtime.evaluate instead of Debugger.evaluateOnCallFrame,
        // because the popup did not pause and halt execution.
        // We need an execution context id for this.

        let sourceExecutionContextId = parseInt(sourceCallFrameId.split(".")[1]);
        let sourceTabId = undefined;
        for (let tabId in ids) {
            if (ids[tabId].has(sourceExecutionContextId)) {
                sourceTabId = tabId;
            }
        }
        
        if (!sourceTabId) {
            console.error(`Failed to find tabId for sourceExecutionContextId #${sourceExecutionContextId}`);
            console.log(ids);
            return;
        }

        let sourceDebuggeeId = {tabId: parseInt(sourceTabId)};

        extractPostMessageSource(
            sourceDebuggeeId,
            sourceExecutionContextId,
            debuggeeId,
            targetCallFrameId
        );
        
    } else if (method == "Runtime.executionContextCreated") {
        let tabId = debuggeeId.tabId;
        let executionContextId = params.context.id;
        let executionContextOrigin = params.context.origin;

        if (!executionContextOrigin.startsWith("http"))
            return;
        
        if (!(tabId in ids)) ids[tabId] = new Set();
        ids[tabId].add(executionContextId);

        console.log(
            `Execution context #${executionContextId} created in tab #${tabId} ` + 
            `with origin ${executionContextOrigin})`
        );

        chrome.debugger.sendCommand(debuggeeId, "Runtime.evaluate", {
            expression: "window.postMessage",
            contextId: executionContextId
        }, (res) => {
            if (res.result.type == "function" && res.result.objectId) {
                console.log(
                    `Found window.postMessage function ` +
                    `in execution context #${executionContextId} ` +
                    `in tab #${tabId}`
                );
            }
        });
    } else if (method == "Runtime.executionContextDestroyed") {
        let tabId = debuggeeId.tabId;
        let executionContextId = params.executionContextId;
        console.log(`Execution context #${executionContextId} destroyed in tab #${tabId}`);
        
        ids[tabId].delete(executionContextId);
    }
}

function extractPostMessageSource(
    sourceDebuggeeId,
    sourceExecutionContextId,
    targetDebuggeeId,
    targetCallFrameId
) {
    
    // Advertise source_frame
    chrome.debugger.sendCommand(sourceDebuggeeId, "Runtime.evaluate", {
        contextId: sourceExecutionContextId, // before postMessage function call on source
        expression: "window._sso._advertise()"
    }, () => {

        // Get source_hierarchy
        chrome.debugger.sendCommand(sourceDebuggeeId, "Runtime.evaluate", {
            contextId: sourceExecutionContextId, // before postMessage function call on source
            expression: "_sso._hierarchy(window)"
        }, (res) => {
            let source_hierarchy = res.result.value;

            // Get source_origin
            chrome.debugger.sendCommand(sourceDebuggeeId, "Runtime.evaluate", {
                contextId: sourceExecutionContextId, // before postMessage function call on source
                expression: "window.location.href"
            }, (res) => {
                let source_origin = res.result.value;

                console.log(
                    `PostMessage: source_hierarchy = ${source_hierarchy}, ` +
                    `source_origin = ${source_origin}`
                );
                
                // Store source_hierarchy and source_origin as vars in wrapped postMessage function.
                // We can access these vars at the start of wrapped postMessage function
                // after the debugger command.
                chrome.debugger.sendCommand(targetDebuggeeId, "Debugger.evaluateOnCallFrame", {
                    callFrameId: targetCallFrameId, // in postMessage function call on target
                    expression: `_sso._source_hierarchy = "${source_hierarchy}"; _sso._source_origin = "${source_origin}";`
                }, () => {
                    
                    // Resume execution
                    chrome.debugger.sendCommand(targetDebuggeeId, "Debugger.resume");
                });
            });
        });
    });
}

console.info("background_pm.js initialized");
