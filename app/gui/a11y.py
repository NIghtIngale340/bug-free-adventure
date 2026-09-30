"""Accessibility helpers: names/descriptions for screen readers and live announcements."""

from PySide6.QtGui import QAccessible, QAccessibleEvent
from PySide6.QtWidgets import QWidget


def label(widget: QWidget, name: str, description: str = "") -> QWidget:
    widget.setAccessibleName(name)
    if description:
        widget.setAccessibleDescription(description)
    return widget


def announce(widget: QWidget) -> None:
    """Ask assistive technology to read `widget` (an alert); harmless where accessibility is off."""
    try:
        QAccessible.updateAccessibility(QAccessibleEvent(widget, QAccessible.Event.Alert))
    except Exception:  # noqa: BLE001 - never let accessibility break the app
        pass
