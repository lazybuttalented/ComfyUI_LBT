/**
 * LBT Show Text Editable
 *
 * Value pipeline:
 *   upstream text  →  [backend]  →  ui.text
 *                                      ↓
 *                              text_display (read-only, index 0)
 *
 *   user edits visible edit box
 *       ↓  (on every input event + before prompt queued)
 *   hidden auto widget "text_edit" (index 1, invisible)
 *       ↓  (serialised by ComfyUI into prompt)
 *   backend receives text_edit as normal function argument
 *       ↓
 *   text_edited output = text_edit value ✓
 *
 * Widget layout on the node:
 *   [0]  text_display  — read-only preview   (custom, NOT serialised via hidden trick)
 *   [1]  text_edit     — AUTO widget, hidden  (height=0, invisible; holds the value)
 *   [2]  text_edit_vis — visible editable box (custom, syncs value into [1])
 *
 * widgets_values on save/load (managed by ComfyUI naturally):
 *   [0] = text_edit hidden widget value  (= user-edited content)
 *   [1] = text_display value             (= last upstream text, for change detection)
 *
 * NOTE: text_display is added BEFORE the auto widget, but ComfyUI only serialises
 * widgets that exist at node definition time. We use serializeValue override on
 * text_display to make it a no-op (return undefined / skip), and rely on the hidden
 * auto widget for actual serialisation.
 */

import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
    name: "LBT.ShowTextEditable",

    async nodeCreated(node) {
        if (node.comfyClass !== "LBT_ShowTextEditable") return;

        // ── Locate the auto-generated text_edit widget (ComfyUI created it) ──
        // It is the first (and only) widget at this point.
        const autoWidget = node.widgets?.find(w => w.name === "text_edit");
        if (!autoWidget) return;

        // ── Hide the auto widget completely ───────────────────────────────────
        // Setting computeSize to return [0,0] removes it from visual layout.
        autoWidget.computeSize = () => [0, 0];
        autoWidget.type = "converted-widget"; // prevents normal rendering
        // Also hide the underlying DOM element if any
        if (autoWidget.inputEl) {
            autoWidget.inputEl.style.display = "none";
        }

        // ── Insert text_display BEFORE the auto widget ───────────────────────
        const displayWidget = ComfyWidgets["STRING"](
            node,
            "text_display",
            ["STRING", { multiline: true, default: "" }],
            app
        ).widget;
        displayWidget.inputEl.readOnly = true;
        displayWidget.inputEl.style.opacity = "0.55";
        displayWidget.inputEl.style.cursor = "default";
        displayWidget.inputEl.title = "Read-only preview of the upstream text";
        displayWidget.inputEl.addEventListener("keydown", (e) => e.preventDefault());
        // Move it to index 0 (before the auto widget)
        const idx = node.widgets.indexOf(displayWidget);
        const autoIdx = node.widgets.indexOf(autoWidget);
        if (idx > 0) {
            node.widgets.splice(idx, 1);
            node.widgets.splice(0, 0, displayWidget);
        }

        // ── Create visible editable box AFTER the auto widget ────────────────
        const editWidget = ComfyWidgets["STRING"](
            node,
            "text_edit_vis",
            ["STRING", { multiline: true, default: "" }],
            app
        ).widget;
        editWidget.inputEl.placeholder = "Edit text here…";

        // Sync visible box → hidden auto widget on every keystroke
        editWidget.inputEl.addEventListener("input", () => {
            autoWidget.value = editWidget.value;
        });

        // Also sync on blur (safety net)
        editWidget.inputEl.addEventListener("change", () => {
            autoWidget.value = editWidget.value;
        });

        // ── Add reset button via node.addWidget (ComfyUI native API) ──────────
        node.addWidget(
            "button",
            "↺ Reset to input",
            null,
            () => {
                // node is a const in the outer closure — do NOT use `this` here
                const upstream = node.__lbt_display?.value ?? "";
                node.__lbt_edit.value = upstream;
                node.__lbt_auto.value = upstream;
            }
        );

        // Store refs
        node.__lbt_display = displayWidget;
        node.__lbt_edit    = editWidget;
        node.__lbt_auto    = autoWidget;

        // ── onExecuted: refresh display, conditionally overwrite edit box ─────
        const _onExecuted = node.onExecuted?.bind(node);
        node.onExecuted = function (message) {
            _onExecuted?.(message);

            const newText = Array.isArray(message?.text)
                ? message.text[0]
                : (message?.text ?? "");

            // Always refresh the read-only preview
            this.__lbt_display.value = newText;

            // Overwrite the visible edit box ONLY if upstream text changed
            const last = this.__lbt_lastUpstream ?? null;
            if (last === null || last !== newText) {
                this.__lbt_edit.value = newText;
                this.__lbt_auto.value = newText;  // keep hidden in sync too
            }
            this.__lbt_lastUpstream = newText;

            this._refreshSize();
        };

        // ── onConfigure: restore from saved widgets_values ────────────────────
        const _onConfigure = node.onConfigure?.bind(node);
        node.onConfigure = function (data) {
            _onConfigure?.(data);

            const wv = data?.widgets_values;
            if (!wv || wv.length === 0) return;

            requestAnimationFrame(() => {
                // widgets_values[0] = text_edit (hidden auto widget value = user-edited)
                // widgets_values[1] = text_display value (last upstream)
                const editedVal  = wv[0] ?? "";
                const displayVal = wv[1] ?? "";

                if (this.__lbt_auto)    this.__lbt_auto.value    = editedVal;
                if (this.__lbt_edit)    this.__lbt_edit.value    = editedVal;
                if (this.__lbt_display) this.__lbt_display.value = displayVal;
                this.__lbt_lastUpstream = displayVal;

                this._refreshSize();
            });
        };

        // ── Helper ────────────────────────────────────────────────────────────
        node._refreshSize = function () {
            requestAnimationFrame(() => {
                const sz = this.computeSize();
                if (sz[0] < this.size[0]) sz[0] = this.size[0];
                if (sz[1] < this.size[1]) sz[1] = this.size[1];
                this.onResize?.(sz);
                app.graph.setDirtyCanvas(true, false);
            });
        };
    },
});
