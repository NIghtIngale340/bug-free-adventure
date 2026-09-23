from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QSizePolicy,
)

from app.gui.widgets.result_card import ResultCard


class ResultOverlay(QWidget):
    closed = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("ResultOverlayBackdrop")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hide()

        self._card_wrap = QWidget(self)
        self._card_wrap.setFixedWidth(460)

        self._card = ResultCard(self._card_wrap, show_close_button=True)
        self._card.setObjectName("ResultModalCard")
        self._card.closeRequested.connect(lambda: self.dismiss(silent=False))

        shadow = QGraphicsDropShadowEffect(self._card)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 170))
        self._card.setGraphicsEffect(shadow)

        wrap_layout = QVBoxLayout(self._card_wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.addWidget(self._card)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._card_wrap, alignment=Qt.AlignmentFlag.AlignCenter)

        self._anim: QPropertyAnimation | None = None

    def show_result(self, result) -> None:
        self._card.show_result(result)
        self.raise_()
        self.show()

        opacity = QGraphicsOpacityEffect(self._card_wrap)
        self._card_wrap.setGraphicsEffect(opacity)
        opacity.setOpacity(0.0)

        self._anim = QPropertyAnimation(opacity, b"opacity", self)
        self._anim.setDuration(200)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._detach_opacity_effect)
        self._anim.start()

    def _detach_opacity_effect(self) -> None:
        # No cached-pixmap effect left attached -> nothing for alt-tab to corrupt.
        self._card_wrap.setGraphicsEffect(None)

    def dismiss(self, silent: bool = False) -> None:
        self.hide()
        if not silent:
            self.closed.emit()

    def refresh(self) -> None:
        if not self.isVisible():
            return
        self.update()
        self._card_wrap.update()
        self._card.update()