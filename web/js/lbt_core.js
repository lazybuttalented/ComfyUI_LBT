import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

// ─────────────────────────────────────────────
// Utility: chain a callback onto an existing method
// ─────────────────────────────────────────────
function chainCallback(object, property, callback) {
    if (!object) return;
    if (property in object && object[property]) {
        const orig = object[property];
        object[property] = function () {
            const r = orig.apply(this, arguments);
            return callback.apply(this, arguments) ?? r;
        };
    } else {
        object[property] = callback;
    }
}

// ─────────────────────────────────────────────
// Text upload widget (for LBT_LoadMultilineText)
// ─────────────────────────────────────────────
function addTextUploadWidget(nodeType, nodeData, widgetName) {
    chainCallback(nodeType.prototype, "onNodeCreated", function () {
        const node = this;
        const fileWidget = this.widgets.find((w) => w.name === widgetName);
        if (!fileWidget) return;
        if (fileWidget.element?.parentNode?.querySelector(".lbt-upload-btn")) return;

        const doUpload = async (file) => {
            try {
                const body = new FormData();
                const new_file = new File([file], file.name, {
                    type: file.type || "text/plain",
                    lastModified: file.lastModified,
                });
                body.append("image", new_file);
                body.append("overwrite", "true");
                const resp = await fetch(api.apiURL("/upload/image"), { method: "POST", body });
                if (resp.status !== 200) { alert("Upload failed: " + resp.statusText); return false; }
                const data = await resp.json();
                const filename = data.name;
                if (!fileWidget.options.values.includes(filename)) fileWidget.options.values.push(filename);
                fileWidget.value = filename;
                if (fileWidget.callback) fileWidget.callback(filename);
                return true;
            } catch (error) {
                console.error("Upload error:", error);
                alert("Upload error: " + error.message);
                return false;
            }
        };

        const fileInput = document.createElement("input");
        Object.assign(fileInput, {
            type: "file",
            accept: ".txt,text/plain",
            style: "display: none",
            onchange: async () => { if (fileInput.files.length) return await doUpload(fileInput.files[0]); },
        });

        const originalOnRemoved = this.onRemoved;
        this.onRemoved = function () {
            fileInput?.remove();
            fileWidget.element?.parentNode?.querySelector(".lbt-upload-btn")?.remove();
            if (originalOnRemoved) originalOnRemoved.apply(this, arguments);
        };

        this.onDragOver = (e) => !!e?.dataTransfer?.types?.includes?.("Files");
        this.onDragDrop = async (e) => {
            if (!this.onDragOver(e)) return;
            e.preventDefault();
            if (e.dataTransfer.files.length) return await doUpload(e.dataTransfer.files[0]);
        };

        const uploadButton = document.createElement("button");
        uploadButton.textContent = "📁 Upload txt";
        uploadButton.className = "comfy-btn lbt-upload-btn";
        uploadButton.style.cssText = "margin-left:8px;margin-top:4px;height:24px;font-size:0.8rem;padding:2px 8px;cursor:pointer;";
        uploadButton.onclick = () => fileInput.click();
        fileWidget.element.parentNode.appendChild(uploadButton);
        fileWidget.element.parentNode.insertBefore(fileInput, uploadButton);
    });
}

// ─────────────────────────────────────────────
// Boolean AND: dynamic socket inputs
// Pattern from bjornulf_custom_nodes/combine_texts.js:
//   - addInput() to grow
//   - filter node.inputs array to shrink (avoids triggering link disconnect)
// ─────────────────────────────────────────────
function setupBooleanAND(nodeType) {
    chainCallback(nodeType.prototype, "onNodeCreated", function () {
        const node = this;

        const updateInputs = (numInputs) => {
            const initialWidth = node.size[0];
            if (!node.inputs) node.inputs = [];

            // Count existing bool_N inputs
            const existing = node.inputs.filter((inp) => inp.name?.startsWith("bool_"));

            if (existing.length < numInputs) {
                // Add missing sockets
                for (let i = existing.length + 1; i <= numInputs; i++) {
                    const name = `bool_${i}`;
                    if (!node.inputs.find((inp) => inp.name === name)) {
                        node.addInput(name, "BOOLEAN");
                    }
                }
            } else if (existing.length > numInputs) {
                // Remove excess sockets by filtering the array (preserves link objects, avoids disconnect events)
                node.inputs = node.inputs.filter(
                    (inp) => !inp.name?.startsWith("bool_") || parseInt(inp.name.split("_")[1]) <= numInputs
                );
            }

            node.setSize(node.computeSize());
            node.size[0] = initialWidth;
            app.graph.setDirtyCanvas(true);
        };

        const attachHook = () => {
            const countWidget = node.widgets?.find((w) => w.name === "input_count");
            if (!countWidget) return;

            // Initial sync
            updateInputs(parseInt(countWidget.value) || 2);

            const origCallback = countWidget.callback;
            countWidget.callback = function (value) {
                if (origCallback) origCallback.call(this, value);
                updateInputs(parseInt(value) || 2);
            };
        };

        setTimeout(attachHook, 0);
    });
}

// ─────────────────────────────────────────────
// Register extension
// ─────────────────────────────────────────────
app.registerExtension({
    name: "LBT.Core",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "LBT_LoadMultilineText") {
            addTextUploadWidget(nodeType, nodeData, "file");
        }
        if (nodeData.name === "LBT_BooleanAND") {
            setupBooleanAND(nodeType);
        }
    },

    nodeCreated(node) {
        if (node.type === "LBT_LoadMultilineText") {
            const fileWidget = node.widgets?.find((w) => w.name === "file");
            if (fileWidget && !fileWidget.element?.parentNode?.querySelector(".lbt-upload-btn")) {
                addTextUploadWidget(node.constructor, node.constructor.prototype, "file");
            }
        }
    },
});
