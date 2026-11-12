"""Parametrische 2-teilige Gießform für einen Silikon-O-Ring.

Erzeugt druckfertige STL-Dateien (stl/) und die Modelle für die Webseite (web/models.js).
Aufruf:  python generate.py
"""
import base64
import math
import os

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, set_circular_segments

set_circular_segments(96)

# ---------------------------------------------------------------- Parameter (mm)
RING_ID = 20.0           # Innendurchmesser O-Ring
CORD = 3.0               # Schnurstärke (Durchmesser Ringschlauch)
R_MAJOR = RING_ID / 2 + CORD / 2
R_MINOR = CORD / 2

BLOCK = 50.0             # Kantenlänge der Form
CORNER_R = 4.0
H_BOTTOM = 8.0
H_TOP = 8.0

BOLT_POS = 20.0          # M4-Schrauben in den Ecken
BOLT_D = 4.5
NUT_AF = 7.3             # M4-Mutter Schlüsselweite + Spiel
NUT_DEPTH = 3.4

PIN_A = (0.0, 20.0, 5.0)     # (x, y, Ø) – unterschiedliche Ø = verdrehsicher
PIN_B = (0.0, -20.0, 4.0)
PIN_H = 4.0
PIN_CLEAR = 0.3

SPRUE_ANGLE = 0.0
SPRUE_D = 2.5
FUNNEL_D = 18.0          # Trichter-Öffnung oben (Kartuschendüse kegelig, Spitze ca. Ø 5 mm)
FUNNEL_BASE_D = 5.5      # Trichter-Grund: Düsenspitze sitzt hier auf
FUNNEL_DEPTH = 10.0
BOSS_D = 22.0
BOSS_H = 4.0

VENT_ANGLES = (90.0, 180.0, 270.0)   # Reihenfolge des Verschließens: 1=90°, 2=270°, 3=180°
VENT_D = 1.6

PRY_W, PRY_H, PRY_DEPTH = 10.0, 1.5, 4.0

RECESS = 0.4             # Trennfläche des Oberteils ist abgesenkt, nur Steg und Pads berühren
LAND_W = 5.0             # Stegbreite beidseits des Rings
PAD_D = 12.0             # Pads um Schrauben und Passstifte


def polar(angle_deg, r=R_MAJOR):
    a = math.radians(angle_deg)
    return r * math.cos(a), r * math.sin(a)


def rounded_block(height, z0):
    off = BLOCK / 2 - CORNER_R
    cyls = [Manifold.cylinder(height, CORNER_R).translate((sx * off, sy * off, z0))
            for sx in (-1, 1) for sy in (-1, 1)]
    return Manifold.batch_hull(cyls)


def ring_cavity():
    return CrossSection.circle(R_MINOR).translate((R_MAJOR, 0)).revolve()


def bolt_holes(z0, h):
    out = Manifold()
    for sx in (-1, 1):
        for sy in (-1, 1):
            out = out + Manifold.cylinder(h, BOLT_D / 2).translate((sx * BOLT_POS, sy * BOLT_POS, z0))
    return out


def pin(x, y, d, clearance=0.0, extra=0.0):
    dd = d + clearance
    h = PIN_H + extra
    body = Manifold.cylinder(h - 0.6, dd / 2)
    tip = Manifold.cylinder(0.6, dd / 2, dd / 2 - 0.5).translate((0, 0, h - 0.6))
    if clearance:
        tip = Manifold.cylinder(0.6, dd / 2).translate((0, 0, h - 0.6))
    return (body + tip).translate((x, y, 0))


def bottom_half():
    m = rounded_block(H_BOTTOM, -H_BOTTOM)
    m = m - ring_cavity()
    m = m - bolt_holes(-H_BOTTOM - 1, H_BOTTOM + 2)
    nut = CrossSection.circle(NUT_AF / math.sqrt(3), 6).extrude(NUT_DEPTH)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m = m - nut.translate((sx * BOLT_POS, sy * BOLT_POS, -H_BOTTOM - 0.01))
    for x, y, d in (PIN_A, PIN_B):
        m = m + pin(x, y, d)
    for sx in (-1, 1):  # Hebelschlitze zum Öffnen
        m = m - Manifold.cube((PRY_DEPTH * 2, PRY_W, PRY_H)).translate(
            (sx * BLOCK / 2 - PRY_DEPTH, -PRY_W / 2, -PRY_H + 0.001))
    return m


