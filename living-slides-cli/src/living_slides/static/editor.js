(function() {
    const editor = grapesjs.init({
        container: '#gjs',
        fromElement: false,
        storageManager: false,
        plugins: [],
        canvas: { styles: [], scripts: [] },
        panels: { defaults: [] },
        undoManager: { maximumStackLength: 500, trackSelection: false },
    });

    // ------------------------------------------------------------------
    // Load HTML from server on init, then set up auto-reload on file change
    // ------------------------------------------------------------------
    let lastKnownMtime = null;

    function syncVersion() {
        return fetch('/api/version')
            .then(function(r) { return r.json(); })
            .then(function(v) { lastKnownMtime = v.mtime; })
            .catch(function() {});
    }

    fetch('/api/load')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.html) {
                editor.setComponents(data.html);
                if (data.css) editor.setStyle(data.css);
            }
            return syncVersion();
        })
        .catch(function(err) { console.error('Failed to load HTML:', err); });

    // Auto-reload: if the file on disk changes (e.g. Claude edited it via
    // chat), pull the new HTML and re-render the canvas, preserving the
    // currently-selected element's data-oid when possible.
    function reloadCanvasFromDisk() {
        // Don't interrupt an active drag/resize
        if (typeof dragState !== 'undefined' && dragState) return;
        if (typeof blockDragState !== 'undefined' && blockDragState) return;

        // Remember what's selected so we can re-select after reload
        const sel = editor.getSelected();
        let prevOid = null;
        try {
            const el = sel && sel.getEl ? sel.getEl() : null;
            if (el && el.getAttribute) prevOid = el.getAttribute('data-oid');
        } catch (e) {}

        fetch('/api/load')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.html) return;
                editor.setComponents(data.html);
                if (data.css) editor.setStyle(data.css);
                // Re-select previous element if still present
                if (prevOid) {
                    setTimeout(function() {
                        try {
                            const wrapper = editor.DomComponents.getWrapper();
                            const matches = wrapper
                                ? wrapper.find('[data-oid="' + prevOid + '"]')
                                : [];
                            if (matches && matches.length) editor.select(matches[0]);
                        } catch (e) {}
                    }, 120);
                }
                showSaveToast('🔄 AI 更新了文档，已自动刷新', '#58a6ff');
            })
            .catch(function() {});
    }

    function checkForFileChange() {
        fetch('/api/version')
            .then(function(r) { return r.json(); })
            .then(function(v) {
                if (lastKnownMtime === null) {
                    lastKnownMtime = v.mtime;
                    return;
                }
                // 0.5s tolerance in case filesystem time resolution drifts
                if (v.mtime > lastKnownMtime + 0.5) {
                    lastKnownMtime = v.mtime;
                    reloadCanvasFromDisk();
                }
            })
            .catch(function() {});
    }
    setInterval(checkForFileChange, 2000);

    // ------------------------------------------------------------------
    // Save command + Ctrl+S + floating save button
    // ------------------------------------------------------------------
    editor.Commands.add('save-html', {
        run: function(editor) {
            const html = editor.getHtml();
            const css = editor.getCss();
            fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ html, css }),
            })
            .then(r => r.json())
            .then(data => {
                const status = document.getElementById('save-status');
                if (data.ok) {
                    status.textContent = 'Saved! ' + (data.summary || '');
                    status.style.background = '#238636';
                } else {
                    status.textContent = 'Save failed: ' + (data.error || 'unknown');
                    status.style.background = '#da3633';
                }
                status.style.display = 'block';
                setTimeout(() => { status.style.display = 'none'; }, 3000);
                // Refresh baseline mtime so our own save doesn't trigger reload
                if (data.ok) syncVersion();
            })
            .catch(err => console.error('Save failed:', err));
        },
    });

    function handleSaveShortcut(e) {
        if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
            e.preventDefault();
            e.stopPropagation();
            editor.runCommand('save-html');
        }
    }
    document.addEventListener('keydown', handleSaveShortcut);

    // Ctrl+Z → GrapesJS UndoManager (editor-level undo for local edits incl.
    // deletes, drags, text edits). Must be bound explicitly because our
    // `panels: { defaults: [] }` disables the default keymap registration.
    function handleUndoShortcut(e) {
        const isZ = (e.key === 'z' || e.key === 'Z');
        if ((e.ctrlKey || e.metaKey) && !e.shiftKey && isZ) {
            e.preventDefault();
            e.stopPropagation();
            try {
                const um = editor.UndoManager;
                if (um && um.hasUndo && um.hasUndo()) {
                    um.undo();
                    const status = document.getElementById('save-status');
                    if (status) {
                        status.textContent = '↶ Undo';
                        status.style.background = '#58a6ff';
                        status.style.display = 'block';
                        setTimeout(function() { status.style.display = 'none'; }, 1200);
                    }
                } else {
                    const status = document.getElementById('save-status');
                    if (status) {
                        status.textContent = '没有可撤销的本地编辑 · 试试 Ctrl+Shift+Z 撤文件级变更';
                        status.style.background = '#d29922';
                        status.style.display = 'block';
                        setTimeout(function() { status.style.display = 'none'; }, 2500);
                    }
                }
            } catch (err) { console.error('undo failed:', err); }
        }
    }
    // Ctrl+Y → GrapesJS redo (paired with Ctrl+Z)
    function handleRedoShortcut(e) {
        const isY = (e.key === 'y' || e.key === 'Y');
        if ((e.ctrlKey || e.metaKey) && !e.shiftKey && isY) {
            e.preventDefault();
            e.stopPropagation();
            try {
                const um = editor.UndoManager;
                if (um && um.hasRedo && um.hasRedo()) um.redo();
            } catch (err) {}
        }
    }
    document.addEventListener('keydown', handleUndoShortcut);
    document.addEventListener('keydown', handleRedoShortcut);

    // Ctrl+Shift+Z → file-level revert (undoes AI edits or prior saves)
    function handleRevertShortcut(e) {
        const isZ = (e.key === 'z' || e.key === 'Z');
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && isZ) {
            e.preventDefault();
            e.stopPropagation();
            fetch('/api/revert', { method: 'POST' })
                .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, data: d }; }); })
                .then(function(res) {
                    const status = document.getElementById('save-status');
                    if (res.ok && res.data.ok) {
                        status.textContent = '↶ 撤销到上一个快照 (剩余 ' + res.data.remaining + ' 步)';
                        status.style.background = '#8250df';
                    } else {
                        status.textContent = '无可撤销的历史';
                        status.style.background = '#d29922';
                    }
                    status.style.display = 'block';
                    setTimeout(function() { status.style.display = 'none'; }, 2500);
                })
                .catch(function(err) { console.error('Revert failed:', err); });
        }
    }
    document.addEventListener('keydown', handleRevertShortcut);
    editor.on('load', function() {
        try {
            const frameEl = editor.Canvas.getFrameEl();
            if (frameEl && frameEl.contentDocument) {
                frameEl.contentDocument.addEventListener('keydown', handleSaveShortcut);
                frameEl.contentDocument.addEventListener('keydown', handleUndoShortcut);
                frameEl.contentDocument.addEventListener('keydown', handleRedoShortcut);
                frameEl.contentDocument.addEventListener('keydown', handleRevertShortcut);
            }
        } catch (err) {}
    });
    // ======================================================================
    // Top toolbar (PowerPoint-style) — wire up all buttons
    // ======================================================================

    function getSelEl() {
        const sel = editor.getSelected();
        return sel ? sel.getEl() : null;
    }

    function applyStyleToSelected(prop, value) {
        const sel = editor.getSelected();
        if (!sel) return;
        const style = {};
        style[prop] = value;
        sel.addStyle(style);
    }

    function toggleStyleOnSelected(prop, onVal, offVal) {
        const sel = editor.getSelected();
        if (!sel) return;
        const current = (sel.getStyle() || {})[prop];
        const style = {};
        style[prop] = (current === onVal) ? offVal : onVal;
        sel.addStyle(style);
    }

    // Save button
    const saveBtn = document.getElementById('tb-save');
    if (saveBtn) saveBtn.addEventListener('click', function() { editor.runCommand('save-html'); });

    // Font family
    const fontFamilySel = document.getElementById('tb-font-family');
    if (fontFamilySel) {
        fontFamilySel.addEventListener('change', function(e) {
            if (e.target.value) applyStyleToSelected('font-family', e.target.value);
        });
    }

    // Font size
    const fontSizeSel = document.getElementById('tb-font-size');
    if (fontSizeSel) {
        fontSizeSel.addEventListener('change', function(e) {
            if (e.target.value) applyStyleToSelected('font-size', e.target.value);
        });
    }

    // B / I / U
    document.getElementById('tb-bold').addEventListener('click', function() {
        toggleStyleOnSelected('font-weight', '700', '400');
    });
    document.getElementById('tb-italic').addEventListener('click', function() {
        toggleStyleOnSelected('font-style', 'italic', 'normal');
    });
    document.getElementById('tb-underline').addEventListener('click', function() {
        toggleStyleOnSelected('text-decoration', 'underline', 'none');
    });

    // Colors
    document.getElementById('tb-color-fg').addEventListener('input', function(e) {
        applyStyleToSelected('color', e.target.value);
    });
    document.getElementById('tb-color-bg').addEventListener('input', function(e) {
        applyStyleToSelected('background-color', e.target.value);
    });

    // Alignment
    document.getElementById('tb-align-left').addEventListener('click', function() {
        applyStyleToSelected('text-align', 'left');
    });
    document.getElementById('tb-align-center').addEventListener('click', function() {
        applyStyleToSelected('text-align', 'center');
    });
    document.getElementById('tb-align-right').addEventListener('click', function() {
        applyStyleToSelected('text-align', 'right');
    });

    // Insert helpers — place new component after the currently selected one,
    // or append to its nearest .body-area if the selection has no siblings.
    function randomOid(prefix) {
        return prefix + '-' + Math.random().toString(36).slice(2, 8);
    }
    function insertAfterSelected(html) {
        const sel = editor.getSelected();
        if (!sel) {
            alert('请先选中一个元素作为插入位置参考（工具会在它后面插入）');
            return;
        }
        const parent = sel.parent();
        if (!parent) {
            alert('无法确定插入位置');
            return;
        }
        const idx = sel.index();
        parent.append(html, { at: idx + 1 });
    }

    // Insert: single block
    document.getElementById('tb-ins-block').addEventListener('click', function() {
        const oid = randomOid('new');
        insertAfterSelected(
            '<div class="block" data-oid="' + oid + '-block">' +
            '<div class="block-title" data-oid="' + oid + '-title">新块标题</div>' +
            '<div class="item-text" data-oid="' + oid + '-text">在这里输入内容…</div>' +
            '</div>'
        );
    });

    // Insert: two-col block
    document.getElementById('tb-ins-two').addEventListener('click', function() {
        const oid = randomOid('new');
        insertAfterSelected(
            '<div class="two-col" data-oid="' + oid + '-two">' +
            '<div class="block"><div class="block-title" data-oid="' + oid + '-lt">左标题</div>' +
            '<div class="item-text" data-oid="' + oid + '-lx">左内容</div></div>' +
            '<div class="block"><div class="block-title" data-oid="' + oid + '-rt">右标题</div>' +
            '<div class="item-text" data-oid="' + oid + '-rx">右内容</div></div>' +
            '</div>'
        );
    });

    // Insert: three-col block
    document.getElementById('tb-ins-three').addEventListener('click', function() {
        const oid = randomOid('new');
        insertAfterSelected(
            '<div class="three-col" data-oid="' + oid + '-three">' +
            '<div class="block"><div class="block-title" data-oid="' + oid + '-1t">一</div>' +
            '<div class="item-text" data-oid="' + oid + '-1x">内容</div></div>' +
            '<div class="block"><div class="block-title" data-oid="' + oid + '-2t">二</div>' +
            '<div class="item-text" data-oid="' + oid + '-2x">内容</div></div>' +
            '<div class="block"><div class="block-title" data-oid="' + oid + '-3t">三</div>' +
            '<div class="item-text" data-oid="' + oid + '-3x">内容</div></div>' +
            '</div>'
        );
    });

    // Insert: KPI row
    document.getElementById('tb-ins-kpi').addEventListener('click', function() {
        const oid = randomOid('new');
        insertAfterSelected(
            '<div class="kpi-row" data-oid="' + oid + '-kpi">' +
            '<div class="kpi"><div class="num" data-oid="' + oid + '-k1n">100</div><div class="lab" data-oid="' + oid + '-k1l">指标一</div></div>' +
            '<div class="kpi"><div class="num" data-oid="' + oid + '-k2n">200</div><div class="lab" data-oid="' + oid + '-k2l">指标二</div></div>' +
            '<div class="kpi"><div class="num" data-oid="' + oid + '-k3n">300</div><div class="lab" data-oid="' + oid + '-k3l">指标三</div></div>' +
            '<div class="kpi"><div class="num" data-oid="' + oid + '-k4n">400</div><div class="lab" data-oid="' + oid + '-k4l">指标四</div></div>' +
            '</div>'
        );
    });

    // Insert: tag / item
    document.getElementById('tb-ins-item').addEventListener('click', function() {
        const oid = randomOid('new');
        insertAfterSelected(
            '<div class="item" data-oid="' + oid + '-it">' +
            '<div class="item-label" data-oid="' + oid + '-il">要点</div>' +
            '<div class="item-text" data-oid="' + oid + '-ix">内容</div></div>'
        );
    });

    // Duplicate / Delete / Undo / Redo
    document.getElementById('tb-duplicate').addEventListener('click', function() {
        const sel = editor.getSelected();
        if (!sel) return;
        const parent = sel.parent();
        const idx = sel.index();
        if (parent) parent.append(sel.clone(), { at: idx + 1 });
    });
    document.getElementById('tb-delete').addEventListener('click', function() {
        const sel = editor.getSelected();
        if (!sel) return;
        if (confirm('确认删除选中元素？')) sel.remove();
    });
    document.getElementById('tb-undo').addEventListener('click', function() {
        editor.UndoManager.undo();
    });
    document.getElementById('tb-redo').addEventListener('click', function() {
        editor.UndoManager.redo();
    });

    // ======================================================================
    // Image insert + free-form drag/resize
    // ======================================================================

    // ---- Insert flow: button → file picker → upload → append to slide ----
    const imgInput = document.getElementById('tb-img-file');
    const imgBtn = document.getElementById('tb-ins-image');

    function randomImgOid() {
        return 'img-' + Math.random().toString(36).slice(2, 8);
    }

    function findTargetSlide() {
        // Prefer the slide containing the current selection; fall back to
        // the first .slide in the canvas.
        const sel = editor.getSelected();
        if (sel && sel.getEl) {
            const el = sel.getEl();
            if (el) {
                const s = el.closest('.slide');
                if (s) return s;
            }
        }
        const frame = editor.Canvas.getFrameEl();
        if (frame && frame.contentDocument) {
            return frame.contentDocument.querySelector('.slide');
        }
        return null;
    }

    function appendToComponentByOid(oid, html) {
        // Use GrapesJS wrapper to find the component so that append() keeps
        // the component model in sync (important for Save to include it).
        const wrapper = editor.DomComponents.getWrapper();
        if (!wrapper) return false;
        const matches = wrapper.find('[data-oid="' + oid + '"]');
        if (matches && matches.length) {
            matches[0].append(html);
            return true;
        }
        return false;
    }

    // Shared upload + insert helper, used by button/drag-drop/paste
    function uploadAndInsert(file, targetSlideEl, atX, atY) {
        if (!file) return;
        const form = new FormData();
        form.append('file', file);
        fetch('/api/upload', { method: 'POST', body: form })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!data.ok) {
                    alert('上传失败: ' + (data.error || 'unknown'));
                    return;
                }
                const slide = targetSlideEl || findTargetSlide();
                if (!slide) {
                    alert('找不到目标 slide。请先点选画布里任意一个元素。');
                    return;
                }
                const slideOid = slide.getAttribute('data-oid');
                const oid = randomImgOid();
                // Default size 500px wide; position = drop coordinates if given,
                // otherwise centered near (550, 320).
                const left = (typeof atX === 'number') ? Math.max(0, atX - 250) : 550;
                const top  = (typeof atY === 'number') ? Math.max(0, atY - 150) : 320;
                const imgHtml =
                    '<img src="' + data.path + '"' +
                    ' data-oid="' + oid + '"' +
                    ' data-draggable="true"' +
                    ' style="position:absolute; left:' + left + 'px; top:' + top + 'px;' +
                    ' width:500px; height:auto; z-index:10; cursor:move;' +
                    ' box-shadow:0 4px 18px rgba(0,0,0,0.18);' +
                    ' border-radius:6px;">';
                if (slideOid && appendToComponentByOid(slideOid, imgHtml)) {
                    showSaveToast('📷 图片已插入（' + oid + '）→ Ctrl+S 保存', '#8250df');
                } else {
                    slide.insertAdjacentHTML('beforeend', imgHtml);
                    showSaveToast('图片已插入到 DOM（model 同步可能失败）', '#d29922');
                }
            })
            .catch(function(err) {
                alert('上传异常: ' + err.message);
            });
    }

    if (imgBtn) {
        imgBtn.addEventListener('click', function() { imgInput.click(); });
    }
    if (imgInput) {
        imgInput.addEventListener('change', function(e) {
            const file = e.target.files && e.target.files[0];
            uploadAndInsert(file);
            imgInput.value = '';
        });
    }

    // Compute slide-local coordinates from a mouse event within the canvas
    // iframe, accounting for GrapesJS canvas scaling.
    function pointToSlideCoords(slideEl, clientX, clientY) {
        const rect = slideEl.getBoundingClientRect();
        const scaleX = rect.width > 0 ? (rect.width / slideEl.offsetWidth) : 1;
        const scaleY = rect.height > 0 ? (rect.height / slideEl.offsetHeight) : 1;
        return {
            x: Math.round((clientX - rect.left) / scaleX),
            y: Math.round((clientY - rect.top) / scaleY),
        };
    }

    // ---- A) Drag external image file into the canvas ----
    function installDropHandler(doc) {
        doc.addEventListener('dragover', function(e) {
            // Only react if at least one dragged item is an image.
            const items = e.dataTransfer && e.dataTransfer.items;
            if (!items) return;
            let hasImage = false;
            for (let i = 0; i < items.length; i++) {
                if (items[i].kind === 'file' && items[i].type.indexOf('image/') === 0) {
                    hasImage = true;
                    break;
                }
            }
            if (!hasImage) return;
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });
        doc.addEventListener('drop', function(e) {
            const files = e.dataTransfer && e.dataTransfer.files
                ? Array.from(e.dataTransfer.files) : [];
            const imgFile = files.find(function(f) { return f.type.indexOf('image/') === 0; });
            if (!imgFile) return;
            e.preventDefault();
            e.stopPropagation();
            // Find the slide element under the drop point
            const target = e.target && e.target.closest ? e.target.closest('.slide') : null;
            if (target) {
                const pt = pointToSlideCoords(target, e.clientX, e.clientY);
                uploadAndInsert(imgFile, target, pt.x, pt.y);
            } else {
                uploadAndInsert(imgFile);
            }
        });
    }

    // ---- B) Paste image from clipboard (capture phase to beat GrapesJS) ----
    function installPasteHandler(doc) {
        // Use CAPTURE phase so we run before GrapesJS's own paste handler,
        // which would otherwise try to interpret text/html clipboard data as
        // components to insert (and can cause cross-slide content bleeding).
        doc.addEventListener('paste', function(e) {
            const items = e.clipboardData && e.clipboardData.items
                ? Array.from(e.clipboardData.items) : [];
            const imgItem = items.find(function(it) {
                return it.kind === 'file' && it.type.indexOf('image/') === 0;
            });
            if (imgItem) {
                // Image paste: handle ourselves and block everything else
                e.preventDefault();
                e.stopPropagation();
                if (e.stopImmediatePropagation) e.stopImmediatePropagation();
                const file = imgItem.getAsFile();
                uploadAndInsert(file);
                return;
            }
            // Non-image paste: if clipboard has text/html, strip it and let
            // only plain text through to avoid GrapesJS interpreting random
            // markup as components.
            const htmlItem = items.find(function(it) { return it.type === 'text/html'; });
            if (htmlItem) {
                e.preventDefault();
                e.stopPropagation();
                if (e.stopImmediatePropagation) e.stopImmediatePropagation();
                const textItem = items.find(function(it) { return it.type === 'text/plain'; });
                if (textItem && e.target && e.target.isContentEditable) {
                    textItem.getAsString(function(txt) {
                        try {
                            doc.execCommand('insertText', false, txt);
                        } catch (err) {}
                    });
                }
            }
        }, true);  // ← capture phase
    }

    // Install handlers on BOTH the top document and the canvas iframe document.
    // GrapesJS canvas is an iframe, so events inside it do not bubble to top.
    installDropHandler(document);
    installPasteHandler(document);

    function showSaveToast(text, color) {
        const status = document.getElementById('save-status');
        if (!status) return;
        status.textContent = text;
        status.style.background = color || '#238636';
        status.style.display = 'block';
        setTimeout(function() { status.style.display = 'none'; }, 3000);
    }

    // ---- Free-form drag + corner-resize inside the canvas iframe ----
    // GrapesJS doesn't natively support free x/y drag for absolutely
    // positioned elements, so we hook the iframe document directly.
    // On mouseup we sync back to the component model via addStyle().

    let dragState = null;
    const RESIZE_CORNER_PX = 18;

    editor.on('load', function() {
        const frame = editor.Canvas.getFrameEl();
        if (!frame || !frame.contentDocument) return;
        const doc = frame.contentDocument;

        // Install drop + paste handlers on the canvas iframe document too,
        // so users can drag/paste directly into the slide canvas.
        installDropHandler(doc);
        installPasteHandler(doc);

        // Inject a subtle hover outline so users can see draggable images.
        const style = doc.createElement('style');
        style.textContent = [
            'img[data-draggable="true"] {',
            '  outline: 1px dashed rgba(130,80,223,0.35);',
            '  outline-offset: 2px;',
            '}',
            'img[data-draggable="true"]:hover {',
            '  outline: 2px dashed #8250df;',
            '}',
        ].join('\n');
        doc.head.appendChild(style);

        doc.addEventListener('mousedown', function(e) {
            const img = e.target && e.target.closest && e.target.closest('img[data-draggable="true"]');
            if (!img) return;
            const slide = img.closest('.slide');
            if (!slide) return;

            const rect = img.getBoundingClientRect();
            const slideRect = slide.getBoundingClientRect();
            const nearCorner = (
                e.clientX > rect.right - RESIZE_CORNER_PX &&
                e.clientY > rect.bottom - RESIZE_CORNER_PX
            );

            // Convert current pixel position to "slide-local px", using the
            // canvas's current scale (GrapesJS scales the iframe via zoom).
            const scaleX = slideRect.width / slide.offsetWidth;
            const scaleY = slideRect.height / slide.offsetHeight;

            dragState = {
                img: img,
                slide: slide,
                mode: nearCorner ? 'resize' : 'move',
                scaleX: scaleX || 1,
                scaleY: scaleY || 1,
                startX: e.clientX,
                startY: e.clientY,
                imgLeft: parseFloat(img.style.left) || 0,
                imgTop:  parseFloat(img.style.top)  || 0,
                imgWidth:  img.offsetWidth,
                imgHeight: img.offsetHeight,
                aspect: img.offsetWidth > 0 ? (img.offsetHeight / img.offsetWidth) : 1,
            };
            e.preventDefault();
            e.stopPropagation();
        });

        doc.addEventListener('mousemove', function(e) {
            if (!dragState) {
                // Cursor hint
                const img = e.target && e.target.closest && e.target.closest('img[data-draggable="true"]');
                if (img) {
                    const rect = img.getBoundingClientRect();
                    const nearCorner = (
                        e.clientX > rect.right - RESIZE_CORNER_PX &&
                        e.clientY > rect.bottom - RESIZE_CORNER_PX
                    );
                    img.style.cursor = nearCorner ? 'nwse-resize' : 'move';
                }
                return;
            }
            const dx = (e.clientX - dragState.startX) / dragState.scaleX;
            const dy = (e.clientY - dragState.startY) / dragState.scaleY;
            if (dragState.mode === 'move') {
                dragState.img.style.left = (dragState.imgLeft + dx) + 'px';
                dragState.img.style.top  = (dragState.imgTop + dy) + 'px';
            } else {
                // Resize keeping aspect ratio; Shift breaks aspect lock
                const newW = Math.max(60, dragState.imgWidth + dx);
                const newH = e.shiftKey
                    ? Math.max(60, dragState.imgHeight + dy)
                    : newW * dragState.aspect;
                dragState.img.style.width  = newW + 'px';
                dragState.img.style.height = newH + 'px';
            }
            e.preventDefault();
        });

        function finishDrag() {
            if (!dragState) return;
            // Sync the final values back into the GrapesJS component model
            // so that the next save includes the updated left/top/width/height.
            const img = dragState.img;
            const oid = img.getAttribute('data-oid');
            if (oid) {
                const wrapper = editor.DomComponents.getWrapper();
                const matches = wrapper ? wrapper.find('[data-oid="' + oid + '"]') : [];
                if (matches && matches.length) {
                    const comp = matches[0];
                    const updates = {};
                    if (img.style.left)   updates.left   = img.style.left;
                    if (img.style.top)    updates.top    = img.style.top;
                    if (img.style.width)  updates.width  = img.style.width;
                    if (img.style.height) updates.height = img.style.height;
                    comp.addStyle(updates);
                }
            }
            dragState = null;
        }
        doc.addEventListener('mouseup', finishDrag);
        doc.addEventListener('mouseleave', finishDrag);
    });

    // ======================================================================
    // Block resize — use GrapesJS's NATIVE resize handles.
    //
    // On every selection we walk up to the nearest block-level container,
    // redirect GrapesJS's selection to THAT container (so the handles appear
    // on the right element), and enable `resizable` on it. This prevents the
    // case where the user clicks deep into a title/text span and drags the
    // inner element (which has no visible effect because its parent block is
    // flex:1 and overrides the inner height).
    // ======================================================================
    const BLOCK_LEVEL_SELECTOR =
        '.block, .item, .summary, .risk, .need, .kpi, .two-col, .three-col, .outline-list';

    function findBlockLevelAncestor(el) {
        let cur = el;
        while (cur && cur.nodeType === 1) {
            if (cur.tagName === 'IMG') return null;
            if (cur.classList && cur.classList.contains('slide')) return null;
            if (cur.matches && cur.matches(BLOCK_LEVEL_SELECTOR)) return cur;
            cur = cur.parentElement;
        }
        return null;
    }

    let _redirectingSelection = false;

    // ----- Double-click to edit text in ANY element (including td/th) -----
    // GrapesJS only makes genuine "text" type components editable by default,
    // so <td>, <th>, <div>, <span> etc. can be selected but not edited.
    // Hook double-click to enable contenteditable, commit on blur/Enter.
    const EDITABLE_TAGS = {
        TD: 1, TH: 1, P: 1, DIV: 1, SPAN: 1, LI: 1, A: 1,
        H1: 1, H2: 1, H3: 1, H4: 1, H5: 1, H6: 1,
        B: 1, I: 1, U: 1, STRONG: 1, EM: 1,
    };

    function installInlineEditor(doc) {
        doc.addEventListener('dblclick', function(e) {
            const el = e.target;
            if (!el || !el.tagName) return;
            if (!EDITABLE_TAGS[el.tagName]) return;
            if (el.isContentEditable) return;
            // Skip if the user double-clicked on a child that has its own data-oid —
            // prefer the most specific element under the click.
            el.contentEditable = 'true';
            const prevOutline = el.style.outline;
            const prevBg = el.style.backgroundColor;
            el.style.outline = '2px solid #58a6ff';
            el.style.outlineOffset = '2px';
            el.style.backgroundColor = 'rgba(88, 166, 255, 0.06)';
            el.focus();

            // Place cursor at click position if possible
            try {
                const sel = doc.getSelection ? doc.getSelection() : null;
                if (sel && doc.caretRangeFromPoint) {
                    const r = doc.caretRangeFromPoint(e.clientX, e.clientY);
                    if (r) {
                        sel.removeAllRanges();
                        sel.addRange(r);
                    }
                }
            } catch (err) {}

            function commit() {
                el.contentEditable = 'false';
                el.style.outline = prevOutline;
                el.style.outlineOffset = '';
                el.style.backgroundColor = prevBg;

                // Sync new HTML into GrapesJS component model by data-oid
                const oid = el.getAttribute('data-oid');
                if (oid) {
                    try {
                        const wrapper = editor.DomComponents.getWrapper();
                        const matches = wrapper ? wrapper.find('[data-oid="' + oid + '"]') : [];
                        if (matches && matches.length) {
                            matches[0].components(el.innerHTML);
                        }
                    } catch (err) { /* ignore */ }
                }
                el.removeEventListener('blur', commit);
                el.removeEventListener('keydown', onKey);
            }

            function onKey(ke) {
                if (ke.key === 'Escape') {
                    ke.preventDefault();
                    commit();
                } else if (ke.key === 'Enter' && !ke.shiftKey &&
                           el.tagName !== 'DIV' && el.tagName !== 'TD' && el.tagName !== 'TH') {
                    // For short text tags (P, SPAN, etc.) Enter commits.
                    // For cells / divs, Enter inserts a line break (default behavior).
                    ke.preventDefault();
                    commit();
                }
            }

            el.addEventListener('blur', commit);
            el.addEventListener('keydown', onKey);
            e.preventDefault();
            e.stopPropagation();
        });
    }

    // Install on the canvas iframe once it's ready
    editor.on('load', function() {
        const frame = editor.Canvas.getFrameEl();
        if (frame && frame.contentDocument) {
            installInlineEditor(frame.contentDocument);
            installAutoFit(frame.contentDocument);
        }
    });

    // ======================================================================
    // Overflow DETECTION only — never shrinks the font. User preference is
    // to keep min font size at 20px+; if content overflows, they will trim.
    // We flag overflowing slides with data-overflow="true" so a red badge
    // appears and they know where to cut.
    // ======================================================================
    function fitSlideIn(doc, slide) {
        const body = slide.querySelector('.body-area');
        if (!body) return;
        // Reset any previous zoom from older versions
        if (body.style.zoom) body.style.zoom = '';
        let overflowed = false;
        Array.prototype.forEach.call(body.children, function(c) {
            if (c.scrollHeight > c.clientHeight + 2) overflowed = true;
        });
        if (body.scrollHeight > body.clientHeight + 2) overflowed = true;
        if (overflowed) {
            slide.setAttribute('data-overflow', 'true');
        } else {
            slide.removeAttribute('data-overflow');
        }
    }
    function installAutoFit(doc) {
        function runAll() {
            try {
                doc.querySelectorAll('.slide').forEach(function(s) { fitSlideIn(doc, s); });
            } catch (e) {}
        }
        // Initial pass
        runAll();
        // Re-run on canvas mutations (throttled)
        let mutTimer = null;
        try {
            new doc.defaultView.MutationObserver(function() {
                clearTimeout(mutTimer);
                mutTimer = setTimeout(runAll, 350);
            }).observe(doc.body, { subtree: true, childList: true, characterData: true });
        } catch (e) {}
        // Inject overflow-badge CSS into the iframe document
        try {
            const existing = doc.getElementById('__ls_autofit_css');
            if (!existing) {
                const s = doc.createElement('style');
                s.id = '__ls_autofit_css';
                s.textContent =
                    '.slide[data-overflow="true"]::after {' +
                    '  content: "\\26A0 content exceeds limit";' +
                    '  position: absolute; top: 14px; right: 14px;' +
                    '  background: rgba(231,76,60,0.92); color: #fff;' +
                    '  padding: 4px 10px; border-radius: 4px;' +
                    '  font-size: 13px; font-family: sans-serif;' +
                    '  z-index: 100; pointer-events: none;' +
                    '}';
                doc.head.appendChild(s);
            }
        } catch (e) {}
    }

    // Upsert a [data-oid="X"]{width:Npx} rule in the deck's first <style>
    // element inside the canvas iframe. Used by IMG resize so that the new
    // width is keyed by the stable data-oid (not GrapesJS's auto-generated
    // component id, which gets regenerated on every load and breaks #id
    // selectors — that's exactly why pasted images "maximized" themselves).
    function upsertImgWidthRule(doc, oid, width) {
        if (!doc || !oid || !width) return;
        const styleEl = doc.querySelector('style');
        if (!styleEl) return;
        const sel = '[data-oid="' + oid + '"]';
        const css = styleEl.textContent || '';
        // Find an existing rule for this exact selector
        const re = new RegExp('\\[data-oid="' + oid.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&') + '"\\]\\s*\\{[^}]*\\}', 'g');
        if (re.test(css)) {
            styleEl.textContent = css.replace(re, function(match) {
                // Replace any width:..px with the new width
                if (/width\s*:/i.test(match)) {
                    return match.replace(/width\s*:\s*[^;}]+/i, 'width:' + width + 'px !important');
                }
                // Otherwise inject width before closing brace
                return match.replace(/\}$/, ';width:' + width + 'px !important;}');
            });
        } else {
            styleEl.textContent = css + sel + '{width:' + width + 'px !important;height:auto !important;max-width:none !important;}';
        }
    }

    editor.on('component:selected', function(comp) {
        if (_redirectingSelection) { _redirectingSelection = false; return; }
        if (!comp || !comp.getEl) return;
        const el = comp.getEl();
        if (!el) return;

        // ----- IMG: enable corner resize, persist via [data-oid] CSS rule -----
        if (el.tagName === 'IMG') {
            comp.set('resizable', {
                tl: 1, tc: 0, tr: 1,
                cl: 1, cr: 1,
                bl: 1, bc: 0, br: 1,
                keepAutoHeight: true,
                autoHeight: true,
                autoWidth: false,
                minDim: 50,
                unitWidth: 'px',
                onEnd: function() {
                    try {
                        const w = el.offsetWidth;
                        const oid = el.getAttribute('data-oid');
                        if (oid && w) {
                            upsertImgWidthRule(el.ownerDocument, oid, w);
                            // Also nudge GrapesJS to mark dirty so save picks up
                            try { editor.trigger('change:canvasOffset'); } catch (e) {}
                        }
                    } catch (err) { /* ignore */ }
                },
            });
            return;
        }


        // Redirect to the nearest block-level container if we're not already on one
        const blockLevel = findBlockLevelAncestor(el);
        if (blockLevel && blockLevel !== el) {
            const oid = blockLevel.getAttribute('data-oid');
            const wrapper = editor.DomComponents.getWrapper();
            if (oid && wrapper) {
                const matches = wrapper.find('[data-oid="' + oid + '"]');
                if (matches && matches.length) {
                    _redirectingSelection = true;
                    editor.select(matches[0]);
                    return;  // the re-fired event will handle the rest
                }
            }
        }
        // If no block-level ancestor found, this element isn't resizable
        if (!blockLevel) return;
        // Enable GrapesJS's built-in resize: top-center and bottom-center only
        comp.set('resizable', {
            tl: 0, tc: 1, tr: 0,
            cl: 0, cr: 0,
            bl: 0, bc: 1, br: 0,
            keepAutoHeight: false,
            autoHeight: false,
            autoWidth: true,
            minDim: 30,
            unitHeight: 'px',

            // On drag start: freeze every sibling at its current rendered
            // height so the flex container stops auto-redistributing space.
            // Without this, pulling block A bigger in a packed slide would
            // shrink B and C (flex:1 1 0). After freeze, only A changes.
            onStart: function(e, opts) {
                try {
                    const curEl = comp.getEl();
                    if (!curEl) return;
                    const parent = curEl.parentElement;
                    if (!parent) return;
                    const siblings = Array.from(parent.children);
                    siblings.forEach(function(sib) {
                        // Freeze everyone (including the target) so their
                        // heights become fixed. GrapesJS will then only
                        // change curEl's height via the drag.
                        const h = sib.offsetHeight;
                        if (h > 0) {
                            sib.style.height = h + 'px';
                            sib.style.flex = '0 0 auto';
                        }
                    });
                } catch (err) { /* ignore */ }
            },

            // On drag end: persist the new inline styles to GrapesJS's
            // component model so the next save captures them. We also
            // capture the siblings' frozen heights, since they're now part
            // of the user's layout intent.
            onEnd: function(e, opts) {
                try {
                    const curEl = comp.getEl();
                    if (!curEl) return;
                    // Sync the target component's height
                    if (curEl.style.height) {
                        const updates = { 'height': curEl.style.height };
                        if (curEl.style.flex) updates.flex = curEl.style.flex;
                        comp.addStyle(updates);
                    }
                    // Sync the frozen siblings' heights too
                    const parent = curEl.parentElement;
                    if (parent) {
                        const wrapper = editor.DomComponents.getWrapper();
                        Array.from(parent.children).forEach(function(sib) {
                            if (sib === curEl) return;
                            const sibOid = sib.getAttribute('data-oid');
                            if (!sibOid || !wrapper) return;
                            const sibComps = wrapper.find('[data-oid="' + sibOid + '"]');
                            if (sibComps && sibComps.length) {
                                const sibUpdates = {};
                                if (sib.style.height) sibUpdates.height = sib.style.height;
                                if (sib.style.flex) sibUpdates.flex = sib.style.flex;
                                if (Object.keys(sibUpdates).length) {
                                    sibComps[0].addStyle(sibUpdates);
                                }
                            }
                        });
                    }
                } catch (err) { /* ignore */ }
            },
        });
    });

    // Z-index front/back controls
    const frontBtn = document.getElementById('tb-img-front');
    const backBtn = document.getElementById('tb-img-back');
    if (frontBtn) {
        frontBtn.addEventListener('click', function() {
            applyStyleToSelected('z-index', '20');
        });
    }
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            applyStyleToSelected('z-index', '1');
        });
    }

    // Live-sync toolbar values with the currently selected element
    editor.on('component:selected', function(sel) {
        if (!sel || !sel.getStyle) return;
        const style = sel.getStyle() || {};
        const el = sel.getEl();
        if (!el) return;
        // Use computed style for inherited values
        const computed = window.getComputedStyle(el);
        const fs = style['font-size'] || computed.fontSize;
        const ff = style['font-family'] || computed.fontFamily;
        if (fs && fontSizeSel) {
            const opts = Array.from(fontSizeSel.options).map(o => o.value);
            if (opts.indexOf(fs) !== -1) fontSizeSel.value = fs;
            else fontSizeSel.value = '';
        }
        if (ff && fontFamilySel) {
            const opts = Array.from(fontFamilySel.options).map(o => o.value);
            // Fuzzy match
            const match = opts.find(o => o && ff.indexOf(o.split(',')[0].replace(/['"]/g, '')) !== -1);
            fontFamilySel.value = match || '';
        }
    });

    // ======================================================================
    // Selection hierarchy — used internally as "chat attachment context"
    // Layer 1: page (.slide + data-oid="sNN-slide" + title)
    // Layer 2: frames (semantic containers)
    // Layer 3: element (selected leaf)
    // ======================================================================
    const SEMANTIC_CONTAINER_CLASSES = [
        'block', 'risk', 'need', 'summary', 'kpi-row', 'kpi',
        'two-col', 'three-col', 'outline-list', 'progress-table',
        'header', 'body-area', 'tag-box', 'item',
    ];

    function textPreview(el, max) {
        if (!el) return '';
        const t = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
        return t.length > max ? t.slice(0, max) + '…' : t;
    }

    function buildHierarchy(component) {
        if (!component) return null;
        const el = component.getEl ? component.getEl() : component;
        if (!el || !el.closest) return null;

        const pageEl = el.closest('.slide');
        let page = null;
        if (pageEl) {
            const pageOid = pageEl.getAttribute('data-oid') || '';
            const m = pageOid.match(/^s(\d+)/);
            const titleEl = pageEl.querySelector('.title');
            const eyebrowEl = pageEl.querySelector('.eyebrow');
            page = {
                index: m ? parseInt(m[1], 10) : null,
                oid: pageOid || null,
                title: titleEl ? textPreview(titleEl, 80) : '',
                eyebrow: eyebrowEl ? textPreview(eyebrowEl, 60) : '',
            };
        }

        const frames = [];
        let cur = el.parentElement;
        while (cur && cur !== pageEl) {
            const oid = cur.getAttribute && cur.getAttribute('data-oid');
            const classes = cur.classList ? Array.from(cur.classList) : [];
            const semantic = classes.find(c => SEMANTIC_CONTAINER_CLASSES.indexOf(c) !== -1);
            if (semantic || oid) {
                frames.unshift({
                    role: semantic || null,
                    oid: oid || null,
                    tag: cur.tagName.toLowerCase(),
                    classes: classes,
                    preview: textPreview(cur, 80),
                });
            }
            cur = cur.parentElement;
        }

        const element = {
            oid: el.getAttribute('data-oid') || null,
            tag: el.tagName ? el.tagName.toLowerCase() : '',
            classes: el.classList ? Array.from(el.classList) : [],
            text: textPreview(el, 240),
        };

        return { page: page, frames: frames, element: element };
    }

    // ======================================================================
    // Chat panel logic
    // ======================================================================
    let currentHierarchy = null;  // latest selection, auto-attached to next msg

    function updateAttachBar() {
        const bar = document.getElementById('chat-attach-bar');
        if (!bar) return;
        if (!currentHierarchy) {
            bar.className = 'empty';
            bar.textContent = '无选中 · 消息会作用到整个文档';
            return;
        }
        bar.className = '';
        const p = currentHierarchy.page || {};
        const elOid = currentHierarchy.element.oid || '(no oid)';
        const elText = currentHierarchy.element.text || '';
        const shortText = elText.length > 28 ? elText.slice(0, 28) + '…' : elText;
        bar.innerHTML =
            '📍 <span class="attach-chip">' +
            '<span class="pg">p.' + (p.index != null ? p.index : '?') + '</span>' +
            '<span class="oid">' + elOid + '</span>' +
            (shortText ? ' · ' + shortText : '') +
            '</span>';
    }

    editor.on('component:selected', function(component) {
        currentHierarchy = buildHierarchy(component);
        updateAttachBar();
    });
    editor.on('component:deselected', function() {
        currentHierarchy = null;
        updateAttachBar();
    });

    function renderMessages(messages) {
        const list = document.getElementById('chat-messages');
        if (!list) return;
        if (!messages || messages.length === 0) {
            list.innerHTML = '<div class="empty">点选画布里任意元素，<br>告诉我要改什么。</div>';
            return;
        }
        list.innerHTML = messages.map(function(m) {
            const role = m.role === 'user' ? '你' : 'Claude';
            const time = m.timestamp ? new Date(m.timestamp).toLocaleTimeString() : '';
            let attach = '';
            if (m.role === 'user' && m.selection && m.selection.page) {
                const p = m.selection.page;
                const oid = m.selection.element ? (m.selection.element.oid || '(no oid)') : '';
                attach = '<div class="msg-attach">📍 p.' + (p.index != null ? p.index : '?') +
                         ' · ' + oid + '</div>';
            }
            // Escape HTML in message text
            const escaped = (m.text || '').replace(/[&<>"']/g, function(c) {
                return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
            });
            return '<div class="msg ' + m.role + '">' +
                '<div class="msg-meta"><span class="role">' + role + '</span><span>' + time + '</span></div>' +
                escaped +
                attach +
                '</div>';
        }).join('');
        list.scrollTop = list.scrollHeight;
    }

    let lastMessageCount = 0;

    function pollMessages() {
        fetch('/api/chat')
            .then(r => r.json())
            .then(data => {
                const msgs = data.messages || [];
                if (msgs.length !== lastMessageCount) {
                    lastMessageCount = msgs.length;
                    renderMessages(msgs);
                }
            })
            .catch(err => { /* ignore transient errors */ });
    }

    function sendMessage() {
        const input = document.getElementById('chat-input');
        const btn = document.getElementById('chat-send-btn');
        const text = (input.value || '').trim();
        if (!text) return;
        btn.disabled = true;
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                selection: currentHierarchy,
            }),
        })
        .then(r => r.json())
        .then(data => {
            btn.disabled = false;
            if (data.ok) {
                input.value = '';
                pollMessages();
            } else {
                alert('发送失败: ' + (data.error || 'unknown'));
            }
        })
        .catch(err => {
            btn.disabled = false;
            alert('发送失败: ' + err.message);
        });
    }

    const sendBtn = document.getElementById('chat-send-btn');
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);

    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Collapse / reopen
    const toggleBtn = document.getElementById('chat-toggle');
    const reopenBtn = document.getElementById('chat-reopen');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            document.body.classList.add('chat-collapsed');
        });
    }
    if (reopenBtn) {
        reopenBtn.addEventListener('click', function() {
            document.body.classList.remove('chat-collapsed');
        });
    }

    // ----- Draggable chat panel (via header) -----
    (function makeDraggable() {
        const panel = document.getElementById('chat-panel');
        const header = document.getElementById('chat-header');
        if (!panel || !header) return;
        let dragging = false, startX = 0, startY = 0, startLeft = 0, startTop = 0;

        header.addEventListener('mousedown', function(e) {
            // Don't start drag if user clicked the close button
            if (e.target.closest('#chat-toggle')) return;
            dragging = true;
            const rect = panel.getBoundingClientRect();
            startX = e.clientX;
            startY = e.clientY;
            startLeft = rect.left;
            startTop = rect.top;
            // Switch from right-anchored to left-anchored on first drag
            panel.style.left = rect.left + 'px';
            panel.style.top = rect.top + 'px';
            panel.style.right = 'auto';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (!dragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            let newLeft = startLeft + dx;
            let newTop = startTop + dy;
            // Clamp to viewport
            const maxLeft = window.innerWidth - panel.offsetWidth;
            const maxTop = window.innerHeight - 40;
            newLeft = Math.max(0, Math.min(newLeft, maxLeft));
            newTop = Math.max(52, Math.min(newTop, maxTop));
            panel.style.left = newLeft + 'px';
            panel.style.top = newTop + 'px';
        });

        document.addEventListener('mouseup', function() {
            if (dragging) {
                dragging = false;
                document.body.style.userSelect = '';
                // Persist position in localStorage
                try {
                    localStorage.setItem('chatPanelPos', JSON.stringify({
                        left: panel.style.left,
                        top: panel.style.top,
                        width: panel.style.width,
                        height: panel.style.height,
                    }));
                } catch (err) {}
            }
        });

        // Restore last position
        try {
            const saved = JSON.parse(localStorage.getItem('chatPanelPos') || 'null');
            if (saved && saved.left && saved.top) {
                panel.style.left = saved.left;
                panel.style.top = saved.top;
                panel.style.right = 'auto';
                if (saved.width) panel.style.width = saved.width;
                if (saved.height) panel.style.height = saved.height;
            }
        } catch (err) {}

        // Also persist on resize (native CSS resize)
        const resizeObserver = new ResizeObserver(function() {
            try {
                const saved = JSON.parse(localStorage.getItem('chatPanelPos') || '{}') || {};
                saved.width = panel.style.width || panel.offsetWidth + 'px';
                saved.height = panel.style.height || panel.offsetHeight + 'px';
                if (panel.style.left) saved.left = panel.style.left;
                if (panel.style.top) saved.top = panel.style.top;
                localStorage.setItem('chatPanelPos', JSON.stringify(saved));
            } catch (err) {}
        });
        resizeObserver.observe(panel);
    })();

    // Initial load + polling
    updateAttachBar();
    pollMessages();
    setInterval(pollMessages, 2000);
})();
