def update_header_source_buttons(app, pagename, templatename, context, doctree):
    """Replace .py with .ipynb in the download sources button.

    Sphinx documentation at https://www.sphinx-doc.org/en/master/extdev/event_callbacks.html#event-html-page-context
    """
    buttons = context["header_buttons"]
    dropdown_buttons = next((i["buttons"] for i in buttons if "fa-download" in i["icon"].split()), False)
    if not dropdown_buttons:
        return
    bad_button = next((i for i in dropdown_buttons if i["text"] == ".py"), False)
    if not bad_button:
        return
    bad_button["url"] = bad_button["url"].replace(".py", ".ipynb")
    bad_button["text"] = ".ipynb"

def setup(app):
    # Prioritize to run after `add_header_buttons`
    # https://github.com/executablebooks/sphinx-book-theme/blob/master/src/sphinx_book_theme/__init__.py
    app.connect("html-page-context", update_header_source_buttons, priority=502)
    return {
        'version': '0.1',
        'env_version': 1,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }