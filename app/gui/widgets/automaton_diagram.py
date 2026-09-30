"""
Model-driven state diagram (NFA, DFA or minimal DFA) with zoom, pan and step highlighting.

Nothing about the automaton is hardcoded here: nodes and labelled edges come from a
`Graph` (app/core/present.py) built from the very objects the simulator executes.
Node colours: idle = outline · visited = amber tint · current = solid amber ·
accepting = double ring · dead = dashed red.
"""

import math
import os

from PySide6.QtCore import QEasingCurve, QPointF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.present import GEdge, Graph
from app.gui.theme import FONT_MONO
from app.gui.theme import PALETTE as P

R, COL, ROW, MARGIN, ARROW = 26, 108, 118, 60, 10
DURATION_MS = 180                                            # state / edge colour transitions
ANIMATE = os.environ.get("CAUTOMA_REDUCE_MOTION", "") != "1"  # set CAUTOMA_REDUCE_MOTION=1 to disable
_NODE_STYLE = {   # status: (fill, stroke, width, dashed, text colour)
    "idle": (P["surface"], P["line"], 2, False, P["text"]),
    "visited": (P["accent_bg"], P["accent"], 2, False, P["text"]),
    "current": (P["accent"], P["accent"], 3, False, P["accent_text"]),
    "accept": (P["ok"], P["ok"], 3, False, P["accent_text"]),
    "reject": (P["bad_bg"], P["bad"], 3, False, P["text"]),
    "dead": (P["surface"], P["bad"], 2, True, P["text"]),
    "dead_hit": (P["bad"], P["bad"], 3, False, P["accent_text"]),
}


def _pen(color, width: float, dashed: bool = False) -> QPen:
    pen = QPen(QColor(color), width)
    if dashed:
        pen.setStyle(Qt.PenStyle.DashLine)
    return pen