def contact_recess():
    """Abgesenkter Bereich der Trennfläche: nur Ringsteg und Pads um Schrauben/Passstifte bleiben auf Höhe 0."""
    h = RECESS + 0.4
    r_out, r_in = R_MAJOR + R_MINOR + LAND_W, max(R_MAJOR - R_MINOR - LAND_W, 0.5)
    keep = Manifold.cylinder(h, r_out) - Manifold.cylinder(h, r_in)
    for sx in (-1, 1):
        for sy in (-1, 1):
            keep = keep + Manifold.cylinder(h, PAD_D / 2).translate((sx * BOLT_POS, sy * BOLT_POS, 0))
    for x, y, _ in (PIN_A, PIN_B):
        keep = keep + Manifold.cylinder(h, PAD_D / 2).translate((x, y, 0))
    return rounded_block(RECESS, 0) - keep.translate((0, 0, -0.2))


def top_half():
    m = rounded_block(H_TOP, 0)
    m = m - contact_recess()
    sx_, sy_ = polar(SPRUE_ANGLE)
    m = m + Manifold.cylinder(BOSS_H, BOSS_D / 2).translate((sx_, sy_, H_TOP - 0.01))
    m = m - ring_cavity()
    m = m - bolt_holes(-1, H_TOP + 2)
    for x, y, d in (PIN_A, PIN_B):
        m = m - pin(x, y, d, clearance=PIN_CLEAR, extra=0.6).translate((0, 0, -0.01))
    top_z = H_TOP + BOSS_H
    m = m - Manifold.cylinder(top_z + 1, SPRUE_D / 2).translate((sx_, sy_, 0))
    m = m - Manifold.cylinder(FUNNEL_DEPTH + 0.01, FUNNEL_BASE_D / 2, FUNNEL_D / 2).translate(
        (sx_, sy_, top_z - FUNNEL_DEPTH))
    for a in VENT_ANGLES:
        vx, vy = polar(a)
        m = m - Manifold.cylinder(H_TOP + 2, VENT_D / 2).translate((vx, vy, -1))
        m = m - Manifold.cylinder(0.81, VENT_D / 2, VENT_D / 2 + 0.8).translate((vx, vy, H_TOP - 0.8))
    return m


def seal():
    return CrossSection.circle(R_MINOR).translate((R_MAJOR, 0)).revolve()


def to_trimesh(m):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                        faces=np.asarray(mesh.tri_verts), process=True)
    assert t.is_watertight, "Mesh nicht wasserdicht"
    return t


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(root, "stl"), exist_ok=True)
    os.makedirs(os.path.join(root, "web"), exist_ok=True)

    parts = {"bottom": to_trimesh(bottom_half()), "top": to_trimesh(top_half()), "seal": to_trimesh(seal())}

    # Druckorientierung: Trennebene jeweils nach oben, keine Stützen nötig
    b = parts["bottom"].copy(); b.apply_translation((0, 0, H_BOTTOM))
    t = parts["top"].copy(); t.apply_transform(trimesh.transformations.rotation_matrix(math.pi, (1, 0, 0)))
    t.apply_translation((0, 0, -t.bounds[0][2]))
    b.export(os.path.join(root, "stl", "form_unterteil.stl"))
    t.export(os.path.join(root, "stl", "form_oberteil.stl"))
    parts["seal"].export(os.path.join(root, "stl", "o_ring_vorschau.stl"))

    # Druckplatte: beide Teile nebeneinander, als STL und 3MF (zwei Objekte)
    b2 = b.copy(); b2.apply_translation((-b.bounds[1][0] - 5, 0, 0))
    t2 = t.copy(); t2.apply_translation((-t.bounds[0][0] + 5, 0, 0))
    scene = trimesh.Scene({"unterteil": b2, "oberteil": t2})
    scene.export(os.path.join(root, "stl", "druckplatte.3mf"))
    trimesh.util.concatenate([b2, t2]).export(os.path.join(root, "stl", "druckplatte.stl"))

    lines = ["// automatisch erzeugt von generate.py – nicht von Hand bearbeiten",
             "window.MOLD = {",
             f"  params: {{ringId:{RING_ID}, cord:{CORD}, rMajor:{R_MAJOR}, hBottom:{H_BOTTOM}, hTop:{H_TOP},"
             f" bossH:{BOSS_H}, funnelD:{FUNNEL_D}, funnelBaseD:{FUNNEL_BASE_D}, funnelDepth:{FUNNEL_DEPTH}, sprueD:{SPRUE_D}, sprueAngle:{SPRUE_ANGLE},"
             f" ventAngles:{list(VENT_ANGLES)}, block:{BLOCK}, boltPos:{BOLT_POS}}},"]
    for name, mesh in parts.items():
        data = base64.b64encode(mesh.export(file_type="stl")).decode()
        lines.append(f'  {name}: "{data}",')
    lines.append("};")
    with open(os.path.join(root, "web", "models.js"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    for name, mesh in parts.items():
        print(f"{name:7s} Volumen {mesh.volume/1000:7.2f} cm3  Größe {np.round(mesh.extents, 2)}  wasserdicht={mesh.is_watertight}")


if __name__ == "__main__":
    main()
