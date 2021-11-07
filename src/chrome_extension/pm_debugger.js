var attached_tabs = new Set();
var ids = {}; // {tabId: Set(executionContextId, ...)}

chrome.debugger.onEvent.addListener(onevent);
chrome.debugger.onDetach.addListener(ondetach);

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
	console.log(`[PM Callalyzer] Tab #${tabId} updated`);
	console.log(`[PM Callalyzer] Currently attached tabs: ${attached_tabs.size !== 0 ? Array.from(attached_tabs).join(",") : "empty"}`);
	if (tab.url.startsWith("http") && !attached_tabs.has(tabId)) {
		let debuggeeId = {tabId: tabId};
		attached_tabs.add(tabId);
		console.log(`[PM Callalyzer] Attaching to tab #${tabId}`);
		chrome.debugger.attach(debuggeeId, "1.0", onattach.bind(this, debuggeeId));
	}
});

function onattach(debuggeeId) {
	let tabId = debuggeeId.tabId;
	console.log(`[PM Callalyzer] Attached to tab #${tabId}`);
	chrome.debugger.sendCommand(debuggeeId, "Debugger.enable");
	chrome.debugger.sendCommand(debuggeeId, "Runtime.enable");
	chrome.debugger.sendCommand(debuggeeId, "Debugger.setAsyncCallStackDepth", {maxDepth: 10});
}

function ondetach(debuggeeId) {
	let tabId = debuggeeId.tabId;
	attached_tabs.delete(tabId);
	console.log(`[PM Callalyzer] Detached from tab #${tabId}`);
	//chrome.debugger.sendCommand(debuggeeId, "Debugger.disable");
}

function onevent(debuggeeId, method, params) {
	if (method == "Debugger.paused") {
		let tabId = debuggeeId.tabId;
		
		console.log(`[PM Callalyzer] Debugger paused in tab #${tabId}`);
		console.log(`[PM Callalyzer] Call frames:`);
		console.log(params.callFrames);

		let sourceCallFrameId = params.callFrames[1].callFrameId; // points to postMessage call in source frame
		let targetCallFrameId = params.callFrames[0].callFrameId; // points to event listener in target frame
		
		// Note: sourceCallFrameId must not be in tab that paused
		// I.e., if popup (tabId=2) sends postMessage to its opener (tabId=1), the opener (tabId=1) pauses
		// but the sourceCallFrameId is inside the popup with (tabId=2).
		// If we use evaluateOnCallFrame with sourceCallFrameId and current tabId (=1)
		// we get an error, because sourceCallFrame is not present in current tab.

		// Solution: We must find the correct tabId that matches the sourceCallFrameId
		// Also, we must use dynamic Runtime.evaluate instead of Debugger.evaluateOnCallFrame
		// because the popup did not pause and halt execution. Therefore, we need an execution context id.

		let sourceExecutionContextId = parseInt(sourceCallFrameId.split(".")[1]);
		let sourceTabId = undefined;
		for (let tabId in ids) {
			if (ids[tabId].has(sourceExecutionContextId)) {
				sourceTabId = tabId;
			}
		}
		
		if (!sourceTabId) {
			console.error(`[PM Callalyzer] Failed to find tabId for sourceExecutionContextId #${sourceExecutionContextId}`);
			console.log(`[PM Callalyzer] IDs:`);
			console.log(ids);
			return;
		}

		let sourceDebuggeeId = {tabId: parseInt(sourceTabId)};

		// console.log(`[PM Callalyzer] Testing window.location.href in tab #${sourceTabId} and context id #${sourceExecutionContextId}`);
		// chrome.debugger.sendCommand(sourceDebuggeeId, "Runtime.evaluate", {
		// 	expression: "window.location.href",
		// 	contextId: sourceExecutionContextId
		// }, (res) => {
		// 	console.log(res);
		// });

		extractPostMessageSource(sourceDebuggeeId, sourceExecutionContextId, debuggeeId, targetCallFrameId);
		
	} else if (method == "Runtime.executionContextCreated") {
		let tabId = debuggeeId.tabId;
		let executionContextId = params.context.id;
		//let executionContextUniqueId = params.context.uniqueId;
		let executionContextOrigin = params.context.origin;

		if (!executionContextOrigin.startsWith("http"))
			return;
		
		if (!(tabId in ids)) ids[tabId] = new Set();
		ids[tabId].add(executionContextId);

		console.log(`[PM Callalyzer] Execution context #${executionContextId} created in tab #${tabId} (Origin: ${executionContextOrigin})`);

		chrome.debugger.sendCommand(debuggeeId, "Runtime.evaluate", {
			expression: "window.postMessage",
			contextId: executionContextId
		}, (res) => {
			if (res.result.type == "function" && res.result.objectId) {
				console.log(`[PM Callalyzer] Found window.postMessage function with objectId #${res.result.objectId} in execution context #${executionContextId} in tab #${tabId}`);
			}
		});
	} else if (method == "Runtime.executionContextDestroyed") {
		let tabId = debuggeeId.tabId;
		let executionContextId = params.executionContextId;
		ids[tabId].delete(executionContextId);
		console.log(`[PM Callalyzer] Execution context #${executionContextId} destroyed in tab #${tabId}`);
	}
}

function extractPostMessageSource(sourceDebuggeeId, sourceExecutionContextId, targetDebuggeeId, targetCallFrameId) {
	
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

				console.log(`[PM Callalyzer] Source: source_hierarchy = ${source_hierarchy}, source_origin = ${source_origin}`);
				
				// Store source_hierarchy and source_origin as variables in wrapped postMessage function
				// We can access these variables at the start of our wrapped window.postMessage function
				// after the debugger command
				chrome.debugger.sendCommand(targetDebuggeeId, "Debugger.evaluateOnCallFrame", {
					callFrameId: targetCallFrameId, // in postMessage function call on target
					expression: `var source_hierarchy = "${source_hierarchy}"; var source_origin = "${source_origin}";`
				}, () => {
					
					// Resume execution
					chrome.debugger.sendCommand(targetDebuggeeId, "Debugger.resume");
				});
			});
		});
	});
}
