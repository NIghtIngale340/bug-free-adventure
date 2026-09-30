from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.gui.theme import PALETTE

_VISIBLE = {" ": "␣", "\t": "⇥", "\n": "↵"}


def segment_legend(segments) -> str:
    """Rich-text legend of the RE parts, coloured like the bars under the tape."""
    items = [f'<span style="color:{PALETTE["seg_a" if i % 2 == 0 else "seg_b"]}">■</span> {s.name} <b>{s.formal}</b>'
             for i, s in enumerate(segments)]
    return "Regular-expression parts:  " + "   ".join(items)


def repolish(w: QWidget) -> None:
    w.style().unpolish(w)
    w.style().polish(w)


class TapeView(QFrame):
    """The input string as a row of cells; shows progress, the failing symbol and illegal symbols."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TapeFrame")
        self.setAccessibleName("Input tape")
        self.setFixedHeight(84)
        self._row = QHBoxLayout()
        self._row.setContentsMargins(10, 5, 10, 5)
        self._row.setSpacing(5)
        inner = QWidget()
        inner.setObjectName("TapeInner")
        inner.setLayout(self._row)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(inner)
        self._scroll.viewport().setObjectName("TapeViewport")
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)
        self._cells: list[QLabel] = []
        self._illegal: set[int] = set()

    def load(self, text: str, illegal: set[int] | None = None, segments=()) -> None:
        """`segments`: RE parts (name, formal, start, end); a coloured bar under each cell shows which part matches it."""
        while self._row.count():
            item = self._row.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        self._cells, self._illegal = [], set(illegal or ())
        if not text:
            hint = QLabel("(empty input)")
            hint.setObjectName("Muted")
            self._row.addWidget(hint)
        for i, ch in enumerate(text):
            col = QVBoxLayout()
            col.setSpacing(2)
            cell = QLabel(_VISIBLE.get(ch, ch))
            cell.setObjectName("TapeCell")
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setFixedSize(34, 34)
            cell.setToolTip(f"position {i}: {ch!r}" + ("  — not in Σ" if i in self._illegal else ""))
            seg = next(((k, sg) for k, sg in enumerate(segments) if sg.start <= i < sg.end), None)
            bar = QLabel()
            bar.setObjectName("TapeSeg")
            bar.setProperty("seg", "none" if seg is None else "a" if seg[0] % 2 == 0 else "b")
            if seg:
                cell.setToolTip(cell.toolTip() + f"  — {seg[1].name} ({seg[1].formal})")
            idx = QLabel(str(i))
            idx.setObjectName("TapeIndex")
            idx.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(cell)
            col.addWidget(bar)
            col.addWidget(idx)
            holder = QWidget()
            holder.setObjectName("TapeInner")
            holder.setLayout(col)
            self._row.addWidget(holder)
            self._cells.append(cell)
        self._row.addStretch()
        self.set_progress(0)

    def set_progress(self, consumed: int, failed: bool = False, accepted: bool = False) -> None:
        """`consumed` symbols have been read; the last one is highlighted (red if it killed the run)."""
        for i, cell in enumerate(self._cells):
            if i in self._illegal:
                kind = "illegal"
            elif accepted:
                kind = "final"
            elif i < consumed - 1:
                kind = "done"
            elif i == consumed - 1:
                kind = "error" if failed else "active"
            else:
                kind = "pending"
            cell.setProperty("cell", kind)
            repolish(cell)
        self.setAccessibleDescription(f"{consumed} of {len(self._cells)} symbols read"
                                      + (", the last one caused rejection" if failed else "")
                                      + (", input accepted" if accepted else "")
                                      + (f", symbols outside the alphabet at positions {sorted(self._illegal)}" if self._illegal else ""))
        if 0 < consumed <= len(self._cells):
            self._scroll.ensureWidgetVisible(self._cells[consumed - 1].parentWidget())
        elif self._illegal:
            self._scroll.ensureWidgetVisible(self._cells[min(self._illegal)].parentWidget())