def _mix(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(*(round(x + (y - x) * t) for x, y in ((a.red(), b.red()), (a.green(), b.green()),
                                                        (a.blue(), b.blue()), (a.alpha(), b.alpha()))))


def _style(status: str) -> tuple:
    fill, stroke, width, dashed, text = _NODE_STYLE[status]
    return QColor(fill), QColor(stroke), float(width), QColor(text), dashed


class _Hot:
    """Mixin: report hover / click of a scene item to the diagram (explanation strip + tooltip)."""

    def _hot(self, tip: str, owner) -> None:
        self.tip, self._owner = tip, owner
        self.setAcceptHoverEvents(True)
        self.setToolTip(tip)

    def hoverEnterEvent(self, event) -> None:
        self._owner.hovered.emit(self.tip)

    def hoverLeaveEvent(self, event) -> None:
        self._owner.hovered.emit("")

    def mousePressEvent(self, event) -> None:
        self._owner.clicked.emit(self.tip)
        event.accept()


class _HotEllipse(_Hot, QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, tip, owner) -> None:
        QGraphicsEllipseItem.__init__(self, x, y, w, h)
        self._hot(tip, owner)


class _HotPath(_Hot, QGraphicsPathItem):
    def __init__(self, path, tip, owner) -> None:
        QGraphicsPathItem.__init__(self, path)
        self._hot(tip, owner)


class _Edge:
    def __init__(self, e: GEdge, line, head, label) -> None:
        self.e, self.line, self.head, self.label = e, line, head, label
        self.active = False
        self.shown = self.start = self.end = self.target()
        self.apply(1.0)

    def target(self) -> tuple[QColor, float]:
        return (QColor(P["accent"]), 3.2) if self.active else (QColor(P["line"]), 1.8)

    def retarget(self, active: bool) -> None:
        self.active, self.start, self.end = active, self.shown, self.target()
        f = self.label.font()
        f.setBold(active)
        self.label.setFont(f)
        self.label.setBrush(QBrush(QColor(P["accent"] if active else P["muted"])))
        for item in (self.line, self.head):
            item.setZValue(1 if active else 0.4)

    def apply(self, t: float) -> None:
        color, width = _mix(self.start[0], self.end[0], t), self.start[1] + (self.end[1] - self.start[1]) * t
        self.shown = (color, width)
        self.line.setPen(_pen(color, width, self.e.epsilon))
        self.head.setBrush(QBrush(color))


class AutomatonDiagram(QGraphicsView):
    hovered = Signal(str)     # explanation of the item under the cursor ("" when it leaves)
    clicked = Signal(str)     # explanation of the clicked state / transition

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAccessibleName("Automaton diagram")
        self._anim: QVariantAnimation | None = None
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor(P["bg"])))
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._auto_fit = True
        self.graph: Graph | None = None
        self._clear_state()

    # --- build ----------------------------------------------------------------

    def _clear_state(self) -> None:
        if self._anim:
            self._anim.stop()
            self._anim = None
        self._scene.clear()
        self._shown_nodes: dict[str, tuple] = {}
        self._from_nodes: dict[str, tuple] = {}
        self._to_nodes: dict[str, tuple] = {}
        self._nodes: dict[str, tuple[QGraphicsEllipseItem, QGraphicsSimpleTextItem]] = {}
        self._pos: dict[str, QPointF] = {}
        self._index: dict[str, int] = {}
        self._edges: list[_Edge] = []
        self._temp: list = []
        self._visited: set[str] = set()
        self._current: set[str] = set()
        self._final: str | None = None
        self._dead: str | None = None

    def set_graph(self, graph: Graph) -> None:
        self._clear_state()
        self.graph = graph
        live = [n for n in graph.nodes if not n.dead]
        cols = 7 if len(live) <= 16 else 9
        for i, n in enumerate(live):
            row, col = divmod(i, cols)
            col = cols - 1 - col if row % 2 else col
            self._pos[n.name] = QPointF(MARGIN + col * COL, MARGIN + row * ROW)
            self._index[n.name] = i
        rows = (len(live) - 1) // cols + 1
        for n in graph.nodes:
            if n.dead:
                self._dead = n.name
                self._pos[n.name] = QPointF(MARGIN + (cols - 1) * COL, MARGIN + rows * ROW)
        for n in graph.nodes:
            self._add_node(n)
        for e in graph.edges:
            self._add_edge(e)
        for n in graph.nodes:
            if n.caption:
                self._add_caption(n)
        start = next((n for n in graph.nodes if n.start), None)
        if start:
            self._add_start_arrow(start.name)
        self._transition(animate=False)
        self.setAccessibleDescription(f"{graph.title}: {len(graph.nodes)} states. Hover or click a state or transition for an explanation.")
        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(-40, -40, 40, 40))
        self.fit()

    def _add_node(self, n) -> None:
        c = self._pos[n.name]
        if n.accepting:
            ring = QGraphicsEllipseItem(c.x() - R - 6, c.y() - R - 6, 2 * (R + 6), 2 * (R + 6))
            ring.setPen(_pen(P["line"], 2))
            self._scene.addItem(ring)
        ell = _HotEllipse(c.x() - R, c.y() - R, 2 * R, 2 * R, n.tip, self)
        ell.setZValue(2)
        self._scene.addItem(ell)
        label = QGraphicsSimpleTextItem(n.name)
        label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        label.setFont(QFont(FONT_MONO.split(",")[0].strip('" '), 12 if len(n.name) < 5 else 10, QFont.Weight.Bold))
        label.setZValue(3)
        self._scene.addItem(label)
        r = label.boundingRect()
        label.setPos(c.x() - r.width() / 2, c.y() - r.height() / 2)
        if n.dead:
            note = QGraphicsSimpleTextItem("dead state: every undefined move ends here")
            note.setFont(QFont(FONT_MONO.split(",")[0].strip('" '), 9))
            note.setBrush(QBrush(QColor(P["muted"])))
            nr = note.boundingRect()
            note.setPos(c.x() - nr.width() + R, c.y() + R + (22 if n.caption else 8))
            self._scene.addItem(note)
        self._nodes[n.name] = (ell, label)
        self._shown_nodes[n.name] = _style("dead" if n.dead else "idle")

    def _add_caption(self, n) -> None:
        """Subset caption under the node; shifted aside when a vertical edge leaves downward."""
        c = self._pos[n.name]
        cap = QGraphicsSimpleTextItem(n.caption)
        cap.setFont(QFont(FONT_MONO.split(",")[0].strip('" '), 9))
        cap.setBrush(QBrush(QColor(P["muted"])))
        cr = cap.boundingRect()
        down = any(e.src == n.name and self._pos[e.dst].y() > c.y() + 1 and abs(self._pos[e.dst].x() - c.x()) < 1
                   for e in self.graph.edges)
        cap.setPos(c.x() - cr.width() - 6 if down else c.x() - cr.width() / 2, c.y() + R + 6)
        self._scene.addItem(cap)

    def _add_start_arrow(self, name: str) -> None:
        c = self._pos[name]
        tip = QPointF(c.x() - R, c.y())
        path = QPainterPath(QPointF(tip.x() - 34, tip.y()))
        path.lineTo(tip)
        line = QGraphicsPathItem(path)
        line.setPen(_pen(P["line"], 2))
        head = QGraphicsPolygonItem(self._arrow(tip, 1, 0))
        head.setBrush(QBrush(QColor(P["line"])))
        head.setPen(QPen(Qt.PenStyle.NoPen))
        self._scene.addItem(line)
        self._scene.addItem(head)

    @staticmethod
    def _arrow(tip: QPointF, ux: float, uy: float) -> QPolygonF:
        bx, by = tip.x() - ux * ARROW, tip.y() - uy * ARROW
        return QPolygonF([tip, QPointF(bx - uy * ARROW * .45, by + ux * ARROW * .45),
                          QPointF(bx + uy * ARROW * .45, by - ux * ARROW * .45)])

    def _route(self, a: QPointF, b: QPointF, curved: bool, bulge: float = 46, t: float = .5):
        """(path, tip, unit direction at the tip, label anchor) for an edge between node centres."""
        mx, my = (a.x() + b.x()) / 2, (a.y() + b.y()) / 2
        dx, dy = b.x() - a.x(), b.y() - a.y()
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        path = QPainterPath()
        if not curved:
            p1 = QPointF(a.x() + ux * R, a.y() + uy * R)
            tip = QPointF(b.x() - ux * R, b.y() - uy * R)
            path.moveTo(p1)
            path.lineTo(tip)
            return path, tip, (ux, uy), QPointF(mx, my), (uy, -ux)
        ctrl = QPointF(mx - uy * bulge, my + ux * bulge)
        sx, sy = ctrl.x() - a.x(), ctrl.y() - a.y()
        sd = math.hypot(sx, sy) or 1.0
        ex, ey = b.x() - ctrl.x(), b.y() - ctrl.y()
        ed = math.hypot(ex, ey) or 1.0
        p1 = QPointF(a.x() + sx / sd * R, a.y() + sy / sd * R)
        tip = QPointF(b.x() - ex / ed * R, b.y() - ey / ed * R)
        path.moveTo(p1)
        path.quadTo(ctrl, tip)
        w0, w1, w2 = (1 - t) ** 2, 2 * t * (1 - t), t * t
        anchor = QPointF(w0 * p1.x() + w1 * ctrl.x() + w2 * tip.x(), w0 * p1.y() + w1 * ctrl.y() + w2 * tip.y())
        return path, tip, (ex / ed, ey / ed), anchor, ((ctrl.x() - mx) / bulge, (ctrl.y() - my) / bulge)

    def _place_label(self, label: QGraphicsSimpleTextItem, anchor: QPointF, normal) -> None:
        nx, ny = normal
        if ny > 0 or (ny == 0 and nx < 0):
            nx, ny = -nx, -ny
        r = label.boundingRect()
        off = 12 + .5 * (abs(nx) * r.width() + abs(ny) * r.height())
        label.setPos(anchor.x() + nx * off - r.width() / 2, anchor.y() + ny * off - r.height() / 2)

    def _add_edge(self, e: GEdge) -> None:
        a, b = self._pos[e.src], self._pos[e.dst]
        curved = abs(self._index.get(e.src, 0) - self._index.get(e.dst, 0)) != 1
        path, tip, (ux, uy), anchor, normal = self._route(a, b, curved)
        line = QGraphicsPathItem(path)
        head = QGraphicsPolygonItem(self._arrow(tip, ux, uy))
        head.setPen(QPen(Qt.PenStyle.NoPen))
        label = QGraphicsSimpleTextItem(e.label)
        label.setFont(QFont(FONT_MONO.split(",")[0].strip('" '), 12))
        for item in (line, head, label):
            self._scene.addItem(item)
        self._place_label(label, anchor, normal)
        label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        hit = _HotPath(path, e.tip, self)             # wide invisible stroke: easy to hover / click
        hit.setPen(QPen(QColor(0, 0, 0, 0), 16))
        hit.setZValue(0.2)
        self._scene.addItem(hit)
        self._edges.append(_Edge(e, line, head, label))

    # --- highlighting (animated) -------------------------------------------------------

    def _node_status(self, name: str) -> str:
        if name in self._current:
            return "dead_hit" if name == self._dead else (self._final or "current")
        if name == self._dead:
            return "dead"
        return "visited" if name in self._visited else "idle"

    def _paint_node(self, name: str, style: tuple) -> None:
        fill, stroke, width, text, dashed = style
        ell, label = self._nodes[name]
        ell.setBrush(QBrush(fill))
        ell.setPen(_pen(stroke, width, dashed))
        label.setBrush(QBrush(text))
        self._shown_nodes[name] = style

    def _apply_frame(self, t) -> None:
        t = max(0.0, min(1.0, float(t)))
        for name, end in self._to_nodes.items():
            a = self._from_nodes[name]
            self._paint_node(name, (_mix(a[0], end[0], t), _mix(a[1], end[1], t), a[2] + (end[2] - a[2]) * t,
                                    _mix(a[3], end[3], t), end[4]))
        for e in self._edges:
            e.apply(t)
        for item in self._temp:
            item.setOpacity(t)

    def _transition(self, animate: bool) -> None:
        """Move what is painted towards the current model state: eased over ~180 ms, or snapped."""
        if self._anim:
            self._anim.stop()
            self._anim = None
        self._from_nodes = dict(self._shown_nodes)
        self._to_nodes = {n: _style(self._node_status(n)) for n in self._nodes}
        for e in self._edges:
            e.start, e.end = e.shown, e.target()
        if animate and ANIMATE and self.isVisible():
            anim = QVariantAnimation(self)
            anim.setDuration(DURATION_MS)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.valueChanged.connect(self._apply_frame)
            anim.finished.connect(lambda: self._apply_frame(1.0))
            self._anim = anim
            self._apply_frame(0.0)
            anim.start()
        else:
            self._apply_frame(1.0)

    def _clear_temp(self) -> None:
        for item in self._temp:
            self._scene.removeItem(item)
        self._temp = []

    def _describe_current(self) -> None:
        names = ", ".join(sorted(self._current)) or "none (empty set)"
        self.setAccessibleDescription(f"{self.graph.title if self.graph else ''}. Current state: {names}. "
                                      f"Visited: {len(self._visited)} states.")

    def reset_highlight(self, active=()) -> None:
        """Nothing visited yet; `active` marks the start state(s). Snaps (no animation)."""
        self._clear_temp()
        self._visited, self._current, self._final = set(), set(active), None
        for e in self._edges:
            e.retarget(False)
        self._transition(animate=False)
        self._describe_current()

    def show_step(self, prev, nxt, symbol: str, dead: bool) -> None:
        """One consumed symbol: states left become 'visited', edges used light up."""
        self._clear_temp()
        prev, nxt = set(prev), set(nxt)
        self._visited |= prev
        self._final = None
        for e in self._edges:
            ed = e.e
            e.retarget((not ed.epsilon and symbol in ed.symbols and ed.src in prev and ed.dst in nxt) or
                       (ed.epsilon and ed.src in nxt and ed.dst in nxt))
        if dead and self._dead in self._pos and len(prev) == 1:
            (src,) = prev
            self._add_dead_edge(src, symbol)
            nxt = {self._dead}
        self._current = nxt
        self._transition(animate=True)
        self._describe_current()

    def _add_dead_edge(self, src: str, symbol: str) -> None:
        path, tip, (ux, uy), anchor, normal = self._route(self._pos[src], self._pos[self._dead], True, 34, t=.2)
        line = _HotPath(path, f"δ({src}, {symbol}) = {self._dead} — no valid move: the run enters the dead state and is rejected.", self)
        line.setPen(_pen(P["bad"], 3, True))
        head = QGraphicsPolygonItem(self._arrow(tip, ux, uy))
        head.setBrush(QBrush(QColor(P["bad"])))
        head.setPen(QPen(Qt.PenStyle.NoPen))
        label = QGraphicsSimpleTextItem(symbol)
        label.setFont(QFont(FONT_MONO.split(",")[0].strip('" '), 12, QFont.Weight.Bold))
        label.setBrush(QBrush(QColor(P["bad"])))
        for item, z in ((line, .5), (head, .5), (label, 5)):   # under the nodes, label on top
            item.setZValue(z)
            item.setOpacity(0.0)
            self._scene.addItem(item)
        self._place_label(label, anchor, normal)
        self._temp = [line, head, label]

    def show_final(self, accepted: bool) -> None:
        """Colour the state(s) the run ended in: green if accepted, red outline if rejected."""
        self._final = "accept" if accepted else "reject"
        self._transition(animate=True)

    # --- view control -----------------------------------------------------------------

    def fit(self) -> None:
        self._auto_fit = True
        rect = self._scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        self.resetTransform()
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        if self.transform().m11() > 1.5:
            self.resetTransform()
            self.scale(1.5, 1.5)
            self.centerOn(rect.center())

    def zoom(self, factor: float) -> None:
        new = self.transform().m11() * factor
        if 0.2 <= new <= 5:
            self.scale(factor, factor)
            self._auto_fit = False

    def wheelEvent(self, event) -> None:
        self.zoom(1.15 ** (event.angleDelta().y() / 120))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._auto_fit and self.graph:
            self.fit()


