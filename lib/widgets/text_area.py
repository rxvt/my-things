"""Custom TextArea widget with cursor-scroll fix for newline insertion."""

from textual.widgets import TextArea
from textual.widgets._text_area import Edit
from textual.widgets._text_area import EditResult


class ScrollingTextArea(TextArea):
    """A TextArea that keeps the cursor visible after newline insertion.

    Textual's stock TextArea calls ``scroll_cursor_visible`` inside ``edit()``
    before ``_refresh_size()`` has updated ``virtual_size``.  For newlines this
    means ``max_scroll_y`` is still based on the pre-edit document height and
    the scroll delta is clamped to zero.  Regular characters don't change the
    document height so they are unaffected.

    The fix schedules an additional ``scroll_cursor_visible`` call via
    ``call_after_refresh`` whenever the edit text contains a newline, matching
    the pattern Textual itself uses in ``_watch_soft_wrap``.
    """

    def edit(self, edit: Edit) -> EditResult:
        """Apply an edit and ensure the cursor stays visible afterwards.

        Args:
            edit: The edit operation to apply.

        Returns:
            The result of the edit operation.
        """
        result = super().edit(edit)
        if "\n" in edit.text:
            self.call_after_refresh(self.scroll_cursor_visible)
        return result
