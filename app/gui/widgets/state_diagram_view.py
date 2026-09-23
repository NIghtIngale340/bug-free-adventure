import math

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QBrush, QColor, QPen, QFont, QPainter, QPainterPath, QPolygonF
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsPathItem, QGraphicsPolygonItem, QSizePolicy, QFrame,
)

_CHAIN = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8",
          "q9", "q10", "q11", "q12", "q13"]
_TRAP = "q_trap"

_EDGE_LABELS = {
    ("q0", "q1"): "E", ("q1", "q2"): "M", ("q2", "q3"): "P", ("q3", "q4"): "-",
    ("q4", "q5"): "0-9", ("q5", "q6"): "0-9", ("q6", "q7"): "0-9", ("q7", "q8"): "0-9",
    ("q8", "q9"): "-",
    ("q9", "q10"): "0-9", ("q10", "q11"): "0-9", ("q11", "q12"): "0-9", ("q12", "q13"): "0-9",
}

# Where to draw each edge's label relative to the line's midpoint.
_EDGE_LABEL_SIDE = {
    ("q0", "q1"): "above", ("q1", "q2"): "above", ("q2", "q3"): "above", ("q3", "q4"): "above",
    ("q4", "q5"): "right",
    ("q5", "q6"): "above", ("q6", "q7"): "above", ("q7", "q8"): "above", ("q8", "q9"): "above",
    ("q9", "q10"): "left",
    ("q10", "q11"): "above", ("q11", "q12"): "above", ("q12", "q13"): "above",
}

_COLUMNS = 5
_COL_SPACING = 150
_ROW_SPACING = 150
_RADIUS = 36
_RING_GAP = 6
_MARGIN = 100
_ARROW_SIZE = 11

_IDLE_BRUSH = QBrush(QColor("#1B2028"))
_VISITED_BRUSH = QBrush(QColor("#173028"))
_ACTIVE_BRUSH = QBrush(QColor("#3A2E12"))
_ACCEPT_BRUSH = QBrush(QColor("#1FAE7A"))
_TRAP_BRUSH = QBrush(QColor("#2B1518"))
_TRAP_ACTIVE_BRUSH = QBrush(QColor("#C13B3B"))

_BORDER = QPen(QColor("#3A404B"), 2)
_VISITED_BORDER = QPen(QColor("#2E7D5C"), 2)
_ACTIVE_BORDER = QPen(QColor("#E8A93A"), 3)
_ACCEPT_BORDER = QPen(QColor("#0E8F60"), 3)
_TRAP_BORDER = QPen(QColor("#7A2323"), 2)
_TRAP_ACTIVE_BORDER = QPen(QColor("#8F1F1F"), 3)
_FINAL_RING_PEN = QPen(QColor("#2E7D5C"), 2)

_LINE_PEN = QPen(QColor("#3A404B"), 2)
_ARROW_BRUSH = QBrush(QColor("#3A404B"))
_LABEL_COLOR = QColor("#7C8593")
_NODE_TEXT_COLOR = QColor("#E5E7EB")


def _snake_position(index: int) -> tuple[float, float]:
    """Boustrophedon layout: even rows go left→right, odd rows go right→left."""
    row, col = divmod(index, _COLUMNS)
    if row % 2 == 1:
        col = _COLUMNS - 1 - col
    x = _MARGIN + col * _COL_SPACING
    y = _MARGIN + row * _ROW_SPACING
    return x, y


def _shrink_to_borders(ax: float, ay: float, bx: float, by: float, radius: float):
    dx, dy = bx - ax, by - ay
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    return (ax + ux * radius, ay + uy * radius), (bx - ux * radius, by - uy * radius), (ux, uy)


def _arrow_head_polygon(tip_x: float, tip_y: float, ux: float, uy: float, size: float = _ARROW_SIZE) -> QPolygonF:
    back_x, back_y = tip_x - ux * size, tip_y - uy * size
    perp_x, perp_y = -uy, ux
    p1 = QPointF(back_x + perp_x * size * 0.5, back_y + perp_y * size * 0.5)
    p2 = QPointF(back_x - perp_x * size * 0.5, back_y - perp_y * size * 0.5)
    return QPolygonF([QPointF(tip_x, tip_y), p1, p2])


