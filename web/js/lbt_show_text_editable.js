/**
 * LBT Show Text Editable
 *
 * Node layout (widgets in order):
 *   [0]  text_display  — read-only preview, mirrors upstream `text`, not serialised
 *   [1]  text_edit     — editable multiline box, serialised as widgets_values[1]
 *
 * Behaviour:
 *   • On every execution (onExecuted):
 *       - Always refresh text_display with the new upstream value.
 *       - Overwrite text_edit ONLY when the new upstream value differs from
 *         the last upstream value seen (stored in node.__lbt_lastUpstream).
 *         This lets the user freely edit text_edit between runs that reuse
 *         the same upstream text.
 *   • On configure / load (onConfigure):
 *       - Restore text_display from widgets_values[0] (last upstream text).
 *       - Restore text_edit  from widgets_values[1] (last edited value).
 *
 * widgets_values persisted by Python backend:
 *   [0] = last upstream text
 *   [1] = text_edit content
 */

import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
    name: "LBT.ShowTextEditable",

    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        if (nodeData.name !== "LBT_ShowTextEditable") return;

        // ── Helper: create or reuse the two fixed widgets ─────────────────
        function ensureWidgets(node) {
            // We always want exactly 2 widgets:
            //   index 0 → text_display (read-only)
            //   index 1 → text_edit    (editable)
            // They may already exist after configure(); only create if missing.

            if (!node.widgets) node.widgets = [];

            // ── text_display (index 0) ────────────────────────────────────
            if (!node.__lbt_display) {
                const w = ComfyWidgets["STRING"](
                    node,
                    "text_display",
                    ["STRING", { multiline: true, default: "" }],
                    app
                ).widget;
                w.inputEl.readOnly    = true;
                w.inputEl.style.opacity = "0.55";
                w.inputEl.style.cursor  = "default";
                w.inputEl.title = "Read-only preview of the upstream text input";
                // Prevent the user accidentally typing in the read-only box
                w.inputEl.addEventListener("keydown", (e) => e.preventDefault());
                node.__lbt_display = w;
            }

            // ── text_edit (index 1) ───────────────────────────────────────
            if (!node.__lbt_edit) {
                const w = ComfyWidgets["STRING"](
                    node,
                    "text_edit",
                    ["STRING", { multiline: true, default: "" }],
                    app
                ).widget;
                w.inputEl.placeholder = "Edit text here…";
                node.__lbt_edit = w;
            }
        }

        // ── Helper: trigger canvas resize after widget changes ─────────────
        function refreshSize(node) {
            requestAnimationFrame(() => {
                const sz = node.computeSize();
                if (sz[0] < node.size[0]) sz[0] = node.size[0];
                if (sz[1] < node.size[1]) sz[1] = node.size[1];
                node.onResize?.(sz);
                app.graph.setDirtyCanvas(true, false);
            });
        }

        // ── onExecuted: called every time the backend finishes ─────────────
        const _onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            _onExecuted?.apply(this, arguments);

            const newText = Array.isArray(message.text)
                ? message.text[0]
                : message.text;

            ensureWidgets(this);

            // Always update the read-only preview
            this.__lbt_display.value = newText;

            // Overwrite text_edit ONLY if upstream text has changed
            const lastUpstream = this.__lbt_lastUpstream ?? null;
            if (lastUpstream === null || lastUpstream !== newText) {
                this.__lbt_edit.value = newText;
            }
            // Record the latest upstream value for next comparison
            this.__lbt_lastUpstream = newText;

            refreshSize(this);
        };

        // ── configure: intercept before widgets are reset by new frontend ──
        const VALUES = Symbol("lbt_ste_values");

        const _configure = nodeType.prototype.configure;
        nodeType.prototype.configure = function () {
            // Stash widget values before the base configure wipes them
            this[VALUES] = arguments[0]?.widgets_values;
            return _configure?.apply(this, arguments);
        };

        // ── onConfigure: restore widgets from saved values ─────────────────
        const _onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            _onConfigure?.apply(this, arguments);

            const wv = this[VALUES];
            if (!wv || wv.length === 0) return;

            requestAnimationFrame(() => {
                ensureWidgets(this);

                // widgets_values[0] = last upstream text (for display + change-detection)
                // widgets_values[1] = text_edit value    (user-edited content)
                const upstream = wv[0] ?? "";
                const edited   = wv[1] ?? "";

                this.__lbt_display.value    = upstream;
                this.__lbt_edit.value       = edited;
                this.__lbt_lastUpstream     = upstream;

                refreshSize(this);
            });
        };

        // ── getExtraMenuOptions: nothing extra needed, but hook available ──
    },
});