class DiagramPanel(QWidget):
    """Diagram + title + zoom buttons + an explanation strip (hover or click a state / transition)."""

    DEFAULT = ("Double ring = accepting · amber = current · tinted = visited · dashed red = dead. "
               "Hover or click a state or transition to explain it; scroll to zoom, drag to pan.")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.title = QLabel()
        self.title.setObjectName("SubHeading")
        self.view = AutomatonDiagram()
        row = QHBoxLayout()
        row.addWidget(self.title)
        row.addStretch()
        for text, tip, fn in (("−", "Zoom out", lambda: self.view.zoom(1 / 1.25)),
                              ("Fit", "Fit to window", self.view.fit),
                              ("+", "Zoom in", lambda: self.view.zoom(1.25))):
            b = QPushButton(text)
            b.setObjectName("ToolButton")
            b.setToolTip(tip)
            b.setAccessibleName(tip)
            b.clicked.connect(fn)
            row.addWidget(b)
        self._pinned = ""
        self.info = QLabel(self.DEFAULT)
        self.info.setObjectName("InfoStrip")
        self.info.setWordWrap(True)
        self.info.setMinimumHeight(44)
        self.info.setAccessibleName("Diagram explanation")
        self.view.hovered.connect(lambda t: self.info.setText(t or self._pinned or self.DEFAULT))
        self.view.clicked.connect(self._pin)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(row)
        lay.addWidget(self.view, 1)
        lay.addWidget(self.info)

    def _pin(self, text: str) -> None:
        self._pinned = text
        self.info.setText(text)

    def set_graph(self, graph: Graph) -> None:
        self.title.setText(graph.title)
        self._pinned = ""
        self.info.setText(self.DEFAULT)
        self.view.set_graph(graph)
