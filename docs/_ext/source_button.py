def update_header_source_buttons(app, pagename, templatename, context, doctree):
    """Prepend .ipynb button to the download sources dropdown.

    Sphinx documentation at https://www.sphinx-doc.org/en/master/extdev/event_callbacks.html#event-html-page-context
    """
    buttons = context["header_buttons"]
    dropdown_buttons = next((i["buttons"] for i in buttons if "fa-download" in i["icon"].split()), [])
    md_button = next((i for i in dropdown_buttons if i["text"] == ".md"), False)
    if md_button:
        # FIXME import jupytext and write to md_button["url"], no action for unpaired MyST
        ipynb_button = {
            **md_button,
            "text": ".ipynb",
            "url": md_button["url"].replace(".md", ".ipynb"),
        }
        dropdown_buttons.insert(0, ipynb_button)


def setup(app):
    # Prioritize to run after `add_header_buttons`
    # https://github.com/executablebooks/sphinx-book-theme/blob/master/src/sphinx_book_theme/__init__.py
    app.connect("html-page-context", update_header_source_buttons, priority=502)
    return {
        "version": "0.1",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
