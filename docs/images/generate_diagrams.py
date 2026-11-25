#!/usr/bin/env python3
"""Generates the architecture diagrams (SVG) used in docs/*.md.

Run:  python3 docs/images/generate_diagrams.py
No dependencies beyond the Python standard library.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).parent
FONT = "Helvetica, Arial, sans-serif"
MONO = "Menlo, Consolas, monospace"

C = {
    "text": "#212121", "muted": "#616161", "arrow": "#455A64",
    "svc_fill": "#E8F5E9", "svc_stroke": "#43A047", "svc_sub": "#2E7D32",
    "topic_fill": "#FFE0B2", "topic_stroke": "#EF6C00",
    "band_fill": "#FFF8EE", "band_stroke": "#FFB74D",
    "dlq_fill": "#FFCDD2", "dlq_stroke": "#C62828",
    "db_fill": "#E3F2FD", "db_stroke": "#1E88E5",
    "ext_fill": "#F5F5F5", "ext_stroke": "#9E9E9E",
    "k8s": "#326CE5",
    "ok_fill": "#C8E6C9", "ok_stroke": "#2E7D32",
    "comp_fill": "#FFE0B2", "comp_stroke": "#EF6C00",
    "end_fill": "#ECEFF1", "end_stroke": "#37474F",
}


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.els = []
        self.bg = []

    # ---------- primitives ----------
    def text(self, x, y, s, size=13, weight="normal", fill=None, anchor="middle",
             family=FONT, halo=False, italic=False, strike=False):
        extra = ' stroke="white" stroke-width="4" paint-order="stroke"' if halo else ""
        style = (' font-style="italic"' if italic else "") + (' text-decoration="line-through"' if strike else "")
        self.els.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill or C["text"]}" text-anchor="{anchor}"{style}{extra}>'
            f'{escape(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke, rx=10, dash=False, sw=1.6):
        d = ' stroke-dasharray="7 5"' if dash else ""
        self.els.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def _lines(self, x, y, w, h, title, lines, title_size=15, line_size=11.5,
               first_color=None, title_family=FONT):
        total = title_size + 4 + (line_size + 4) * len(lines)
        cy = y + (h - total) / 2 + title_size - 1
        cx = x + w / 2
        self.text(cx, cy, title, size=title_size, weight="bold", family=title_family)
        for i, ln in enumerate(lines):
            cy += line_size + 4 + (4 if i == 0 else 0)
            color = first_color if (i == 0 and first_color) else C["muted"]
            self.text(cx, cy, ln, size=line_size, fill=color)

    def tag(self, x, y, label="STRETCH"):
        w = 7 * len(label) + 10
        self.rect(x - w, y - 9, w, 16, "#FFF9C4", "#F9A825", rx=4, sw=1)
        self.text(x - w / 2, y + 3, label, size=9, weight="bold", fill="#8D6E00")

    # ---------- components ----------
    def service(self, x, y, w, h, title, lines=(), stretch=False):
        self.rect(x, y, w, h, C["svc_fill"], C["svc_stroke"], dash=stretch, sw=2)
        self._lines(x, y, w, h, title, lines, first_color=C["svc_sub"])
        if stretch:
            self.tag(x + w - 4, y + 2)

    def infra(self, x, y, w, h, title, lines=(), fill="#EDE7F6", stroke="#5E35B1",
              stretch=False):
        self.rect(x, y, w, h, fill, stroke, dash=stretch, sw=2)
        self._lines(x, y, w, h, title, lines, title_size=14, line_size=11)
        if stretch:
            self.tag(x + w - 4, y + 2)

    def ext(self, x, y, w, h, title, lines=()):
        self.rect(x, y, w, h, C["ext_fill"], C["ext_stroke"], dash=True)
        self._lines(x, y, w, h, title, lines, title_size=13, line_size=11)

    def topic(self, x, y, w, label, h=30, kind="topic", stretch=False, sub=None, bold=False):
        fill, stroke = (C["dlq_fill"], C["dlq_stroke"]) if kind == "dlq" else (C["topic_fill"], C["topic_stroke"])
        self.rect(x, y, w, h, fill, stroke, rx=h / 2, dash=stretch, sw=2.6 if bold else 1.6)
        if sub:
            self.text(x + w / 2, y + h / 2 - 2, label, size=12, weight="bold", family=MONO)
            self.text(x + w / 2, y + h / 2 + 13, sub, size=10, fill=C["muted"])
        else:
            self.text(x + w / 2, y + h / 2 + 4, label, size=11.5,
                      weight="bold" if bold else "normal", family=MONO)

    def band(self, x, y, w, h, label=None, label_anchor="middle"):
        self.rect(x, y, w, h, C["band_fill"], C["band_stroke"], rx=12, dash=False, sw=1.4)
        if label:
            lx = x + w / 2 if label_anchor == "middle" else x + 14
            self.text(lx, y + 19, label, size=12, weight="bold", fill="#BF5B00", anchor=label_anchor)

    def db(self, x, y, w, h, title, lines=(), stretch=False):
        ry = 10
        d = ' stroke-dasharray="7 5"' if stretch else ""
        self.els.append(
            f'<path d="M{x},{y + ry} A{w / 2},{ry} 0 0 1 {x + w},{y + ry} V{y + h - ry} '
            f'A{w / 2},{ry} 0 0 1 {x},{y + h - ry} Z" fill="{C["db_fill"]}" '
            f'stroke="{C["db_stroke"]}" stroke-width="2"{d}/>')
        self.els.append(
            f'<ellipse cx="{x + w / 2}" cy="{y + ry}" rx="{w / 2}" ry="{ry}" '
            f'fill="#BBDEFB" stroke="{C["db_stroke"]}" stroke-width="2"{d}/>')
        self._lines(x, y + ry, w, h - ry, title, lines, title_size=13, line_size=10.5)

    def event(self, x, y, w, name, emitter, kind="ok", stretch=False, h=52):
        fill, stroke = {"ok": (C["ok_fill"], C["ok_stroke"]),
                        "fail": (C["dlq_fill"], C["dlq_stroke"]),
                        "comp": (C["comp_fill"], C["comp_stroke"]),
                        "end": (C["end_fill"], C["end_stroke"])}[kind]
        self.rect(x, y, w, h, fill, stroke, rx=10, dash=stretch, sw=2)
        self.text(x + w / 2, y + 22, name, size=13.5, weight="bold")
        self.text(x + w / 2, y + 40, emitter, size=11, fill=C["muted"])
        if stretch:
            self.tag(x + w - 4, y + 2)

    def arrow(self, pts, label=None, at=None, dash=False, both=False, color=None,
              label_anchor="middle", label_size=10.5):
        color = color or C["arrow"]
        p = " ".join(f"{a},{b}" for a, b in pts)
        d = ' stroke-dasharray="6 4"' if dash else ""
        start = ' marker-start="url(#arrowStart)"' if both else ""
        self.els.append(
            f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="1.8"{d} '
            f'marker-end="url(#arrow)"{start}/>')
        if label:
            lx, ly = at
            self.text(lx, ly, label, size=label_size, fill=C["muted"], anchor=label_anchor, halo=True)

    def line(self, pts, dash=True, color=None):
        color = color or C["arrow"]
        p = " ".join(f"{a},{b}" for a, b in pts)
        d = ' stroke-dasharray="4 4"' if dash else ""
        self.els.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="1.4"{d}/>')

    def boundary(self, x, y, w, h, title, sub=None, color=None):
        color = color or C["k8s"]
        self.rect(x, y, w, h, "none", color, rx=16, dash=True, sw=2)
        self.text(x + 16, y + 22, title, size=13.5, weight="bold", fill=color, anchor="start")
        if sub:
            self.text(x + 16, y + 40, sub, size=11, fill=C["muted"], anchor="start")

    def heading(self, s, sub=None):
        self.text(30, 38, s, size=22, weight="bold", anchor="start")
        if sub:
            self.text(30, 58, sub, size=12, fill=C["muted"], anchor="start")

    def legend(self, y, items, x=30):
        for kind, label in items:
            if kind == "service":
                self.rect(x, y - 12, 34, 18, C["svc_fill"], C["svc_stroke"], rx=4, sw=1.6)
            elif kind == "stretch":
                self.rect(x, y - 12, 34, 18, C["svc_fill"], C["svc_stroke"], rx=4, dash=True, sw=1.6)
            elif kind == "topic":
                self.rect(x, y - 12, 34, 18, C["topic_fill"], C["topic_stroke"], rx=9)
            elif kind == "dlq":
                self.rect(x, y - 12, 34, 18, C["dlq_fill"], C["dlq_stroke"], rx=9)
            elif kind == "db":
                self.rect(x, y - 12, 34, 18, C["db_fill"], C["db_stroke"], rx=6)
            elif kind == "infra":
                self.rect(x, y - 12, 34, 18, "#EDE7F6", "#5E35B1", rx=4)
            elif kind == "ext":
                self.rect(x, y - 12, 34, 18, C["ext_fill"], C["ext_stroke"], rx=4, dash=True)
            elif kind == "compose":
                self.rect(x, y - 12, 34, 18, "none", "#546E7A", rx=4, dash=True, sw=2)
            elif kind == "cloud":
                self.rect(x, y - 12, 34, 18, "#E8EAF6", "#3949AB", rx=4)
            elif kind == "k8sres":
                self.rect(x, y - 12, 34, 18, "#E1F5FE", "#0277BD", rx=4)
            elif kind == "resil":
                self.rect(x, y - 12, 34, 18, "#FFF3E0", "#EF6C00", rx=4)
            elif kind == "k8s":
                self.rect(x, y - 12, 34, 18, "none", C["k8s"], rx=4, dash=True, sw=2)
            elif kind in ("ok", "fail", "comp", "end"):
                f, s = {"ok": (C["ok_fill"], C["ok_stroke"]), "fail": (C["dlq_fill"], C["dlq_stroke"]),
                        "comp": (C["comp_fill"], C["comp_stroke"]), "end": (C["end_fill"], C["end_stroke"])}[kind]
                self.rect(x, y - 12, 34, 18, f, s, rx=4)
            self.text(x + 42, y + 2, label, size=12, anchor="start")
            x += 42 + int(6.6 * len(label)) + 28

    def save(self, name):
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">\n'
            f'<title>{escape(self.title)}</title>\n'
            '<defs>'
            f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["arrow"]}"/></marker>'
            f'<marker id="arrowStart" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
            f'<path d="M10,0 L0,5 L10,10 z" fill="{C["arrow"]}"/></marker>'
            + "".join(
                f'<marker id="mk-{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
                f'<path d="{d}" fill="{f}" stroke="{f}" stroke-width="1.2"/></marker>'
                for n, d, f in [("orange", "M0,0 L10,5 L0,10 z", "#EF6C00"),
                                ("red", "M0,0 L10,5 L0,10 z", "#C62828"),
                                ("grey", "M0,1 L9,5 L0,9", "#78909C")])
            + '</defs>\n'
            f'<rect width="100%" height="100%" fill="white"/>\n'
            + "\n".join(self.bg + self.els) + "\n</svg>\n")
        (OUT / name).write_text(svg)
        print("wrote", OUT / name)


# =====================================================================
# Project 3 — Notification Hub
# =====================================================================
def notification_hub():
    s = Svg(1600, 700, "Project 3 - Notification Hub architecture")
    s.heading("Project 3 · Real-time Notification Hub",
              "Spring Boot services on Kubernetes, communicating only through Kafka topics")
    s.boundary(180, 80, 1240, 540, "Kubernetes cluster (kind)",
               "namespace: notifications (apps) · namespace: kafka (Strimzi)")

    # Strimzi banner + topic bands
    s.rect(420, 130, 790, 44, C["band_fill"], C["topic_stroke"], rx=10, sw=1.6)
    s.text(815, 157, "Kafka cluster · Strimzi operator · 3 brokers (KRaft) · RF=3 · min.insync.replicas=2",
           size=12.5, weight="bold", fill="#BF5B00")
    s.line([(540, 174), (540, 255)])
    s.line([(1060, 174), (1060, 200)])
    s.band(420, 255, 240, 150, "domain events")
    s.topic(435, 285, 210, "users.user.events", h=34)
    s.topic(435, 341, 210, "orders.order.events", h=34)
    s.band(930, 200, 260, 350, "channel commands")
    s.topic(945, 230, 230, "notifications.email.commands", h=34)
    s.topic(945, 313, 230, "notifications.sms.commands", h=34, stretch=True)
    s.topic(945, 396, 230, "notifications.push.commands", h=34, stretch=True)
    s.topic(945, 495, 230, "notifications.dlq", h=34, kind="dlq")
    s.text(1060, 470, "key = userId · 6 partitions", size=10.5, fill=C["muted"])

    # client + producer
    s.ext(20, 300, 110, 60, "Client", ["curl / Postman"])
    s.arrow([(130, 330), (215, 330)], "POST /events", (172, 352))
    s.service(215, 298, 170, 64, "event-producer", ["Spring Boot", "REST + KafkaTemplate"])
    s.arrow([(385, 322), (435, 302)])
    s.arrow([(385, 338), (435, 358)])

    # router
    s.arrow([(645, 302), (695, 322)])
    s.arrow([(645, 358), (695, 338)])
    s.service(695, 285, 200, 90, "notification-service",
              ["Spring Boot · router", "@KafkaListener → KafkaTemplate", "preferences + templates"])
    s.db(720, 445, 150, 95, "PostgreSQL", ["preferences · templates", "notification status"])
    s.arrow([(795, 375), (795, 445)], both=True)

    # fan-out to channel topics
    for y in (247, 330, 413):
        s.arrow([(895, 330 + (y - 330) * 0.2), (945, y)])

    # workers + providers
    workers = [("email-worker", 247, False, "Deployment ×1–6 (scales)"),
               ("sms-worker", 330, True, "Deployment"),
               ("push-worker", 413, True, "Deployment")]
    providers = ["SMTP stub", "SMS stub", "Push stub"]
    for (name, cy, stretch, dep), prov in zip(workers, providers):
        s.arrow([(1175, cy), (1225, cy)])
        s.service(1225, cy - 32, 170, 64, name, ["Spring Boot · @KafkaListener", dep], stretch=stretch)
        s.arrow([(1395, cy), (1450, cy)])
        s.ext(1450, cy - 25, 130, 50, prov, ["configurable failures"])

    # DLQ + status
    s.arrow([(1250, 445), (1176, 503)], color=C["dlq_stroke"])
    s.text(1250, 470, "retries exhausted /", size=10.5, fill=C["dlq_stroke"], anchor="start")
    s.text(1250, 484, "poison message", size=10.5, fill=C["dlq_stroke"], anchor="start")
    s.arrow([(1340, 445), (1340, 585), (795, 585), (795, 541)], dash=True,
            label="workers record delivery status (FR-10)", at=(1060, 579))

    s.legend(660, [("service", "Spring Boot service"), ("stretch", "Stretch (optional)"),
                   ("topic", "Kafka topic"), ("dlq", "Dead-letter topic"), ("db", "Database"),
                   ("ext", "External / stub"), ("k8s", "Kubernetes boundary")])
    s.save("03-notification-hub-architecture.svg")


# =====================================================================
# Project 4 — Order Saga (architecture)
# =====================================================================
def order_saga_architecture():
    s = Svg(1560, 900, "Project 4 - Order Saga architecture")
    s.heading("Project 4 · E-commerce Order Saga",
              "Schema per service · transactional outbox → polling relay → Kafka → idempotent consumers")
    s.boundary(170, 70, 1360, 740, "Kubernetes cluster (kind)",
               "namespace: shop · one Helm umbrella chart · PodDisruptionBudgets · Kafka via Strimzi")

    cols = [210, 420, 630, 840, 1050]
    cw = 190
    centers = [c + cw / 2 for c in cols]

    # Kafka band
    s.band(200, 125, 1080, 135, "Kafka cluster (Strimzi) · key = orderId · RF=3", label_anchor="start")
    topics = [("orders.order.events", False), ("payments.payment.events", False),
              ("inventory.stock.events", False), ("shipping.shipment.events", True)]
    for (name, st), c in zip(topics, cols):
        s.topic(c, 160, cw, name, h=32, stretch=st)
    s.topic(cols[4], 160, cw, "retry-5s · retry-1m · dlq", h=32, kind="dlq", stretch=True)
    s.text(216, 238, "Each service's outbox relay publishes here. Consumers use @KafkaListener and skip "
                     "duplicates (processed_events).", size=11, fill=C["muted"], anchor="start")

    s.infra(1310, 135, 195, 80, "Schema Registry", ["Apicurio / Confluent", "Avro / Protobuf schemas"],
            stretch=True)
    s.line([(1280, 175), (1310, 175)])

    # consume (down) + publish (up) per service
    for i, c in enumerate(centers):
        s.arrow([(c - 30, 260), (c - 30, 380)], "consume" if i == 0 else None,
                (c - 38, 325) if i == 0 else None, label_anchor="end")
        if i < 4:
            s.arrow([(c + 30, 380), (c + 30, 261)], "publish (relay)" if i == 0 else None,
                    (c + 38, 325) if i == 0 else None, label_anchor="start")

    s.ext(25, 400, 120, 60, "Client", ["POST /orders"])
    s.arrow([(145, 430), (210, 430)])

    services = [
        ("order-service", ["Spring Boot · REST + JPA", "outbox relay (@Scheduled)"], False),
        ("payment-service", ["Spring Boot · fake gateway", "outbox relay (@Scheduled)"], False),
        ("inventory-service", ["Spring Boot · JPA", "outbox relay (@Scheduled)"], False),
        ("shipping-service", ["Spring Boot · fake carrier", "outbox relay (@Scheduled)"], True),
        ("notification-service", ["from Project 3", "consumer only"], True),
    ]
    for (name, lines, st), x in zip(services, cols):
        s.service(x, 380, cw, 100, name, lines, stretch=st)

    # one Postgres, schema per service
    for i in range(4):
        s.arrow([(centers[i], 480), (centers[i], 530)],
                "1 local tx: state + outbox row" if i == 0 else None,
                (centers[i] + 8, 509) if i == 0 else None, label_anchor="start")
    s.db(220, 530, 800, 100, "PostgreSQL · one server",
         ["schema per service, own login: orders · payments · inventory · shipping",
          "each schema: business tables + outbox + processed_events"])
    s.arrow([(centers[4], 480), (centers[4], 530)])
    s.db(1060, 530, 170, 100, "notifications", ["from Project 3"], stretch=True)

    # Debezium as the stretch alternative to the relay
    s.infra(210, 680, 820, 62, "Stretch: Kafka Connect + Debezium (replaces the polling relay)",
            ["reads the outbox via Postgres CDC (WAL) · Outbox Event Router SMT routes rows to topics"],
            fill="#F3E5F5", stroke="#8E24AA", stretch=True)
    s.arrow([(620, 630), (620, 680)], "CDC", (628, 660), dash=True, label_anchor="start")
    s.arrow([(1030, 711), (1265, 711), (1265, 261)], "publish", (1272, 600), dash=True, label_anchor="start")

    # KEDA
    s.infra(1310, 380, 195, 100, "KEDA", ["ScaledObject per consumer", "scales Deployments", "on consumer-group lag"],
            fill="#E1F5FE", stroke="#0277BD", stretch=True)
    s.arrow([(1310, 395), (1272, 262)], dash=True, label="reads lag", at=(1330, 330), label_anchor="start")
    s.arrow([(1310, 460), (1241, 460)], dash=True)

    s.legend(860, [("service", "Spring Boot service"), ("stretch", "Stretch (optional)"),
                   ("topic", "Kafka topic"), ("dlq", "Retry / DLQ topics"), ("db", "Database"),
                   ("infra", "Platform component"), ("ext", "External"), ("k8s", "Kubernetes boundary")])
    s.save("04-order-saga-architecture.svg")


# =====================================================================
# Project 4 — Order Saga (event flow)
# =====================================================================
def order_saga_flow():
    s = Svg(1260, 680, "Project 4 - Order Saga event flow")
    s.heading("Project 4 · Saga event flow and compensations")
    cols = [40, 290, 540, 790, 1040]
    w = 190
    cx = [c + w / 2 for c in cols]

    # happy path
    happy = [("OrderCreated", "order-service", False), ("PaymentAuthorized", "payment-service", False),
             ("StockReserved", "inventory-service", False), ("ShipmentScheduled", "shipping-service", True),
             ("OrderCompleted", "order-service · terminal", False)]
    for (n, e, st), c in zip(happy, cols):
        s.event(c, 110, w, n, e, kind="end" if n == "OrderCompleted" else "ok", stretch=st)
    s.rect(1040, 110, w, 52, "none", C["ok_stroke"], rx=10, sw=2.4)
    for i in range(4):
        s.arrow([(cols[i] + w, 136), (cols[i + 1], 136)])
    s.text(30, 95, "HAPPY PATH", size=11, weight="bold", fill=C["ok_stroke"], anchor="start")

    # core bypass
    s.arrow([(700, 110), (700, 78), (1100, 78), (1100, 109)], dash=True, color=C["ok_stroke"])
    s.text(900, 72, "core slice (no shipping): complete right after StockReserved", size=11,
           fill=C["ok_stroke"], halo=True)

    # failures
    s.text(30, 230, "FAILURES", size=11, weight="bold", fill=C["dlq_stroke"], anchor="start")
    fails = [(1, "PaymentFailed", "payment-service", "declined", False),
             (2, "StockUnavailable", "inventory-service", "out of stock", False),
             (3, "ShipmentFailed", "shipping-service", "carrier error", True)]
    for col, n, e, why, st in fails:
        s.arrow([(cols[col - 1] + w - 40, 162), (cols[col] + 20, 238)], why,
                (cols[col - 1] + w - 6, 205), label_anchor="start")
        s.event(cols[col], 240, w, n, e, kind="fail", stretch=st)

    # compensations
    s.text(30, 340, "COMPENSATIONS", size=11, weight="bold", fill=C["comp_stroke"], anchor="start")
    s.arrow([(cx[2], 292), (cx[2], 348)])
    s.event(cols[2], 350, w, "PaymentRefunded", "payment-service", kind="comp")
    s.arrow([(cx[3], 292), (cx[3], 348)])
    s.event(cols[3], 350, w, "StockReleased", "inventory-service", kind="comp", stretch=True)
    s.arrow([(cx[3] + 60, 292), (cx[4] - 40, 348)])
    s.event(cols[4], 350, w, "PaymentRefunded", "payment-service", kind="comp", stretch=True)

    # cancelled
    s.arrow([(cx[1], 292), (cx[1], 478)])
    for i in (2, 3, 4):
        s.arrow([(cx[i], 402), (cx[i], 478)])
    s.event(290, 480, 940, "OrderCancelled", "order-service · terminal · customer notified", kind="end")

    s.text(30, 575, "Also starts compensation (stretch): OrderCancelRequested by the customer before shipping (FR-8) "
                    "and the saga timeout (FR-9).", size=12, fill=C["muted"], anchor="start")
    s.text(30, 595, "All events are keyed by orderId, so every event of one saga lands on the same partition, in order.",
           size=12, fill=C["muted"], anchor="start")

    s.legend(645, [("ok", "Success event"), ("fail", "Failure event"), ("comp", "Compensation event"),
                   ("end", "Terminal state"), ("stretch", "Dashed = stretch")])
    s.save("04-order-saga-flow.svg")


# =====================================================================
# Project 5 — Banking Ledger
# =====================================================================
def banking_ledger():
    s = Svg(1770, 800, "Project 5 - Banking Ledger architecture")
    s.heading("Project 5 · Event-sourced Banking Ledger (CQRS)",
              "Kafka event log is the source of truth · read models are disposable and rebuilt by replay")
    s.boundary(190, 70, 1360, 670, "Kubernetes cluster (kind)",
               "namespace: ledger · all manifests deployed by Argo CD · default-deny NetworkPolicies")

    # ---- write side
    s.text(210, 150, "WRITE SIDE · commands", size=12, weight="bold", fill=C["k8s"], anchor="start")
    s.ext(25, 175, 130, 60, "Client", ["commands (HTTP)"])
    s.arrow([(155, 205), (220, 205)])
    s.service(220, 165, 180, 80, "command-api", ["Spring Boot · REST", "202 + commandId"])
    s.arrow([(400, 205), (440, 205)])
    s.topic(440, 188, 190, "account.commands", h=34)
    s.arrow([(630, 205), (670, 205)])
    s.service(670, 150, 240, 120, "account-processor",
              ["Kafka Streams · exactly_once_v2", "validates rules (no overdraft)",
               "state store = current account state", "single writer per accountId"])
    s.service(670, 290, 240, 64, "transfer-processor", ["Kafka Streams · transfer saga"], stretch=True)

    # ---- kafka
    s.band(950, 130, 270, 245, "Kafka (Strimzi) · mTLS + ACLs")
    s.topic(965, 160, 240, "account.events", h=46, sub="source of truth · retention ∞ · NOT compacted",
            bold=True)
    s.topic(965, 220, 240, "account.snapshots (compacted)", h=30, stretch=True)
    s.topic(965, 262, 240, "command.results (compacted)", h=30)
    s.topic(965, 304, 240, "transfer.events", h=30, stretch=True)
    s.text(1085, 360, "partition key = accountId", size=10.5, fill=C["muted"])
    s.arrow([(910, 183), (965, 183)], "events", (937, 176))
    s.arrow([(910, 235), (965, 235)], dash=True)
    s.arrow([(910, 262), (965, 277)])
    s.arrow([(910, 322), (965, 319)], dash=True, both=True)

    # command results back to command-api
    s.arrow([(1205, 277), (1236, 277), (1236, 395), (310, 395), (310, 246)],
            "command status → GET /commands/{id}", (700, 389))

    # ---- read side
    s.text(210, 440, "READ SIDE · projections & queries", size=12, weight="bold", fill=C["k8s"], anchor="start")
    cols = [380, 600, 820, 1040]
    cw = 200
    centers = [c + cw / 2 for c in cols]
    s.line([(1085, 375), (1085, 425)], dash=False)
    s.line([(centers[0], 425), (centers[-1], 425)], dash=False)
    s.text(centers[0], 418, "each projection consumes account.events · read_committed · its own consumer group",
           size=10.5, fill=C["muted"], anchor="start", halo=True)
    projections = [
        ("balance-projection", ["Spring Boot · @KafkaListener", "upsert by (accountId, version)"], False),
        ("statement-projection", ["Spring Boot · @KafkaListener", "running balance per txn"], True),
        ("audit-projection", ["Spring Boot · @KafkaListener", "incl. rejected commands"], True),
        ("new read model", ["added \"6 months later\"", "replay from offset 0 · blue/green"], True),
    ]
    stores = [("balances_v1", ["table · PostgreSQL"], False), ("statements", ["table · PostgreSQL"], True),
              ("audit", ["OpenSearch (or a table)"], True), ("new_model_v2", ["table · PostgreSQL"], True)]
    for (name, lines, st), (sn, sl, sst), x, c in zip(projections, stores, cols, centers):
        s.arrow([(c, 425), (c, 455)])
        s.service(x, 455, cw, 80, name, lines, stretch=st)
        s.arrow([(c, 535), (c, 573)])
        s.db(x + 20, 573, cw - 40, 82, sn, sl, stretch=sst)

    s.ext(25, 645, 130, 60, "Client", ["queries (HTTP)"])
    s.arrow([(155, 675), (220, 675)])
    s.service(220, 640, 180, 70, "query-api", ["Spring Boot · read-only"])
    s.line([(400, 690), (centers[-1], 690)], dash=False)
    for c in centers:
        s.arrow([(c, 690), (c, 657)])
    s.text(420, 712, "reads the active projection version (chosen in Git-managed config → switch / rollback)",
           size=10.5, fill=C["muted"], anchor="start")

    # ---- platform panel
    s.infra(1290, 130, 240, 90, "Argo CD", ["app-of-apps · auto-sync", "self-heals manual drift"],
            fill="#E8EAF6", stroke="#3949AB", stretch=True)
    s.ext(1595, 145, 150, 60, "Git repo", ["deploy/ manifests"])
    s.arrow([(1595, 175), (1532, 175)], "sync", (1574, 166))
    s.infra(1290, 250, 240, 130, "Security",
            ["Kafka mTLS: TLS listener + KafkaUser", "ACLs: only account-processor",
             "may write account.events", "default-deny NetworkPolicies"],
            fill="#FCE4EC", stroke="#AD1457", stretch=True)
    s.service(1290, 455, 240, 80, "invariant-checker",
              ["Spring Boot · K8s CronJob · reads stores", "money conserved · balance ≥ 0"])

    s.legend(770, [("service", "Spring Boot service"), ("stretch", "Stretch (optional)"),
                   ("topic", "Kafka topic"), ("db", "Read-model store"), ("infra", "Platform component"),
                   ("ext", "External"), ("k8s", "Kubernetes boundary")])
    s.save("05-banking-ledger-architecture.svg")

# =====================================================================
# Project 1 — Product Catalog (request-driven)
# =====================================================================
CLOUD = dict(fill="#E8EAF6", stroke="#3949AB")
RESIL = dict(fill="#FFF3E0", stroke="#EF6C00")


def product_catalog_phase_a():
    s = Svg(1500, 700, "Project 1 - Product Catalog Phase A")
    s.heading("Project 1 · Product Catalog · Phase A: classic Spring Cloud",
              "docker-compose · service registry · API gateway · config server · circuit breaker")
    s.boundary(170, 75, 1130, 560, "docker-compose network",
               "only the gateway port (8080) is published", color="#546E7A")

    # Spring Cloud infrastructure (top row)
    s.infra(470, 110, 220, 70, "discovery-server",
            ["Eureka · @EnableEurekaServer", "every service registers here"], **CLOUD)
    s.infra(760, 110, 220, 70, "config-server",
            ["Spring Cloud Config", "config for all services at startup"], stretch=True, **CLOUD)
    s.ext(1340, 115, 140, 60, "Git repo", ["config files"])
    s.arrow([(1340, 145), (981, 145)], "reads", (1160, 138))

    # request path
    s.ext(20, 340, 120, 60, "Client", ["browser / Postman"])
    s.arrow([(140, 370), (200, 370)], "/api/**", (170, 361))
    s.service(200, 325, 200, 90, "api-gateway",
              ["Spring Cloud Gateway", "routes lb://catalog-service", "public :8080"])
    s.arrow([(400, 370), (470, 370)])
    s.service(470, 325, 210, 90, "catalog-service",
              ["Spring Boot · REST + JPA", "builds the product page", "OpenFeign clients"])
    s.arrow([(680, 370), (710, 370)])
    s.infra(710, 340, 120, 60, "Resilience4j", ["timeout · breaker"], **RESIL)
    s.service(880, 230, 200, 80, "review-service", ["Spring Boot · REST + JPA", "Eureka client · ×3"])
    s.service(880, 440, 200, 80, "user-service", ["Spring Boot · REST + JPA", "Eureka client"])
    s.arrow([(830, 360), (880, 272)], "HTTP", (850, 305))
    s.arrow([(830, 380), (880, 478)], "HTTP", (850, 440))

    # one PostgreSQL server, one schema per service
    s.db(1115, 225, 165, 300, "PostgreSQL", ["one server", "schema per service:", "catalog", "reviews", "users",
                                             "(own login each)"])
    s.arrow([(1080, 270), (1114, 270)])
    s.arrow([(1080, 480), (1114, 480)])
    s.arrow([(575, 415), (575, 545), (1197, 545), (1197, 526)], label="catalog schema", at=(700, 539))

    # discovery lines
    s.arrow([(300, 325), (300, 145), (470, 145)], dash=True, label="lookup", at=(310, 240),
            label_anchor="start")
    s.arrow([(575, 325), (575, 181)], dash=True, both=True, label="register + lookup", at=(585, 255),
            label_anchor="start")
    s.arrow([(980, 230), (980, 205), (650, 205), (650, 181)], dash=True, label="register (heartbeat)",
            at=(815, 199))

    # optional infra
    s.db(225, 455, 150, 85, "Redis", ["gateway rate limits"], stretch=True)
    s.arrow([(300, 415), (300, 455)], dash=True)
    s.infra(880, 555, 200, 60, "Zipkin", ["traces from all services"], stretch=True, **CLOUD)

    s.legend(672, [("service", "Spring Boot service"), ("stretch", "Stretch (optional)"),
                   ("cloud", "Spring Cloud infra"), ("resil", "Resilience4j"), ("db", "Database"),
                   ("ext", "External"), ("compose", "docker-compose network")])
    s.save("01-product-catalog-phase-a.svg")


def product_catalog_phase_b():
    s = Svg(1500, 690, "Project 1 - Product Catalog Phase B")
    s.heading("Project 1 · Product Catalog · Phase B: same apps on Kubernetes",
              "Kubernetes replaces the plumbing (registry, config, load balancing), not the protection")
    s.boundary(170, 75, 1010, 550, "Kubernetes cluster (kind)",
               "namespace: catalog · no Eureka · no Config Server")

    s.infra(600, 110, 210, 64, "ConfigMaps + Secrets", ["→ env vars / application.yaml"],
            fill="#E1F5FE", stroke="#0277BD")
    s.line([(705, 174), (705, 285)])
    s.text(712, 235, "mounted into pods", size=10.5, fill=C["muted"], anchor="start")

    s.ext(20, 300, 120, 60, "Client", ["browser / Postman"])
    s.arrow([(140, 330), (200, 330)])
    s.infra(200, 290, 150, 80, "Ingress", ["or Gateway API", "public entry"], fill="#E1F5FE", stroke="#0277BD")
    s.arrow([(350, 330), (385, 330)])
    s.service(385, 285, 180, 90, "api-gateway", ["Spring Cloud Gateway", "optional on K8s", "Java filters (JWT…)"])
    s.arrow([(565, 330), (600, 330)])
    s.service(600, 285, 210, 90, "catalog-service",
              ["Spring Boot · RestClient", "http://review-service:8080", "http://user-service:8080"])
    s.arrow([(810, 330), (830, 330)])
    s.infra(830, 305, 100, 50, "Resilience4j", ["still needed"], **RESIL)
    s.text(1050, 190, "kube-dns name: review-service", size=10.5, fill=C["k8s"])
    s.service(950, 200, 200, 80, "review-service", ["Deployment ×3", "Service: review-service"])
    s.service(950, 390, 200, 80, "user-service", ["Deployment", "Service: user-service"])
    s.arrow([(930, 320), (950, 245)])
    s.arrow([(930, 340), (950, 425)])

    s.db(620, 450, 170, 95, "PostgreSQL", ["StatefulSet · one server", "schema per service"])
    s.arrow([(705, 375), (705, 450)])
    s.arrow([(950, 450), (791, 492)])
    s.arrow([(1150, 240), (1165, 240), (1165, 590), (730, 590), (730, 546)])

    # what was replaced
    x, y = 1210, 95
    s.rect(x, y, 270, 420, "#FAFAFA", "#9E9E9E", rx=12, sw=1.4)
    s.text(x + 135, y + 28, "What Kubernetes replaced", size=14, weight="bold")
    rows = [("Eureka", "Service + DNS"), ("Spring Cloud LoadBalancer", "Service (kube-proxy)"),
            ("Config Server", "ConfigMaps + Secrets")]
    yy = y + 62
    for old, new in rows:
        s.text(x + 18, yy, old, size=12.5, fill="#9E9E9E", anchor="start", strike=True)
        s.text(x + 18, yy + 19, "→ " + new, size=12.5, weight="bold", fill=C["k8s"], anchor="start")
        yy += 52
    s.text(x + 135, yy + 8, "Still needed", size=14, weight="bold")
    keep = [("Resilience4j", "app-level timeouts + breakers"),
            ("Spring Cloud Gateway", "only if you need Java filters")]
    yy += 38
    for name, why in keep:
        s.text(x + 18, yy, "✓ " + name, size=12.5, weight="bold", fill=C["svc_sub"], anchor="start")
        s.text(x + 34, yy + 18, why, size=11.5, fill=C["muted"], anchor="start")
        yy += 46
    s.text(x + 135, y + 400, "Replaces the plumbing, not the protection.", size=11.5,
           fill=C["text"], italic=True)

    s.legend(662, [("service", "Spring Boot service"), ("resil", "Resilience4j"),
                   ("k8sres", "Kubernetes resource"), ("db", "Database"), ("ext", "External"),
                   ("k8s", "Kubernetes boundary")])
    s.save("01-product-catalog-phase-b.svg")


# =====================================================================
# Project 2 — URL Shortener (sync hot path + async analytics)
# =====================================================================
def url_shortener():
    s = Svg(1500, 790, "Project 2 - URL Shortener architecture")
    s.heading("Project 2 · URL Shortener",
              "One stateless service for create + redirect (cache first) · clicks counted later through Kafka")
    s.boundary(170, 75, 1095, 650, "Kubernetes cluster (kind)", "namespace: shortener")

    # zones
    s.rect(400, 262, 530, 145, "#F1F8E9", "none", rx=14, sw=0)
    s.text(412, 279, "HOT PATH · sync · p95 < 20 ms", size=11.5, weight="bold", fill=C["ok_stroke"], anchor="start")
    s.rect(400, 435, 840, 265, "#FFF8EE", "none", rx=14, sw=0)
    s.text(415, 688, "ANALYTICS · async · counted seconds later", size=11.5, weight="bold",
           fill="#BF5B00", anchor="start")

    # entry
    s.ext(20, 300, 120, 70, "Client", ["browser / API"])
    s.arrow([(140, 335), (200, 335)])
    s.infra(200, 280, 140, 110, "Ingress", ["/links → shortener", "/{code} → shortener", "/stats → analytics"],
            fill="#E1F5FE", stroke="#0277BD")
    s.arrow([(340, 340), (420, 340)])

    # the one service
    s.service(420, 290, 210, 100, "shortener-service",
              ["Spring Boot · HPA 2–10 pods", "POST /links · GET /{code} → 302", "fires click event (async)"])
    s.arrow([(480, 290), (480, 150), (740, 150)], "save new link", (610, 143))
    s.db(740, 105, 170, 90, "PostgreSQL", ["links schema"])
    s.arrow([(630, 330), (740, 330)], "1 lookup", (685, 323))
    s.db(740, 295, 170, 90, "Redis", ["cache-aside · TTL 1 h"])
    s.arrow([(615, 290), (615, 240), (825, 240), (825, 196)], dash=True,
            label="2 on cache miss: read DB, fill cache", at=(720, 234))

    # kafka + analytics
    s.band(420, 465, 490, 110, "Kafka (Strimzi)")
    s.topic(440, 500, 450, "links.click.events", h=34, bold=True)
    s.text(665, 558, "key = code · batched + compressed · 6 partitions", size=10.5, fill=C["muted"])
    s.arrow([(525, 390), (525, 499)], "3 send async (never waits)", (535, 445), label_anchor="start")
    s.arrow([(910, 517), (990, 517)], "consume", (950, 510))
    s.service(990, 470, 210, 100, "analytics-service",
              ["Spring Boot · batch @KafkaListener", "counts per link / minute", "GET /links/{code}/stats"])
    s.arrow([(1095, 570), (1095, 600)])
    s.db(1020, 600, 150, 80, "PostgreSQL", ["stats schema (same server)"])
    s.arrow([(270, 390), (270, 712), (1240, 712), (1240, 520), (1201, 520)], dash=True,
            label="GET /links/{code}/stats", at=(700, 706))

    # memory panel
    x, y = 1290, 95
    s.rect(x, y, 190, 380, "#FAFAFA", "#9E9E9E", rx=12, sw=1.4)
    s.text(x + 95, y + 30, "Remember", size=14, weight="bold")
    lines = [("Redirect now,", True), ("count later.", True), ("", False),
             ("Cache what's read,", True), ("stream what's written.", True), ("", False),
             ("Kafka down?", False), ("Redirects still work.", False), ("", False),
             ("One service until", False), ("you need two.", False)]
    yy = y + 70
    for ln, bold in lines:
        if ln:
            s.text(x + 95, yy, ln, size=12.5, weight="bold" if bold else "normal",
                   fill=C["text"] if bold else C["muted"])
        yy += 24

    s.legend(760, [("service", "Spring Boot service"), ("k8sres", "Kubernetes resource"),
                   ("topic", "Kafka topic"), ("db", "Database / cache"), ("ext", "External"),
                   ("k8s", "Kubernetes boundary")])
    s.save("02-url-shortener-architecture.svg")


# =====================================================================
# Sequence diagrams (one per project)
# =====================================================================
PART_STYLE = {
    "user": (C["ext_fill"], C["ext_stroke"], True),
    "svc": (C["svc_fill"], C["svc_stroke"], False),
    "kafka": (C["topic_fill"], C["topic_stroke"], False),
    "db": (C["db_fill"], C["db_stroke"], False),
    "cloud": ("#E8EAF6", "#3949AB", False),
}
SECTION_STYLE = {"fail": ("#FFEBEE", "#C62828"), "alt": ("#FFFDE7", "#F9A825"), "info": ("#F3F6FA", "#546E7A")}
ROW, SEC = 36, 34


def sequence(fname, title, subtitle, parts, steps, col_w=200, footer=None):
    n = len(parts)
    xs = {k: 120 + i * col_w for i, (k, *_rest) in enumerate(parts)}
    W = 120 + col_w * (n - 1) + 300
    # height
    h = 165
    for st in steps:
        h += SEC if st[0] == "section" else (8 if st[0] == "end" else ROW)
    H = h + (95 if footer else 70)
    s = Svg(W, H, title)
    s.heading(title, subtitle)

    # participants + lifelines
    for k, label, kind, *sub in parts:
        x = xs[k]
        f, st_, dash = PART_STYLE[kind]
        bw = min(col_w - 16, 180)
        s.line([(x, 132), (x, h + 5)], dash=True, color="#B0BEC5")
        s.rect(x - bw / 2, 80, bw, 52, f, st_, rx=10, dash=dash, sw=2)
        if sub:
            s.text(x, 102, label, size=13, weight="bold")
            s.text(x, 120, sub[0], size=10.5, fill=C["muted"])
        else:
            s.text(x, 111, label, size=13, weight="bold")

    y = 165
    sec_start = None
    for st in steps:
        kind = st[0]
        if kind == "section":
            sk, stitle = st[1], st[2]
            sec_start = (y, sk)
            fill, stroke = SECTION_STYLE[sk]
            s.text(34, y + 21, stitle, size=12, weight="bold", fill=stroke, anchor="start")
            y += SEC
            continue
        if kind == "end":
            y0, sk = sec_start
            fill, stroke = SECTION_STYLE[sk]
            s.bg.append(f'<rect x="20" y="{y0}" width="{W - 40}" height="{y - y0 + 4}" rx="10" '
                        f'fill="{fill}" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="6 4"/>')
            y += 8
            continue
        cy = y + ROW - 12
        if kind == "note":
            x = xs[st[1]]
            w = 6.4 * len(st[2]) + 18
            s.rect(x + 8, cy - 15, w, 24, "#FFFDE7", "#FBC02D", rx=5, sw=1.2)
            s.text(x + 17, cy + 1, st[2], size=11.5, anchor="start")
        else:
            a, b, label = xs[st[1]], xs[st[2]], st[3]
            d = 1 if b > a else -1
            color, mk, dash, lc = {
                "call": (C["arrow"], "url(#arrow)", "", C["text"]),
                "reply": ("#78909C", "url(#mk-grey)", ' stroke-dasharray="6 4"', C["muted"]),
                "event": ("#EF6C00", "url(#mk-orange)", "", "#BF5B00"),
                "fail": ("#C62828", "url(#mk-red)", "", "#C62828"),
            }[kind]
            s.els.append(f'<line x1="{a}" y1="{cy}" x2="{b - d * 3}" y2="{cy}" stroke="{color}" '
                         f'stroke-width="1.8"{dash} marker-end="{mk}"/>')
            s.text((a + b) / 2, cy - 6, label, size=11.5, fill=lc, halo=True,
                   weight="bold" if kind != "reply" else "normal")
        y += ROW

    ly = h + 40
    if footer:
        s.text(30, h + 30, footer, size=12, fill=C["muted"], anchor="start")
        ly = h + 65
    # legend
    lx = 30
    for kind, label in [("call", "call (waits)"), ("reply", "reply"), ("event", "Kafka event (async)"),
                        ("fail", "failure"), ("note", "inside the service")]:
        if kind == "note":
            s.rect(lx, ly - 11, 34, 18, "#FFFDE7", "#FBC02D", rx=4, sw=1.2)
        else:
            color, mk, dash = {"call": (C["arrow"], "url(#arrow)", ""),
                               "reply": ("#78909C", "url(#mk-grey)", ' stroke-dasharray="6 4"'),
                               "event": ("#EF6C00", "url(#mk-orange)", ""),
                               "fail": ("#C62828", "url(#mk-red)", "")}[kind]
            s.els.append(f'<line x1="{lx}" y1="{ly - 2}" x2="{lx + 32}" y2="{ly - 2}" stroke="{color}" '
                         f'stroke-width="1.8"{dash} marker-end="{mk}"/>')
        s.text(lx + 42, ly + 2, label, size=12, anchor="start")
        lx += 42 + int(6.6 * len(label)) + 30
    s.save(fname)


def seq_product_catalog():
    sequence("01-product-catalog-sequence.svg", "Project 1 · Flow: open a product page",
             "Synchronous calls through the gateway · timeout + circuit breaker protect the page",
             [("user", "User", "user"), ("gw", "api-gateway", "svc"), ("eureka", "Eureka", "cloud", "registry"),
              ("cat", "catalog-service", "svc"), ("rev", "review-service", "svc"), ("usr", "user-service", "svc")],
             [("call", "user", "gw", "1. GET /api/catalog/products/42/page"),
              ("call", "gw", "eureka", "2. where is catalog-service?"),
              ("reply", "eureka", "gw", "10.1.0.7, 10.1.0.8"),
              ("call", "gw", "cat", "3. GET /products/42/page"),
              ("note", "cat", "4. load product 42 (catalog schema)"),
              ("call", "cat", "rev", "5. GET /reviews?productId=42 (1 s timeout)"),
              ("reply", "rev", "cat", "2 reviews by users 7 and 9"),
              ("call", "cat", "usr", "6. GET /users?ids=7,9"),
              ("reply", "usr", "cat", "names"),
              ("note", "cat", "7. merge product + reviews + names"),
              ("reply", "cat", "user", "8. 200 product page"),
              ("section", "fail", "IF review-service is slow or down"),
              ("fail", "cat", "rev", "5. GET /reviews …  ✗ no answer within 1 s"),
              ("note", "cat", "fallback: reviews = []"),
              ("note", "cat", "5 of 10 calls failed → breaker OPEN: skip review-service for 10 s"),
              ("reply", "cat", "user", "200 page · reviewsAvailable: false"),
              ("end",)],
             col_w=210)


def seq_url_shortener():
    sequence("02-url-shortener-sequence.svg", "Project 2 · Flow: create, click, count",
             "One service answers from cache right away · the click is counted later through Kafka",
             [("user", "User", "user"), ("app", "shortener-service", "svc"),
              ("redis", "Redis", "db", "cache"), ("pg", "PostgreSQL", "db", "links schema"),
              ("kafka", "Kafka", "kafka", "links.click.events"), ("ana", "analytics-service", "svc")],
             [("section", "info", "A · Create a short link"),
              ("call", "user", "app", "1. POST /links {url}"),
              ("call", "app", "pg", "2. save abc123 → url"),
              ("reply", "app", "user", "201 {shortUrl: /abc123}"),
              ("end",),
              ("section", "info", "B · Click the link (hot path)"),
              ("call", "user", "app", "3. GET /abc123"),
              ("call", "app", "redis", "4. GET abc123"),
              ("reply", "redis", "app", "hit: url"),
              ("reply", "app", "user", "5. 302 Location: url"),
              ("event", "app", "kafka", "6. LinkClicked (async, never waits)"),
              ("event", "kafka", "ana", "7. batch of clicks"),
              ("note", "ana", "8. clicks += n (stats schema)"),
              ("end",),
              ("section", "alt", "IF the code is not in the cache (miss)"),
              ("reply", "redis", "app", "miss"),
              ("call", "app", "pg", "read abc123"),
              ("reply", "pg", "app", "url"),
              ("call", "app", "redis", "SET abc123 (TTL 1 h)"),
              ("end",),
              ("section", "info", "C · See the stats"),
              ("call", "user", "ana", "9. GET /links/abc123/stats"),
              ("reply", "ana", "user", "200 {clicks: 1}"),
              ("end",)],
             col_w=210)


def seq_notification_hub():
    sequence("03-notification-hub-sequence.svg", "Project 3 · Flow: order shipped → email",
             "Publish once · the router fans out · workers deliver once, retry, then dead-letter",
             [("cli", "Client", "user", "upstream service"), ("prod", "event-producer", "svc"),
              ("kafka", "Kafka", "kafka", "topics"), ("noti", "notification-service", "svc"),
              ("pg", "PostgreSQL", "db", "prefs · status"), ("mail", "email-worker", "svc"),
              ("smtp", "SMTP stub", "user", "provider")],
             [("call", "cli", "prod", "1. POST /events OrderShipped (user 7)"),
              ("event", "prod", "kafka", "2. orders.order.events (key = user 7)"),
              ("reply", "prod", "cli", "202 Accepted"),
              ("event", "kafka", "noti", "3. OrderShipped"),
              ("call", "noti", "pg", "4. preferences of user 7?"),
              ("reply", "pg", "noti", "email ✓ push ✓ sms ✗"),
              ("event", "noti", "kafka", "5. email.commands + push.commands"),
              ("event", "kafka", "mail", "6. SendEmail (id = eventId + email)"),
              ("call", "mail", "pg", "7. already SENT?"),
              ("reply", "pg", "mail", "no"),
              ("call", "mail", "smtp", "8. send email"),
              ("reply", "smtp", "mail", "OK"),
              ("call", "mail", "pg", "9. status = SENT"),
              ("note", "mail", "10. commit offset"),
              ("section", "fail", "IF the provider keeps failing"),
              ("fail", "mail", "smtp", "send ✗ (retries: 200 ms, 1 s, 5 s)"),
              ("event", "mail", "kafka", "notifications.dlq (+ error headers)"),
              ("call", "mail", "pg", "status = FAILED"),
              ("end",),
              ("section", "alt", "IF the same command arrives twice"),
              ("call", "mail", "pg", "already SENT?"),
              ("reply", "pg", "mail", "yes → skip, just commit"),
              ("end",)],
             col_w=200)


def seq_order_saga():
    sequence("04-order-saga-sequence.svg", "Project 4 · Flow: place an order",
             "Each service saves data + event in one DB transaction (outbox) · a polling relay publishes it to Kafka",
             [("cus", "Customer", "user"), ("ord", "order-service", "svc"),
              ("kafka", "Kafka", "kafka", "via outbox relay"),
              ("pay", "payment-service", "svc"), ("inv", "inventory-service", "svc")],
             [("call", "cus", "ord", "1. POST /orders (Idempotency-Key)"),
              ("note", "ord", "2. one tx: order PENDING + outbox OrderCreated"),
              ("reply", "ord", "cus", "202 {orderId}"),
              ("event", "ord", "kafka", "3. OrderCreated"),
              ("event", "kafka", "pay", "4. OrderCreated"),
              ("note", "pay", "5. authorize · one tx: payment + outbox"),
              ("event", "pay", "kafka", "6. PaymentAuthorized"),
              ("event", "kafka", "inv", "7. PaymentAuthorized"),
              ("note", "inv", "8. reserve stock · one tx: stock + outbox"),
              ("event", "inv", "kafka", "9. StockReserved"),
              ("event", "kafka", "ord", "10. StockReserved"),
              ("note", "ord", "11. status = COMPLETED"),
              ("call", "cus", "ord", "12. GET /orders/{id}"),
              ("reply", "ord", "cus", "COMPLETED + timeline"),
              ("section", "fail", "IF stock is unavailable → compensate (undo the payment)"),
              ("note", "inv", "8. no stock → outbox StockUnavailable"),
              ("event", "inv", "kafka", "9. StockUnavailable"),
              ("event", "kafka", "pay", "10. StockUnavailable"),
              ("note", "pay", "11. refund → outbox PaymentRefunded"),
              ("event", "pay", "kafka", "12. PaymentRefunded"),
              ("event", "kafka", "ord", "13. PaymentRefunded"),
              ("note", "ord", "14. status = CANCELLED"),
              ("end",)],
             col_w=230,
             footer="Every consumer first checks its processed_events table, so a duplicate event changes nothing.")


def seq_banking_ledger():
    sequence("05-banking-ledger-sequence.svg", "Project 5 · Flow: withdraw money",
             "Commands ask · the processor decides · events are facts · projections answer queries",
             [("cus", "Customer", "user"), ("api", "command-api", "svc"), ("kafka", "Kafka", "kafka", "commands · events"),
              ("proc", "account-processor", "svc", "Kafka Streams"), ("proj", "balance-projection", "svc"),
              ("db", "balances DB", "db"), ("q", "query-api", "svc")],
             [("call", "cus", "api", "1. POST /accounts/A/withdrawals {100}"),
              ("event", "api", "kafka", "2. WithdrawMoney (key = A)"),
              ("reply", "api", "cus", "202 {commandId}"),
              ("event", "kafka", "proc", "3. WithdrawMoney"),
              ("note", "proc", "4. state store: balance 500 ≥ 100 ✓"),
              ("event", "proc", "kafka", "5. one Kafka tx: MoneyWithdrawn + ACCEPTED"),
              ("event", "kafka", "proj", "6. MoneyWithdrawn"),
              ("call", "proj", "db", "7. balance = 400 (version 12)"),
              ("event", "kafka", "api", "8. command.results: ACCEPTED"),
              ("call", "cus", "api", "9. GET /commands/{id}"),
              ("reply", "api", "cus", "ACCEPTED"),
              ("call", "cus", "q", "10. GET /accounts/A/balance"),
              ("call", "q", "db", "read A"),
              ("reply", "q", "cus", "400 (version 12)"),
              ("section", "fail", "IF funds are too low"),
              ("note", "proc", "4. balance 50 < 100 ✗"),
              ("event", "proc", "kafka", "5. CommandRejected + REJECTED"),
              ("call", "cus", "api", "GET /commands/{id}"),
              ("reply", "api", "cus", "REJECTED: insufficient funds"),
              ("end",),
              ("section", "alt", "REBUILD a read model (any time)"),
              ("event", "kafka", "proj", "replay account.events from offset 0 → balances_v2"),
              ("end",)],
             col_w=200)


if __name__ == "__main__":
    seq_product_catalog()
    seq_url_shortener()
    seq_notification_hub()
    seq_order_saga()
    seq_banking_ledger()
    product_catalog_phase_a()
    product_catalog_phase_b()
    url_shortener()
    notification_hub()
    order_saga_architecture()
    order_saga_flow()
    banking_ledger()
