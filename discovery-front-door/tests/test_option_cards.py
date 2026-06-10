"""Option-card pattern: title on button, caption separate — never stacked labels."""

from __future__ import annotations

import inspect

from journey import render as journey_render
from journey import widgets


def test_option_card_helper_exists():
    assert callable(widgets.option_card)
    assert callable(widgets.option_caption)


def test_render_module_never_stacks_title_and_description_in_button():
    source = inspect.getsource(journey_render)
    assert "_selection_button" not in source
    assert '\\n\\n' not in source
    assert "f\"{label}\\n\\n" not in source
