(function (global) {
    "use strict";

    const TEXTAREA_KEYS = /(description|desc|excerpt|summary|quote|answer|paragraph|text|note|terms|message)$/i;
    const IMAGE_KEYS = /(image_url|logo_url|icon_url|avatar_url|media_url|video_url|og_image|cover_image_url)$/i;
    const LABEL_OVERRIDES = { seo: "SEO", cta: "Call To Action" };

    function humanise(key) {
        if (LABEL_OVERRIDES[key]) return LABEL_OVERRIDES[key];
        return String(key).replace(/_/g, " ").replace(/\b\w/g, function (c) {
            return c.toUpperCase();
        });
    }

    function el(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function showToast(message, isError) {
        let toast = document.getElementById("toast");
        if (!toast) {
            toast = el("div");
            toast.id = "toast";
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.className = "toast" + (isError ? " toast-error" : "") + " show";
        setTimeout(function () {
            toast.classList.remove("show");
        }, 3000);
    }

    function setLoading(on) {
        const overlay = document.getElementById("loading");
        if (overlay) overlay.classList.toggle("visible", !!on);
    }

    async function uploadFile(file) {
        const form = new FormData();
        form.append("file", file);
        const response = await fetch("/admin/api/gallery/upload", { method: "POST", body: form });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Upload failed");
        return data.url;
    }

    function buildImageField(key, value) {
        const group = el("div", "form-group");
        group.appendChild(el("label", null, humanise(key)));

        const widget = el("div", "image-widget");
        const input = el("input");
        input.type = "text";
        input.value = value || "";
        input.dataset.field = key;

        const preview = el("img", "image-preview");
        if (value) {
            preview.src = value;
            preview.classList.add("visible");
        }

        const label = el("label", "upload-btn", "Upload");
        const picker = el("input");
        picker.type = "file";
        picker.style.display = "none";
        label.appendChild(picker);

        const pick = el("button", "field-pick-btn", "Gallery");
        pick.type = "button";
        pick.addEventListener("click", function () {
            openGallery(input);
        });

        input.addEventListener("input", function () {
            preview.src = input.value;
            preview.classList.toggle("visible", !!input.value);
        });

        picker.addEventListener("change", async function () {
            if (!picker.files || !picker.files[0]) return;
            setLoading(true);
            try {
                const url = await uploadFile(picker.files[0]);
                input.value = url;
                preview.src = url;
                preview.classList.add("visible");
                input.dispatchEvent(new Event("input", { bubbles: true }));
                showToast("File uploaded");
            } catch (error) {
                showToast(error.message, true);
            } finally {
                setLoading(false);
                picker.value = "";
            }
        });

        widget.appendChild(input);
        widget.appendChild(preview);
        widget.appendChild(label);
        widget.appendChild(pick);
        group.appendChild(widget);
        group.__read = function () {
            return input.value;
        };
        return group;
    }

    function buildScalarField(key, value) {
        if (IMAGE_KEYS.test(key)) return buildImageField(key, value);

        const group = el("div", "form-group");
        group.appendChild(el("label", null, humanise(key)));

        let input;
        if (typeof value === "boolean") {
            input = el("input");
            input.type = "checkbox";
            input.checked = value;
            group.__read = function () {
                return input.checked;
            };
        } else if (typeof value === "number") {
            input = el("input");
            input.type = "number";
            input.value = value;
            group.__read = function () {
                return input.value === "" ? 0 : Number(input.value);
            };
        } else if (TEXTAREA_KEYS.test(key) || String(value || "").length > 90) {
            input = el("textarea");
            input.rows = 3;
            input.value = value == null ? "" : value;
            group.__read = function () {
                return input.value;
            };
        } else {
            input = el("input");
            input.type = "text";
            input.value = value == null ? "" : value;
            group.__read = function () {
                return input.value;
            };
        }

        group.appendChild(input);
        return group;
    }

    function blankLike(sample) {
        if (Array.isArray(sample)) return [];
        if (sample && typeof sample === "object") {
            const copy = {};
            Object.keys(sample).forEach(function (k) {
                copy[k] = blankLike(sample[k]);
            });
            return copy;
        }
        if (typeof sample === "number") return 0;
        if (typeof sample === "boolean") return false;
        return "";
    }

    function buildArrayField(key, value, path) {
        const wrapper = el("div", "sub-section");
        wrapper.appendChild(el("div", "sub-section-title", humanise(key)));

        const list = el("div");
        wrapper.appendChild(list);

        const template = value.length ? value[0] : "";
        const readers = [];

        function renderItem(itemValue, index) {
            const item = el("div", "repeat-item");
            const header = el("div", "repeat-item-header");
            header.appendChild(el("span", "repeat-item-index", "#" + (index + 1)));

            const controls = el("div", "repeat-item-controls");
            const up = el("button", "btn btn-small", "↑");
            const down = el("button", "btn btn-small", "↓");
            const remove = el("button", "btn btn-small btn-danger", "Remove");
            [up, down, remove].forEach(function (b) {
                b.type = "button";
            });
            controls.appendChild(up);
            controls.appendChild(down);
            controls.appendChild(remove);
            header.appendChild(controls);
            item.appendChild(header);

            let reader;
            if (itemValue && typeof itemValue === "object" && !Array.isArray(itemValue)) {
                const body = buildObjectFields(itemValue, path + "." + index);
                item.appendChild(body);
                reader = body.__read;
            } else {
                const field = buildScalarField("value", itemValue);
                item.appendChild(field);
                reader = field.__read;
            }
            item.__read = reader;

            remove.addEventListener("click", function () {
                item.remove();
                reindex();
            });
            up.addEventListener("click", function () {
                if (item.previousElementSibling) {
                    list.insertBefore(item, item.previousElementSibling);
                    reindex();
                }
            });
            down.addEventListener("click", function () {
                if (item.nextElementSibling) {
                    list.insertBefore(item.nextElementSibling, item);
                    reindex();
                }
            });

            return item;
        }

        function reindex() {
            Array.prototype.forEach.call(list.children, function (child, i) {
                child.querySelector(".repeat-item-index").textContent = "#" + (i + 1);
            });
        }

        value.forEach(function (itemValue, index) {
            list.appendChild(renderItem(itemValue, index));
        });

        const add = el("button", "btn btn-small repeat-add", "+ Add " + humanise(key));
        add.type = "button";
        add.addEventListener("click", function () {
            list.appendChild(renderItem(blankLike(template), list.children.length));
            reindex();
        });
        wrapper.appendChild(add);

        wrapper.__read = function () {
            return Array.prototype.map.call(list.children, function (child) {
                return child.__read();
            });
        };
        return wrapper;
    }

    function buildObjectFields(obj, path) {
        const container = el("div");
        const readers = {};

        Object.keys(obj).forEach(function (key) {
            const value = obj[key];
            let node;

            if (Array.isArray(value)) {
                node = buildArrayField(key, value, path + "." + key);
            } else if (value && typeof value === "object") {
                node = el("div", "sub-section");
                node.appendChild(el("div", "sub-section-title", humanise(key)));
                const inner = buildObjectFields(value, path + "." + key);
                node.appendChild(inner);
                node.__read = inner.__read;
            } else {
                node = buildScalarField(key, value);
            }

            readers[key] = node.__read;
            container.appendChild(node);
        });

        container.__read = function () {
            const result = {};
            Object.keys(readers).forEach(function (key) {
                result[key] = readers[key]();
            });
            return result;
        };
        return container;
    }

    function renderEditor(mountId, data, onChange) {
        const mount = document.getElementById(mountId);
        mount.innerHTML = "";
        const readers = {};

        Object.keys(data).forEach(function (sectionKey) {
            const card = el("div", "section-card");
            const header = el("div", "section-header");
            header.appendChild(el("h3", "section-title", humanise(sectionKey)));
            card.appendChild(header);

            const value = data[sectionKey];
            let node;
            if (Array.isArray(value)) {
                node = buildArrayField(sectionKey, value, sectionKey);
            } else if (value && typeof value === "object") {
                node = buildObjectFields(value, sectionKey);
            } else {
                node = buildScalarField(sectionKey, value);
            }
            card.appendChild(node);
            readers[sectionKey] = node.__read;
            mount.appendChild(card);
        });

        if (typeof onChange === "function") {
            mount.addEventListener("input", onChange);
            mount.addEventListener("change", onChange);
            mount.addEventListener("click", function (event) {
                if (event.target.closest("button")) setTimeout(onChange, 0);
            });
        }

        return function read() {
            const result = {};
            Object.keys(readers).forEach(function (key) {
                result[key] = readers[key]();
            });
            return result;
        };
    }

    let galleryTarget = null;
    let galleryItems = [];

    function ensureGalleryDom() {
        if (document.getElementById("gallery-panel")) return;

        const tab = el("div", "gallery-tab", "Gallery");
        tab.id = "gallery-tab";
        tab.addEventListener("click", function () {
            const panel = document.getElementById("gallery-panel");
            if (panel && panel.classList.contains("open")) closeGallery();
            else openGallery(null);
        });
        document.body.appendChild(tab);

        const backdrop = el("div", "gallery-backdrop");
        backdrop.id = "gallery-backdrop";
        backdrop.addEventListener("click", closeGallery);

        const panel = el("div", "gallery-panel");
        panel.id = "gallery-panel";

        const header = el("div", "gallery-header");
        header.appendChild(el("h3", null, "Media Gallery"));
        const close = el("button", "btn btn-small", "Close");
        close.type = "button";
        close.addEventListener("click", closeGallery);
        header.appendChild(close);

        const tools = el("div", "gallery-tools");
        const search = el("input");
        search.type = "text";
        search.placeholder = "Search by file name...";
        search.id = "gallery-search";
        search.addEventListener("input", function () {
            renderGalleryItems(search.value);
        });

        const uploadLabel = el("label", "upload-btn", "Upload new file");
        const uploadInput = el("input");
        uploadInput.type = "file";
        uploadInput.multiple = true;
        uploadInput.style.display = "none";
        uploadInput.addEventListener("change", async function () {
            if (!uploadInput.files || !uploadInput.files.length) return;
            setLoading(true);
            try {
                for (const file of Array.from(uploadInput.files)) {
                    await uploadFile(file);
                }
                showToast("Upload complete");
                await loadGallery();
            } catch (error) {
                showToast(error.message, true);
            } finally {
                setLoading(false);
                uploadInput.value = "";
            }
        });
        uploadLabel.appendChild(uploadInput);

        tools.appendChild(search);
        tools.appendChild(uploadLabel);

        const grid = el("div", "gallery-grid");
        grid.id = "gallery-grid";

        const hint = el("div", "gallery-hint", "Click a file to insert it into the selected field.");

        panel.appendChild(header);
        panel.appendChild(tools);
        panel.appendChild(grid);
        panel.appendChild(hint);

        document.body.appendChild(backdrop);
        document.body.appendChild(panel);
    }

    function renderGalleryItems(filter) {
        const grid = document.getElementById("gallery-grid");
        if (!grid) return;
        const needle = (filter || "").toLowerCase();
        grid.innerHTML = "";

        const visible = galleryItems.filter(function (item) {
            return !needle || (item.display_name || "").toLowerCase().indexOf(needle) !== -1;
        });

        if (!visible.length) {
            grid.appendChild(el("div", "gallery-item-name", "No files found."));
            return;
        }

        visible.forEach(function (item) {
            const tile = el("div", "gallery-item");
            const name = (item.display_name || item.object_name || "").toLowerCase();
            const isImage = /\.(jpe?g|png|gif|webp|svg|bmp|ico|avif)$/.test(name);

            if (isImage) {
                const img = el("img");
                img.src = item.url;
                img.loading = "lazy";
                tile.appendChild(img);
            } else {
                tile.appendChild(el("div", "gallery-file-badge", name.split(".").pop().toUpperCase()));
            }

            tile.appendChild(el("div", "gallery-item-name", item.display_name || item.object_name));
            tile.addEventListener("click", function () {
                if (galleryTarget) {
                    galleryTarget.value = item.url;
                    galleryTarget.dispatchEvent(new Event("input", { bubbles: true }));
                    showToast("Inserted into field");
                    closeGallery();
                } else if (navigator.clipboard) {
                    navigator.clipboard.writeText(item.url);
                    showToast("URL copied");
                }
            });
            grid.appendChild(tile);
        });
    }

    async function loadGallery() {
        try {
            const response = await fetch("/admin/api/gallery?media_type=all");
            if (!response.ok) throw new Error("Could not load the gallery");
            galleryItems = await response.json();
            const search = document.getElementById("gallery-search");
            renderGalleryItems(search ? search.value : "");
        } catch (error) {
            showToast(error.message, true);
        }
    }

    function openGallery(targetInput) {
        ensureGalleryDom();
        galleryTarget = targetInput || null;
        document.getElementById("gallery-panel").classList.add("open");
        document.getElementById("gallery-backdrop").classList.add("visible");
        document.getElementById("gallery-tab").classList.add("shifted");
        loadGallery();
    }

    function closeGallery() {
        const panel = document.getElementById("gallery-panel");
        const backdrop = document.getElementById("gallery-backdrop");
        const tab = document.getElementById("gallery-tab");
        if (panel) panel.classList.remove("open");
        if (backdrop) backdrop.classList.remove("visible");
        if (tab) tab.classList.remove("shifted");
        galleryTarget = null;
    }

    const HIGHLIGHT_CLASS = "bol-preview-highlight";
    const HIGHLIGHT_STYLE_ID = "bol-preview-highlight-style";

    function stripTags(value) {
        return String(value == null ? "" : value)
            .replace(/<[^>]*>/g, " ")
            .replace(/&nbsp;/g, " ")
            .replace(/\s+/g, " ")
            .trim();
    }

    function normalise(value) {
        return stripTags(value).toLowerCase();
    }

    function findByAsset(doc, value) {
        const escaped = window.CSS && CSS.escape ? CSS.escape(value) : value.replace(/"/g, '\\"');
        const direct = doc.querySelector(
            '[src="' + escaped + '"], [href="' + escaped + '"], source[src="' + escaped + '"]'
        );
        if (direct) {
            return direct.tagName === "SOURCE" ? direct.closest("video, audio, picture") || direct.parentElement : direct;
        }
        const nodes = doc.body ? doc.body.querySelectorAll("*") : [];
        for (let i = 0; i < nodes.length; i += 1) {
            const style = nodes[i].getAttribute && nodes[i].getAttribute("style");
            if (style && style.indexOf(value) !== -1) return nodes[i];
        }
        return null;
    }

    function findByText(doc, value) {
        const target = normalise(value);
        if (!doc.body || target.length < 2) return null;

        const nodes = doc.body.querySelectorAll("*");
        let exact = null;
        let partial = null;

        for (let i = 0; i < nodes.length; i += 1) {
            const node = nodes[i];
            if (node.tagName === "SCRIPT" || node.tagName === "STYLE") continue;
            const text = normalise(node.textContent);
            if (!text) continue;

            if (text === target) {
                if (!exact || node.textContent.length <= exact.textContent.length) exact = node;
            } else if (!exact && text.indexOf(target) !== -1) {
                if (!partial || node.textContent.length < partial.textContent.length) partial = node;
            }
        }
        return exact || partial;
    }

    function clearHighlight(doc) {
        if (!doc) return;
        const previous = doc.querySelectorAll("." + HIGHLIGHT_CLASS);
        Array.prototype.forEach.call(previous, function (node) {
            node.classList.remove(HIGHLIGHT_CLASS);
        });
    }

    function ensureHighlightStyle(doc) {
        if (doc.getElementById(HIGHLIGHT_STYLE_ID)) return;
        const style = doc.createElement("style");
        style.id = HIGHLIGHT_STYLE_ID;
        style.textContent =
            "." + HIGHLIGHT_CLASS + "{outline:3px solid #3B4FD4 !important;" +
            "outline-offset:4px !important;background-color:rgba(59,79,212,0.14) !important;" +
            "border-radius:2px;animation:bolPulse 1.1s ease-out 1;scroll-margin:35vh;}" +
            "@keyframes bolPulse{0%{outline-color:rgba(59,79,212,0);}" +
            "35%{outline-color:#3B4FD4;}100%{outline-color:#3B4FD4;}}";
        (doc.head || doc.documentElement).appendChild(style);
    }

    function highlightInPreview(frame, value) {
        const doc = frame && frame.contentDocument;
        if (!doc || !doc.body) return false;

        clearHighlight(doc);

        const clean = stripTags(value);
        if (!clean) return false;

        const isAsset = /^(https?:\/\/|\/static\/|\/)/i.test(clean) && clean.indexOf(" ") === -1;
        const found = isAsset ? findByAsset(doc, clean) || findByText(doc, clean) : findByText(doc, clean);
        if (!found) return false;

        ensureHighlightStyle(doc);
        found.classList.add(HIGHLIGHT_CLASS);
        if (found.scrollIntoView) {
            found.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
        }
        return true;
    }

    function attachHighlighting(mountId, preview) {
        const mount = document.getElementById(mountId);
        if (!mount || !preview || !preview.highlight) return;

        let lastMiss = 0;

        function handle(event) {
            const field = event.target.closest("input, textarea");
            if (!field) return;
            if (field.type === "file" || field.type === "checkbox") return;

            Array.prototype.forEach.call(mount.querySelectorAll(".field-active"), function (node) {
                node.classList.remove("field-active");
            });
            const group = field.closest(".form-group") || field.closest(".repeat-item");
            if (group) group.classList.add("field-active");

            const shown = preview.highlight(field.value);
            if (!shown && field.value && Date.now() - lastMiss > 2500) {
                lastMiss = Date.now();
                showToast("Not visible on this page", false);
            }
        }

        mount.addEventListener("focusin", handle);
        mount.addEventListener("click", handle);
    }

    function renderSection(mountId, value, onChange) {
        const mount = document.getElementById(mountId);
        mount.innerHTML = "";

        let node;
        if (Array.isArray(value)) {
            node = buildArrayField("items", value, "items");
        } else if (value && typeof value === "object") {
            node = buildObjectFields(value, "");
        } else {
            node = buildScalarField("value", value);
        }
        mount.appendChild(node);

        if (typeof onChange === "function") {
            mount.addEventListener("input", onChange);
            mount.addEventListener("change", onChange);
            mount.addEventListener("click", function (event) {
                if (event.target.closest("button")) setTimeout(onChange, 0);
            });
        }
        return node.__read;
    }

    const OVERLAY_STYLE_ID = "bol-overlay-style";

    function labelForSection(key) {
        return "Edit " + humanise(key);
    }

    function injectOverlay(frame, onEdit) {
        const doc = frame && frame.contentDocument;
        if (!doc || !doc.body || doc.getElementById(OVERLAY_STYLE_ID)) return;

        const style = doc.createElement("style");
        style.id = OVERLAY_STYLE_ID;
        style.textContent =
            ".bol-sec-hover{outline:2px dashed #3B4FD4 !important;outline-offset:-2px !important;" +
            "background-color:rgba(59,79,212,0.05) !important;}" +
            ".bol-edit-btn{position:absolute;z-index:2147483000;" +
            "background:#0D1030;color:#fff;font-family:Oswald,'Segoe UI',sans-serif;" +
            "text-transform:uppercase;font-size:11px;letter-spacing:.12em;padding:7px 13px;" +
            "border:2px solid #000;cursor:pointer;line-height:1;white-space:nowrap;" +
            "opacity:.55;transition:opacity .15s ease,background .15s ease;}" +
            ".bol-edit-btn:hover,.bol-edit-btn.active{opacity:1;background:#3B4FD4;}";
        (doc.head || doc.documentElement).appendChild(style);

        const sections = Array.prototype.slice.call(doc.querySelectorAll("[data-bol-section]"));
        const pairs = [];

        sections.forEach(function (section) {
            const key = section.getAttribute("data-bol-section");
            const button = doc.createElement("div");
            button.className = "bol-edit-btn";
            button.textContent = labelForSection(key);

            button.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                onEdit(key, null);
            });

            button.addEventListener("mouseenter", function () {
                section.classList.add("bol-sec-hover");
                button.classList.add("active");
            });
            button.addEventListener("mouseleave", function () {
                section.classList.remove("bol-sec-hover");
                button.classList.remove("active");
            });

            section.addEventListener("mouseenter", function () {
                section.classList.add("bol-sec-hover");
                button.classList.add("active");
            });
            section.addEventListener("mouseleave", function () {
                section.classList.remove("bol-sec-hover");
                button.classList.remove("active");
            });

            doc.body.appendChild(button);
            pairs.push({ section: section, button: button });
        });

        function reposition() {
            const win = frame.contentWindow;
            if (!win) return;
            pairs.forEach(function (pair) {
                const rect = pair.section.getBoundingClientRect();
                if (!rect.width && !rect.height) {
                    pair.button.style.display = "none";
                    return;
                }
                pair.button.style.display = "block";
                pair.button.style.top = rect.top + win.scrollY + 10 + "px";
                pair.button.style.left =
                    Math.max(8, rect.right + win.scrollX - pair.button.offsetWidth - 10) + "px";
            });
        }

        let ticking = false;
        function scheduleReposition() {
            if (ticking) return;
            ticking = true;
            frame.contentWindow.requestAnimationFrame(function () {
                ticking = false;
                reposition();
            });
        }

        reposition();
        setTimeout(reposition, 400);
        frame.contentWindow.addEventListener("scroll", scheduleReposition);
        frame.contentWindow.addEventListener("resize", scheduleReposition);
        if (frame.contentWindow.ResizeObserver) {
            const observer = new frame.contentWindow.ResizeObserver(scheduleReposition);
            observer.observe(doc.body);
        }

        doc.addEventListener(
            "click",
            function (event) {
                const link = event.target.closest && event.target.closest("a, button");
                if (link && !link.classList.contains("bol-edit-btn")) event.preventDefault();
            },
            true
        );

        doc.addEventListener(
            "submit",
            function (event) {
                event.preventDefault();
            },
            true
        );
    }

    function setupPreview(options) {
        const panel = document.getElementById("preview-panel");
        const frame = document.getElementById("preview-iframe");
        const wrap = document.getElementById("preview-frame-wrap");
        const stale = document.getElementById("preview-stale");
        if (!panel || !frame) return { refresh: function () {} };

        const storageKey = "admin_preview_" + (options.key || "page");
        let device = localStorage.getItem(storageKey + "_device") || "desktop";
        let timer = null;

        function applyScale() {
            const width = device === "mobile" ? 390 : 1440;
            const available = wrap.clientWidth;
            const scale = Math.min(available / width, 1);
            frame.style.width = width + "px";
            frame.style.height = wrap.clientHeight / scale + "px";
            frame.style.transform = "scale(" + scale + ")";
        }

        function setDevice(next) {
            device = next;
            localStorage.setItem(storageKey + "_device", next);
            wrap.classList.toggle("mobile", next === "mobile");
            Array.prototype.forEach.call(document.querySelectorAll(".device-btn"), function (btn) {
                btn.classList.toggle("active", btn.dataset.device === next);
            });
            applyScale();
        }

        async function refresh() {
            if (stale) stale.classList.remove("visible");
            let scrollY = 0;
            try {
                scrollY = frame.contentWindow ? frame.contentWindow.scrollY : 0;
            } catch (error) {
                scrollY = 0;
            }
            try {
                const response = await fetch(options.endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(options.read()),
                });
                const html = await response.text();
                frame.addEventListener(
                    "load",
                    function () {
                        try {
                            if (frame.contentWindow && scrollY) frame.contentWindow.scrollTo(0, scrollY);
                        } catch (error) {
                            /* cross-document guard */
                        }
                        if (typeof options.onRendered === "function") options.onRendered(frame);
                    },
                    { once: true }
                );
                frame.srcdoc = html;
                applyScale();
            } catch (error) {
                showToast("Preview failed", true);
            }
        }

        function schedule() {
            if (stale) stale.classList.add("visible");
            clearTimeout(timer);
            timer = setTimeout(refresh, 600);
        }

        Array.prototype.forEach.call(document.querySelectorAll(".device-btn"), function (btn) {
            btn.addEventListener("click", function () {
                setDevice(btn.dataset.device);
            });
        });

        const toggle = document.getElementById("preview-toggle");
        if (toggle) {
            toggle.addEventListener("click", function () {
                panel.classList.toggle("collapsed");
                setTimeout(applyScale, 320);
            });
        }

        window.addEventListener("resize", applyScale);
        setDevice(device);

        return {
            refresh: refresh,
            schedule: schedule,
            highlight: function (value) {
                return highlightInPreview(frame, value);
            },
        };
    }

    function createPageEditor(opts) {
        const state = { doc: {}, section: null, read: null };
        let preview = null;

        function syncSection() {
            if (state.section && state.read && state.doc[state.section] !== undefined) {
                state.doc[state.section] = state.read();
            }
        }

        function currentDoc() {
            syncSection();
            return state.doc;
        }

        function drawer() {
            return document.getElementById("edit-drawer");
        }

        function closeDrawer() {
            syncSection();
            state.section = null;
            state.read = null;
            drawer().classList.remove("open");
        }

        function visibleSections() {
            const frame = document.getElementById("preview-iframe");
            const doc = frame && frame.contentDocument;
            if (!doc) return [];
            return Array.prototype.map.call(doc.querySelectorAll("[data-bol-section]"), function (node) {
                return node.getAttribute("data-bol-section");
            });
        }

        function openSection(key, index) {
            if (!(key in state.doc)) {
                showToast("No editable content for that area", true);
                return;
            }
            syncSection();
            state.section = key;
            document.getElementById("drawer-title").textContent = humanise(key);
            state.read = renderSection("drawer-body", state.doc[key], function () {
                if (preview) preview.schedule();
            });
            drawer().classList.add("open");

            if (index !== null && index !== undefined && index !== "") {
                const items = document.querySelectorAll("#drawer-body .repeat-item");
                const target = items[Number(index)];
                if (target) {
                    target.classList.add("field-active");
                    target.scrollIntoView({ behavior: "smooth", block: "center" });
                }
            }
        }

        function openSectionList() {
            syncSection();
            state.section = null;
            state.read = null;
            document.getElementById("drawer-title").textContent = "All sections";

            const mount = document.getElementById("drawer-body");
            mount.innerHTML = "";

            const hint = el(
                "div",
                "drawer-hint",
                "Hover any area of the page and click Edit, or pick a section below. Sections marked hidden have no visible element on this page."
            );
            mount.appendChild(hint);

            const visible = visibleSections();
            const list = el("div", "section-list");

            Object.keys(state.doc).forEach(function (key) {
                const item = el("button", "section-list-item");
                item.type = "button";
                item.appendChild(el("span", null, humanise(key)));
                item.appendChild(el("span", "section-list-tag", visible.indexOf(key) === -1 ? "hidden" : "on page"));
                item.addEventListener("click", function () {
                    openSection(key, null);
                });
                list.appendChild(item);
            });

            mount.appendChild(list);
            drawer().classList.add("open");
        }

        async function save() {
            const payload = currentDoc();
            setLoading(true);
            try {
                const response = await fetch(opts.putUrl, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Save failed");
                showToast(data.message || "Saved");
                if (preview) preview.refresh();
            } catch (error) {
                showToast(error.message, true);
            } finally {
                setLoading(false);
            }
        }

        async function load() {
            setLoading(true);
            try {
                const response = await fetch(opts.getUrl);
                if (!response.ok) throw new Error("Could not load this page");
                state.doc = await response.json();

                if (!preview) {
                    preview = setupPreview({
                        key: opts.storageKey,
                        endpoint: opts.previewUrl,
                        read: currentDoc,
                        onRendered: function (frame) {
                            injectOverlay(frame, openSection);
                        },
                    });
                }
                await preview.refresh();
            } catch (error) {
                showToast(error.message, true);
            } finally {
                setLoading(false);
            }
        }

        return {
            load: load,
            save: save,
            openSection: openSection,
            openSectionList: openSectionList,
            closeDrawer: closeDrawer,
            reload: function () {
                state.section = null;
                state.read = null;
                drawer().classList.remove("open");
                return load();
            },
        };
    }

    async function requireSession() {
        const response = await fetch("/admin/me");
        if (!response.ok) {
            window.location.href = "/admin/login";
            return null;
        }
        const user = await response.json();
        const greeting = document.getElementById("user-greeting");
        if (greeting) greeting.textContent = "// " + user.username;
        ensureGalleryDom();
        return user;
    }

    global.AdminEditor = {
        renderEditor: renderEditor,
        showToast: showToast,
        setLoading: setLoading,
        requireSession: requireSession,
        uploadFile: uploadFile,
        humanise: humanise,
        openGallery: openGallery,
        closeGallery: closeGallery,
        setupPreview: setupPreview,
        attachHighlighting: attachHighlighting,
        renderSection: renderSection,
        createPageEditor: createPageEditor,
    };
})(window);
