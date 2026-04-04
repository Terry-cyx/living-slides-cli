(function() {
    const editor = grapesjs.init({
        container: '#gjs',
        fromElement: false,
        storageManager: false,
        plugins: [],
        canvas: {
            styles: [],
            scripts: [],
        },
        panels: { defaults: [] },
    });

    // Add save button to toolbar
    editor.Panels.addButton('options', {
        id: 'save-btn',
        className: 'fa fa-floppy-o',
        command: 'save-html',
        attributes: { title: 'Save (Ctrl+S)' },
        label: '💾 Save',
    });

    // Load HTML from server on init
    fetch('/api/load')
        .then(r => r.json())
        .then(data => {
            if (data.html) {
                editor.setComponents(data.html);
                if (data.css) {
                    editor.setStyle(data.css);
                }
            }
        })
        .catch(err => console.error('Failed to load HTML:', err));

    // Save command
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
            })
            .catch(err => {
                console.error('Save failed:', err);
            });
        },
    });

    // Ctrl+S shortcut
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            editor.runCommand('save-html');
        }
    });
})();