class StateDiagramView(QGraphicsView):
    def __init__(self, accepting_states: set[str], parent=None) -> None:
        super().__init__(parent)
        self._accepting = accepting_states
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._nodes: dict[str, QGraphicsEllipseItem] = {}
        self._positions: dict[str, tuple[float, float]] = {}
        self._build_chain()

    def _build_chain(self) -> None:
        self._scene.clear()
        self._nodes.clear()
        self._positions.clear()

        for i, state in enumerate(_CHAIN):
            self._positions[state] = _snake_position(i)

        self._add_initial_arrow(_CHAIN[0])

        for i, state in enumerate(_CHAIN):
            x, y = self._positions[state]
            self._add_node(state, x, y)
            if i > 0:
                self._add_edge(_CHAIN[i - 1], state)

        last_row = (len(_CHAIN) - 1) // _COLUMNS
        trap_x = _MARGIN + (_COLUMNS - 1) * _COL_SPACING
        trap_y = _MARGIN + (last_row + 1) * _ROW_SPACING
        self._positions[_TRAP] = (trap_x, trap_y)
        self._add_node(_TRAP, trap_x, trap_y, is_trap=True)

        pad = _RADIUS + 40
        min_x = min(p[0] for p in self._positions.values()) - pad
        max_x = max(p[0] for p in self._positions.values()) + pad
        max_y = max(p[1] for p in self._positions.values()) + pad
        self._scene.setSceneRect(min(0, min_x), 0, max_x - min(0, min_x), max_y)
        self._fit()

    def _add_initial_arrow(self, first_state: str) -> None:
        x0, y0 = self._positions[first_state]
        start_x = x0 - _RADIUS - 40
        end_x = x0 - _RADIUS
        path = QPainterPath()
        path.moveTo(start_x, y0)
        path.lineTo(end_x, y0)
        line = QGraphicsPathItem(path)
        line.setPen(_LINE_PEN)
        line.setZValue(-1)
        self._scene.addItem(line)

        arrow = QGraphicsPolygonItem(_arrow_head_polygon(end_x, y0, 1.0, 0.0))
        arrow.setBrush(_ARROW_BRUSH)
        arrow.setPen(QPen(Qt.PenStyle.NoPen))
        arrow.setZValue(-1)
        self._scene.addItem(arrow)

    def _add_node(self, state: str, x: float, y: float, is_trap: bool = False) -> None:
        if not is_trap and state in self._accepting:
            ring = QGraphicsEllipseItem(
                x - _RADIUS - _RING_GAP, y - _RADIUS - _RING_GAP,
                (_RADIUS + _RING_GAP) * 2, (_RADIUS + _RING_GAP) * 2,
            )
            ring.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            ring.setPen(_FINAL_RING_PEN)
            ring.setZValue(0)
            self._scene.addItem(ring)

        ellipse = QGraphicsEllipseItem(x - _RADIUS, y - _RADIUS, _RADIUS * 2, _RADIUS * 2)
        ellipse.setBrush(_TRAP_BRUSH if is_trap else _IDLE_BRUSH)
        ellipse.setPen(_TRAP_BORDER if is_trap else _BORDER)
        ellipse.setZValue(1)
        self._scene.addItem(ellipse)

        label = QGraphicsTextItem(state)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        label.setDefaultTextColor(_NODE_TEXT_COLOR)
        label.setZValue(2)
        rect = label.boundingRect()
        label.setPos(x - rect.width() / 2, y - rect.height() / 2)
        self._scene.addItem(label)

        self._nodes[state] = ellipse

    def _add_edge(self, a: str, b: str) -> None:
        ax, ay = self._positions[a]
        bx, by = self._positions[b]
        (sx, sy), (ex, ey), (ux, uy) = _shrink_to_borders(ax, ay, bx, by, _RADIUS)

        path = QPainterPath()
        path.moveTo(sx, sy)
        path.lineTo(ex, ey)
        line = QGraphicsPathItem(path)
        line.setPen(_LINE_PEN)
        line.setZValue(-1)
        self._scene.addItem(line)

        arrow = QGraphicsPolygonItem(_arrow_head_polygon(ex, ey, ux, uy))
        arrow.setBrush(_ARROW_BRUSH)
        arrow.setPen(QPen(Qt.PenStyle.NoPen))
        arrow.setZValue(-1)
        self._scene.addItem(arrow)

        label_text = _EDGE_LABELS.get((a, b), "")
        if not label_text:
            return

        label = QGraphicsTextItem(label_text)
        label.setFont(QFont("Segoe UI", 10))
        label.setDefaultTextColor(_LABEL_COLOR)
        rect = label.boundingRect()
        mx, my = (ax + bx) / 2, (ay + by) / 2
        side = _EDGE_LABEL_SIDE.get((a, b), "above")

        if side == "above":
            label.setPos(mx - rect.width() / 2, my - _RADIUS - rect.height() - 6)
        elif side == "right":
            label.setPos(mx + _RADIUS * 0.7, my - rect.height() / 2)
        else:  # "left"
            label.setPos(mx - _RADIUS * 0.7 - rect.width(), my - rect.height() / 2)
        self._scene.addItem(label)

    def reset(self) -> None:
        for state, node in self._nodes.items():
            if state == _TRAP:
                node.setBrush(_TRAP_BRUSH)
                node.setPen(_TRAP_BORDER)
            else:
                node.setBrush(_IDLE_BRUSH)
                node.setPen(_BORDER)

    def highlight(self, current_state: str, trapped: bool = False, finished: bool = False) -> None:
        for state, node in self._nodes.items():
            if state == current_state:
                if trapped:
                    node.setBrush(_TRAP_ACTIVE_BRUSH)
                    node.setPen(_TRAP_ACTIVE_BORDER)
                elif finished and state in self._accepting:
                    node.setBrush(_ACCEPT_BRUSH)
                    node.setPen(_ACCEPT_BORDER)
                else:
                    node.setBrush(_ACTIVE_BRUSH)
                    node.setPen(_ACTIVE_BORDER)
            elif state == _TRAP:
                continue
            else:
                node.setBrush(_VISITED_BRUSH)
                node.setPen(_VISITED_BORDER)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._fit()

    def _fit(self) -> None:
        if self._scene.sceneRect().isValid():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)