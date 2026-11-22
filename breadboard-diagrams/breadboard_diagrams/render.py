"""Shared vector scene, SVG writer and optional PNG/PDF exporters.

SVG and validation need only Python's standard library. PNG uses Pillow; PDF
uses ReportLab. Scene coordinates are independent of the export resolution.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import csv
from pathlib import Path

from .model import Circuit

INK = "#173044"
MUTED = "#5B7081"
BG = "#F4F7F7"
LINE = "#CFDADF"


def font_path(weight="regular"):
    name = {"regular": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf",
            "mono": "DejaVuSansMono.ttf"}[weight]
    roots = [Path(os.environ.get("BREADBOARD_FONT_DIR", "/usr/share/fonts/truetype/dejavu")),
             Path("/usr/local/share/fonts"), Path("/usr/share/fonts/dejavu")]
    for root in roots:
        candidate = root / name
        if candidate.is_file():
            return candidate
    raise RuntimeError(f"Install fonts-dejavu-core or set BREADBOARD_FONT_DIR; missing {name}")


class Scene:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.elements = []

    def rect(self, x, y, width, height, fill, stroke=None, sw=1, radius=0):
        self.elements.append(dict(kind="rect", x=x, y=y, width=width, height=height,
                                  fill=fill, stroke=stroke, sw=sw, radius=radius))

    def circle(self, x, y, radius, fill, stroke=None, sw=1):
        self.elements.append(dict(kind="circle", x=x, y=y, radius=radius,
                                  fill=fill, stroke=stroke, sw=sw))

    def path(self, points, color, width=1):
        self.elements.append(dict(kind="path", points=list(points), color=color, width=width))

    def text(self, x, y, value, size=20, color=INK, weight="regular", anchor="start"):
        self.elements.append(dict(kind="text", x=x, y=y, value=str(value), size=size,
                                  color=color, weight=weight, anchor=anchor))

    def svg(self, title="Breadboard wiring diagram"):
        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img">',
                 f'<title>{html.escape(title)}</title>',
                 '<desc>Top-view breadboard assembly drawing. Refer to the generated wiring table and validation report.</desc>']
        for e in self.elements:
            kind = e["kind"]
            if kind in ("rect", "circle"):
                style = f'fill="{e["fill"] or "none"}" stroke="{e["stroke"] or "none"}" stroke-width="{e["sw"]}"'
                if kind == "rect":
                    lines.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["width"]}" height="{e["height"]}" rx="{e["radius"]}" {style}/>')
                else:
                    lines.append(f'<circle cx="{e["x"]}" cy="{e["y"]}" r="{e["radius"]}" {style}/>')
            elif kind == "path":
                points = " ".join(f"{x},{y}" for x, y in e["points"])
                lines.append(f'<polyline points="{points}" fill="none" stroke="{e["color"]}" stroke-width="{e["width"]}" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                family = "DejaVu Sans Mono, monospace" if e["weight"] == "mono" else "DejaVu Sans, sans-serif"
                weight = "700" if e["weight"] == "bold" else "400"
                lines.append(f'<text x="{e["x"]}" y="{e["y"]}" fill="{e["color"]}" font-family="{family}" font-size="{e["size"]}" font-weight="{weight}" text-anchor="{e["anchor"]}">{html.escape(e["value"])}</text>')
        return "\n".join([*lines, "</svg>", ""])

    def png(self, path, scale=2):
        from PIL import Image, ImageDraw, ImageFont
        im = Image.new("RGB", (round(self.width * scale), round(self.height * scale)), "white")
        draw = ImageDraw.Draw(im)
        fonts = {}
        def box(x, y, w, h):
            return tuple(round(v * scale) for v in (x, y, x + w, y + h))
        for e in self.elements:
            if e["kind"] == "rect":
                draw.rounded_rectangle(box(e["x"], e["y"], e["width"], e["height"]),
                                       radius=round(e["radius"] * scale), fill=e["fill"],
                                       outline=e["stroke"], width=max(1, round(e["sw"] * scale)))
            elif e["kind"] == "circle":
                r = e["radius"]
                draw.ellipse(box(e["x"] - r, e["y"] - r, 2 * r, 2 * r), fill=e["fill"],
                             outline=e["stroke"], width=max(1, round(e["sw"] * scale)))
            elif e["kind"] == "path":
                points = [(round(x * scale), round(y * scale)) for x, y in e["points"]]
                width = max(1, round(e["width"] * scale))
                draw.line(points, fill=e["color"], width=width, joint="curve")
                for x, y in points:
                    draw.ellipse((x-width/2, y-width/2, x+width/2, y+width/2), fill=e["color"])
            else:
                key = (e["weight"], round(e["size"] * scale))
                if key not in fonts:
                    fonts[key] = ImageFont.truetype(str(font_path(key[0])), key[1])
                anchor = {"start": "ls", "middle": "ms", "end": "rs"}[e["anchor"]]
                draw.text((e["x"] * scale, e["y"] * scale), e["value"], font=fonts[key],
                          fill=e["color"], anchor=anchor)
        im.save(path, optimize=True)

    def pdf(self, path, title="Breadboard diagram"):
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.colors import HexColor
        for weight in ("regular", "bold", "mono"):
            name = "Breadboard-" + weight
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(font_path(weight))))
        # A scalable vector illustration artboard; print with Fit to Page.
        c = canvas.Canvas(str(path), pagesize=(self.width / 2, self.height / 2), invariant=1)
        c.setTitle(title)
        c.setAuthor("Breadboard Diagrams")
        c.scale(0.5, 0.5)
        for e in self.elements:
            kind = e["kind"]
            if kind in ("rect", "circle"):
                if e["fill"]:
                    c.setFillColor(HexColor(e["fill"]))
                if e["stroke"]:
                    c.setStrokeColor(HexColor(e["stroke"]))
                c.setLineWidth(e["sw"])
                if kind == "rect":
                    c.roundRect(e["x"], self.height-e["y"]-e["height"], e["width"], e["height"],
                                e["radius"], fill=bool(e["fill"]), stroke=bool(e["stroke"]))
                else:
                    c.circle(e["x"], self.height-e["y"], e["radius"],
                             fill=bool(e["fill"]), stroke=bool(e["stroke"]))
            elif kind == "path":
                c.setStrokeColor(HexColor(e["color"]))
                c.setLineWidth(e["width"])
                c.setLineCap(1)
                c.setLineJoin(1)
                p = c.beginPath()
                p.moveTo(e["points"][0][0], self.height-e["points"][0][1])
                for x, y in e["points"][1:]:
                    p.lineTo(x, self.height-y)
                c.drawPath(p)
            else:
                c.setFont("Breadboard-" + e["weight"], e["size"])
                c.setFillColor(HexColor(e["color"]))
                method = {"start": c.drawString, "middle": c.drawCentredString, "end": c.drawRightString}[e["anchor"]]
                method(e["x"], self.height-e["y"], e["value"])
        c.showPage()
        c.save()


def source_hash(circuit):
    digest = hashlib.sha256()
    digest.update(json.dumps(circuit.data, sort_keys=True).encode())
    for name, part in sorted(circuit.parts.items()):
        digest.update(name.encode())
        digest.update(json.dumps(part, sort_keys=True).encode())
    return digest.hexdigest()


def draw_board(scene, circuit, board):
    definition = board["definition"]
    x, y = board["origin"]
    p = board["pitch"]
    width = definition["column_pitch_units"][-1] * p
    height = (definition["rows"] - 1) * p
    scene.text(x, y-42, board["label"], 21, weight="bold")
    scene.rect(x-20, y-20, width+40, height+40, "#FFFFFF", "#A8BCC8", 2, 16)
    scene.rect(x+4.55*p, y-5, 1.9*p, height+10, BG, radius=8)
    for column in definition["columns"]:
        cx, _ = circuit.xy(f'{board["id"]}:{column}1')
        scene.text(cx, y-28, column, 14, MUTED, "bold", "middle")
    for row in range(1, definition["rows"]+1):
        for strip in definition["connected_strips"]:
            first = circuit.xy(f'{board["id"]}:{strip[0]}{row}')
            last = circuit.xy(f'{board["id"]}:{strip[-1]}{row}')
            scene.path([first, last], "#E8EDEF", 2)
        for column in definition["columns"]:
            cx, cy = circuit.xy(f'{board["id"]}:{column}{row}')
            scene.circle(cx, cy, 4, "#B5C3CD")


def draw_module(scene, circuit, instance):
    part = instance["definition"]
    board = circuit.boards[instance["board"]]
    p = board["pitch"]
    refs = [f'{instance["id"]}.{pin}' for header in part["headers"] for pin in header["pins"]]
    xy = [circuit.xy(ref) for ref in refs]
    left, right = min(x for x, y in xy), max(x for x, y in xy)
    top, bottom = min(y for x, y in xy), max(y for x, y in xy)
    dongle = instance["part"] == "nordic-pca10059"
    overhang = 1.7*p if dongle else 0.7*p
    scene.rect(left-14, top-overhang, right-left+28, bottom-top+overhang+24,
               part["fill"], "#102B38", 2, 10)
    if dongle:
        scene.rect(left+2, top-overhang+8, right-left-4, 20, "#86A986", radius=4)
        scene.text((left+right)/2, top-overhang+23, "ANTENNA / KEEP CLEAR", 9, "#163F2C", "bold", "middle")
        scene.text((left+right)/2, bottom+19, "PCA10059", 13, "#FFFFFF", "bold", "middle")
        scene.rect((left+right)/2-25, top+95, 50, 63, "#153B34", "#578878", 1, 3)
        scene.text((left+right)/2, top+120, "nRF", 15, "#D6E7DC", "bold", "middle")
        scene.text((left+right)/2, top+142, "52840", 12, "#D6E7DC", "mono", "middle")
        ux, uy = (left+right)/2-54, bottom+24
        scene.rect(ux, uy, 108, 109, "#B7C4CA", "#566D7C", 2, 4)
        scene.rect(ux+11, uy+76, 86, 18, "#7B909C", radius=2)
        scene.text(ux+54, uy+45, "USB-A", 18, INK, "bold", "middle")
        scene.path([(ux+54, uy+109), (ux+54, uy+160)], "#354B5B", 16)
        scene.text(ux+54, uy+193, "ONE USB CABLE", 21, INK, "bold", "middle")
        scene.text(ux+54, uy+220, "power + optional data", 17, MUTED, anchor="middle")
    else:
        scene.text(left+46, top+17, "TB6612", 15, "#FFFFFF", "bold", "middle")
        scene.rect((left+right)/2-21, top+96, 42, 70, "#112D40", "#668395", 1, 3)
    expected = circuit.data.get("expected_nets", {})
    for ref in refs:
        x, y = circuit.xy(ref)
        pin = ref.split(".", 1)[1]
        used = ref in expected
        scene.circle(x, y, 6, "#FFDB8A" if used else "#91A6AA", "#153B44", 0.5)
        side = "start" if x == left else "end"
        label = pin.replace("GND_A", "GND").replace("GND_B", "GND").replace("GND_C", "GND")
        label = label.replace("VDD_OUT", "VDD OUT").replace("AOUT", "A").replace("BOUT", "B")
        if dongle and pin.startswith("P"):
            label = pin[1:]
        scene.text(x+12 if side == "start" else x-12, y+4, label, 11.5,
                   "#FFFFFF" if used else "#B1C3C6", "bold" if used else "regular", side)


def draw_external(scene, instance):
    x, y = instance["origin"]
    width, height = instance["size"]
    scene.rect(x, y, width, height, "#DCE6E9", "#8DA3AF", 2, 20)
    scene.text(x+width/2, y+40, "FADER", 23, INK, "bold", "middle")
    scene.text(x+width/2, y+69, "Adafruit 5466", 16, MUTED, anchor="middle")
    scene.text(x+width/2, y+96, "100 mm / 10 kohm", 14, MUTED, anchor="middle")
    scene.path([(x+width/2, y+150), (x+width/2, y+height-230)], "#718996", 12)
    scene.rect(x+width/2-28, y+470, 56, 78, INK, radius=8)
    for pin, xy in instance["ports"].items():
        if pin == "TOUCH":
            continue
        color = "#89417D" if pin in ("M1", "M2") else "#42586B" if pin == "POT_LOW" else "#17836D"
        scene.circle(*xy, 6, color)
        label = {"M1": "M1", "M2": "M2", "WIPER": "B / WIPER", "POT_LOW": "A / POT-", "POT_HIGH": "C / POT+"}[pin]
        scene.text(x+width-12, xy[1]-10, label, 14, color, "bold", "end")


def draw_sidebar(scene, circuit):
    x, width = 975, 670
    scene.rect(x, 243, width, 1245, "#FFFFFF", "#D0DBDF", 1.5, 18)
    for block in circuit.data.get("sidebar", []):
        y = block["y"]
        scene.text(x+28, y, block["title"], 21, INK, "bold")
        if block["type"] == "text":
            for index, line in enumerate(block["lines"]):
                scene.text(x+28, y+34+index*28, line, 18, MUTED)
        else:
            scene.path([(x+28, y+20), (x+width-28, y+20)], LINE, 1)
            rows = [w for w in circuit.data["wires"] if w.get("group") == block["group"]]
            for index, wire in enumerate(rows):
                row_y = y+59+index*block["row_height"]
                color = wire["color"]
                if wire["group"] == "jumpers":
                    scene.rect(x+28, row_y-19, 34, 26, color, radius=5)
                    scene.text(x+45, row_y, wire["id"], 14, "#FFFFFF", "bold", "middle")
                    label_x = x+76
                    route_label = f'{wire["from"]} > {wire["to"]}'
                else:
                    label_x = x+28
                    route_label = wire["to"]
                scene.text(label_x, row_y, wire["label"], 18, color, "bold")
                scene.text(x+width-28, row_y, route_label, 18, INK, "mono", "end")
                scene.text(label_x, row_y+24, wire["pins"], 16, MUTED)


def build_scene(circuit):
    circuit.validate()
    data = circuit.data
    scene = Scene(*data["canvas"])
    scene.rect(0, 0, scene.width, scene.height, BG)
    scene.rect(60, 53, 78, 7, "#17836D", radius=3)
    scene.text(60, 124, data["title"], 54, weight="bold")
    scene.text(60, 169, data["subtitle"], 25, MUTED)
    scene.text(60, 204, data["strapline"], 22, MUTED)
    scene.rect(1375, 74, 270, 56, "#E0EFE9", radius=12)
    scene.text(1510, 110, data.get("badge", f'REVISION {data["revision"]}'), 18, "#176451", "bold", "middle")
    for board in circuit.boards.values():
        draw_board(scene, circuit, board)
    for instance in circuit.instances.values():
        if instance["definition"]["kind"] == "module":
            draw_module(scene, circuit, instance)
        else:
            draw_external(scene, instance)
    for passive in data.get("passives", []):
        a, b = circuit.xy(passive["a"]), circuit.xy(passive["b"])
        scene.path([a, b], passive["color"], 3)
        mid_x, mid_y = (a[0]+b[0])/2, (a[1]+b[1])/2
        scene.rect(mid_x-7, mid_y-20, 14, 40, "#E8DEC0", "#8D875F", 1.5, 5)
        for offset in (-10, 0, 10):
            scene.path([(mid_x-6, mid_y+offset), (mid_x+6, mid_y+offset)], "#8C6252", 3)
        scene.text(mid_x-18, mid_y+5, passive["id"], 14, "#657546", "bold", "end")
        scene.circle(*a, 5, passive["color"])
        scene.circle(*b, 5, passive["color"])
    for wire in data.get("wires", []):
        points = circuit.route(wire)
        # A pale halo makes insulated crossings legible. Only endpoints have dots.
        scene.path(points, BG, wire["width"]+5)
        scene.path(points, wire["color"], wire["width"])
        for endpoint in (points[0], points[-1]):
            scene.circle(*endpoint, 6, wire["color"], "#FFFFFF", 1)
        if "badge" in wire:
            x, y = wire["badge"]
            scene.rect(x-17, y-11, 34, 22, wire["color"], radius=5)
            scene.text(x, y+5, wire["id"], 13, "#FFFFFF", "bold", "middle")
    # Row-number knockouts keep labels aligned with their actual holes even
    # where an insulated pigtail crosses the outside numbering margin.
    for board in circuit.boards.values():
        x, y = board["origin"]
        for row in range(1, board["definition"]["rows"]+1):
            cy = y+(row-1)*board["pitch"]
            scene.rect(x-47, cy-9, 24, 19, BG, radius=2)
            scene.text(x-27, cy+5, str(row), 12, MUTED, "mono", "end")
    scene.text(95, 1365, "TOP VIEW", 18, INK, "bold")
    scene.text(95, 1394, "Gold pads = module pins.", 17, MUTED)
    scene.text(95, 1423, "Crossings without dots do not join.", 17, MUTED)
    scene.text(95, 1452, "Part bodies are stylized.", 17, MUTED)
    draw_sidebar(scene, circuit)
    for index, card in enumerate(data.get("footer_cards", [])):
        x, y = 60+index*535, 1540
        scene.rect(x, y, 515, 150, "#FFFFFF", LINE, 1, 13)
        scene.rect(x, y, 5, 150, card["color"], radius=2)
        scene.text(x+22, y+34, card["title"], 19, card["color"], "bold")
        for line_index, line in enumerate(card["lines"]):
            scene.text(x+22, y+67+line_index*27, line, 17, MUTED)
    scene.text(60, 1726, "Header-aware connectivity checked / hardware bring-up still required", 17, MUTED)
    scene.text(1645, 1726, "data " + source_hash(circuit)[:12], 16, MUTED, "mono", "end")
    scene.text(60, 1754, "Editable circuit data + reusable part definitions + renderer / sources and bench notes in README", 15, MUTED)
    return scene


def export(circuit_path, output_directory, formats=("svg", "png", "pdf"), png_scale=2):
    circuit = Circuit(circuit_path)
    validation = circuit.validate() | {"source_sha256": source_hash(circuit)}
    scene = build_scene(circuit)
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    name = circuit.data["id"]
    files = []
    for fmt in formats:
        path = output / f"{name}.{fmt}"
        if fmt == "svg":
            path.write_text(scene.svg(circuit.data["title"]))
        elif fmt == "png":
            scene.png(path, png_scale)
        elif fmt == "pdf":
            scene.pdf(path, circuit.data["title"])
        else:
            raise ValueError("Unsupported format: " + fmt)
        files.append(str(path.resolve()))
    check_path = output / f"{name}.validation.json"
    check_path.write_text(json.dumps(validation, indent=2)+"\n")
    files.append(str(check_path.resolve()))
    wiring_path = output / f"{name}.wiring.csv"
    with wiring_path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["ID", "Function", "From", "To", "Pin mapping", "Value"])
        for wire in circuit.data.get("wires", []):
            writer.writerow([wire["id"], wire["label"], wire["from"], wire["to"], wire.get("pins", ""), ""])
        for passive in circuit.data.get("passives", []):
            writer.writerow([passive["id"], passive["kind"], passive["a"], passive["b"], "", str(passive.get("ohms", ""))+" ohm"])
    files.append(str(wiring_path.resolve()))
    pins_path = output / f"{name}.pinmap.csv"
    with pins_path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Instance", "Pin", "Hole", "Intended net"])
        for ref, hole in circuit.seats.items():
            instance, pin = ref.split(".", 1)
            writer.writerow([instance, pin, hole, circuit.data.get("expected_nets", {}).get(ref, "unused")])
    files.append(str(pins_path.resolve()))
    return files
