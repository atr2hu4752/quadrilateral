import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Quadrilateral Explorer for Alice", layout="centered")

st.title("Quadrilateral Explorer for Alice")
st.write(
    "Adjust **side lengths**, **angles**, **rotate the shape**, and **pull vertex C** "
    "to see how a **Square** transforms into a **Rectangle**, **Rhombus**, "
    "**Parallelogram**, or **Kite**."
)

# ----------------- Session State & Reset -----------------
defaults = {
    "side_a": 5.0,
    "side_b": 5.0,
    "angle_deg": 90,
    "pull_c": 1.0,
    "rotation_deg": 0,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def reset_to_square():
  for k, v in defaults.items():
    st.session_state[k] = v


# ----------------- Sidebar Controls -----------------
st.sidebar.header("Geometry Controls")

# Reset button placed prominently at the top
st.sidebar.button(
    "🔄 Reset to Square", on_click=reset_to_square, use_container_width=True
)
st.sidebar.markdown("---")

side_a = st.sidebar.slider(
    "Side a: Length of AB and CD",
    min_value=1.0,
    max_value=10.0,
    step=0.5,
    key="side_a",
    help="Controls the length of side AB.",
)

side_b = st.sidebar.slider(
    "Side b: Length of AD and BC",
    min_value=1.0,
    max_value=10.0,
    step=0.5,
    key="side_b",
    help="Controls the length of side AD. Keep equal to Side a for Rhombus, Square, or Kite.",
)

angle_deg = st.sidebar.slider(
    "Interior Angle at Vertex A ($\\theta$)",
    min_value=0,
    max_value=180,
    step=1,
    key="angle_deg",
    help="Adjust the angle at corner A. At 90°, adjacent edges meet at right angles.",
)

pull_c = st.sidebar.slider(
    "Pull Vertex C (Kite Deformer)",
    min_value=0.4,
    max_value=2.2,
    step=0.05,
    key="pull_c",
    help="Pulls or pushes Vertex C along diagonal AC. When Side a = Side b and Pull != 1.0, the shape becomes a Kite.",
)

rotation_deg = st.sidebar.slider(
    "Rotate Shape (°)",
    min_value=0,
    max_value=360,
    step=5,
    key="rotation_deg",
    help="Rotates the entire quadrilateral around its geometric center.",
)

st.sidebar.markdown("---")
show_diagonals = st.sidebar.checkbox("Show Diagonals", value=True)
show_angle_markers = st.sidebar.checkbox("Show Angle Markers", value=True)
show_side_labels = st.sidebar.checkbox("Show Side Lengths on Edges", value=True)

# ----------------- Vertex Math (Unrotated Base) -----------------
half_theta_rad = np.radians(angle_deg / 2)

# Unit vectors along AB and AD from A
u_AB = np.array([np.cos(half_theta_rad), -np.sin(half_theta_rad)])
u_AD = np.array([np.cos(half_theta_rad), np.sin(half_theta_rad)])

A_raw = np.array([0.0, 0.0])
B_raw = A_raw + side_a * u_AB
D_raw = A_raw + side_b * u_AD

# In a parallelogram, vector AC = vector AB + vector AD
vec_AC_parallelogram = (B_raw - A_raw) + (D_raw - A_raw)
C_raw = A_raw + pull_c * vec_AC_parallelogram

# Center at (0, 0)
center = (A_raw + B_raw + C_raw + D_raw) / 4.0
A_base = A_raw - center
B_base = B_raw - center
C_base = C_raw - center
D_base = D_raw - center

# ----------------- Geometry Properties & Classification -----------------
s_AB = np.linalg.norm(B_base - A_base)
s_BC = np.linalg.norm(C_base - B_base)
s_CD = np.linalg.norm(D_base - C_base)
s_DA = np.linalg.norm(A_base - D_base)

len_ac = np.linalg.norm(C_base - A_base)
len_db = np.linalg.norm(B_base - D_base)


def compute_interior_angle(V, V1, V2):
  v1 = V1 - V
  v2 = V2 - V
  n1 = np.linalg.norm(v1)
  n2 = np.linalg.norm(v2)
  if n1 < 1e-4 or n2 < 1e-4:
    return 0.0
  cos_val = np.dot(v1, v2) / (n1 * n2)
  return float(np.degrees(np.arccos(np.clip(cos_val, -1.0, 1.0))))


ang_A = compute_interior_angle(A_base, D_base, B_base)
ang_B = compute_interior_angle(B_base, A_base, C_base)
ang_C = compute_interior_angle(C_base, B_base, D_base)
ang_D = compute_interior_angle(D_base, C_base, A_base)

tol = 0.08
is_equilateral = (
    np.isclose(s_AB, s_BC, atol=tol)
    and np.isclose(s_BC, s_CD, atol=tol)
    and np.isclose(s_CD, s_DA, atol=tol)
)
all_right_angles = all(
    np.isclose(ang, 90.0, atol=0.8) for ang in [ang_A, ang_B, ang_C, ang_D]
)
is_parallelogram = np.isclose(pull_c, 1.0, atol=0.03)

dot_diagonals = np.dot(C_base - A_base, B_base - D_base)
diagonals_perpendicular = np.isclose(dot_diagonals, 0.0, atol=0.25)
diagonals_equal = np.isclose(len_ac, len_db, atol=0.1)

has_kite_sides = (
    np.isclose(s_AB, s_DA, atol=tol)
    and np.isclose(s_BC, s_CD, atol=tol)
    and not np.isclose(s_AB, s_BC, atol=tol)
)
is_concave = C_base[0] < B_base[0]

# Shape classification
if angle_deg in (0, 180):
  shape_name = "Degenerate Line Segment"
  color = "#7F8C8D"
elif is_concave and has_kite_sides:
  shape_name = "Dart / Arrowhead (Concave Kite)"
  color = "#E74C3C"
elif has_kite_sides:
  if np.isclose(ang_B, 90.0, atol=0.8) and np.isclose(ang_D, 90.0, atol=0.8):
    shape_name = "Right Kite (Angles B & D = 90°)"
  else:
    shape_name = "Kite"
  color = "#9B59B6"
elif is_parallelogram:
  if all_right_angles and is_equilateral:
    shape_name = "Square"
    color = "#2ECC71"
  elif all_right_angles:
    shape_name = "Rectangle (Non-Square)"
    color = "#1ABC9C"
  elif is_equilateral:
    shape_name = "Rhombus (Non-Square)"
    color = "#3498DB"
  else:
    shape_name = "Parallelogram (General)"
    color = "#E67E22"
else:
  shape_name = "General Quadrilateral"
  color = "#7F8C8D"

# ----------------- Apply Rotation -----------------
rot_rad = np.radians(-rotation_deg)
cos_r, sin_r = np.cos(rot_rad), np.sin(rot_rad)
R = np.array([[cos_r, -sin_r], [sin_r, cos_r]])

A = A_base @ R.T
B = B_base @ R.T
C = C_base @ R.T
D = D_base @ R.T
vertices = np.array([A, B, C, D])

# ----------------- Plot Setup -----------------
fig, ax = plt.subplots(figsize=(7.5, 7.5))

polygon = patches.Polygon(
    vertices, closed=True, facecolor=color, alpha=0.32, edgecolor=color, linewidth=3
)
ax.add_patch(polygon)

# Draw diagonals
if show_diagonals:
  ax.plot(
      [A[0], C[0]],
      [A[1], C[1]],
      linestyle="--",
      color="#E74C3C",
      linewidth=1.5,
      label=f"Diagonal AC: {len_ac:.2f}",
  )
  ax.plot(
      [D[0], B[0]],
      [D[1], B[1]],
      linestyle="--",
      color="#8E44AD",
      linewidth=1.5,
      label=f"Diagonal DB: {len_db:.2f}",
  )
  ax.legend(loc="upper right", frameon=True)


# Right-angle markers
def draw_right_angle_symbol(ax, V, V1, V2, size=0.45, color="#1E8449", lw=1.8):
  n1 = np.linalg.norm(V1 - V)
  n2 = np.linalg.norm(V2 - V)
  if n1 < 1e-4 or n2 < 1e-4:
    return
  v1 = (V1 - V) / n1
  v2 = (V2 - V) / n2
  p1 = V + size * v1
  p2 = V + size * v2
  p_corner = V + size * v1 + size * v2
  ax.plot(
      [p1[0], p_corner[0], p2[0]],
      [p1[1], p_corner[1], p2[1]],
      color=color,
      linewidth=lw,
  )


# Angle arcs & degrees
def draw_angle_arc(ax, V, V1, V2, deg_val, color="#D35400"):
  v1 = V1 - V
  v2 = V2 - V
  n1 = np.linalg.norm(v1)
  n2 = np.linalg.norm(v2)
  if n1 < 1e-4 or n2 < 1e-4:
    return
  a1 = np.degrees(np.arctan2(v1[1], v1[0])) % 360
  a2 = np.degrees(np.arctan2(v2[1], v2[0])) % 360
  diff = (a2 - a1) % 360
  if diff <= 180:
    th1, th2 = a1, a1 + diff
    bisector = np.radians(a1 + diff / 2)
  else:
    th1, th2 = a2, a2 + (360 - diff)
    bisector = np.radians(a2 + (360 - diff) / 2)
  r_arc = max(0.4, min(0.9, 0.25 * min(n1, n2)))
  ax.add_patch(
      patches.Arc(
          V,
          2 * r_arc,
          2 * r_arc,
          angle=0,
          theta1=th1,
          theta2=th2,
          color=color,
          linewidth=1.8,
      )
  )
  t_dist = r_arc + 0.45
  tx = V[0] + t_dist * np.cos(bisector)
  ty = V[1] + t_dist * np.sin(bisector)
  ax.text(
      tx,
      ty,
      f"{deg_val:.0f}°",
      ha="center",
      va="center",
      fontsize=9,
      fontweight="bold",
      color=color,
      bbox=dict(
          boxstyle="round,pad=0.18",
          facecolor="white",
          alpha=0.85,
          edgecolor="none",
      ),
  )


if show_angle_markers and 0 < angle_deg < 180:
  corners = [
      (A, D, B, ang_A),
      (B, A, C, ang_B),
      (C, B, D, ang_C),
      (D, C, A, ang_D),
  ]
  for V, V1, V2, ang in corners:
    if np.isclose(ang, 90.0, atol=0.8):
      draw_right_angle_symbol(ax, V, V1, V2)
    elif 5 < ang < 175:
      draw_angle_arc(ax, V, V1, V2, ang)

# Side length labels on edges (pointing radially outward)
if show_side_labels and 0 < angle_deg < 180:
  edge_bbox = dict(
      boxstyle="round,pad=0.18",
      facecolor="#F8F9F9",
      alpha=0.9,
      edgecolor="gray",
      lw=0.5,
  )
  for p1, p2, length in [
      (A, B, s_AB),
      (B, C, s_BC),
      (C, D, s_CD),
      (D, A, s_DA),
  ]:
    mid = (p1 + p2) / 2.0
    edge_vec = p2 - p1
    n_vec = np.linalg.norm(edge_vec)
    if n_vec > 1e-4:
      normal = np.array([-edge_vec[1], edge_vec[0]]) / n_vec
      if np.dot(normal, mid) < 0:
        normal = -normal
      label_pos = mid + 0.42 * normal
      ax.text(
          label_pos[0],
          label_pos[1],
          f"{length:.1f}",
          fontsize=8.5,
          ha="center",
          va="center",
          bbox=edge_bbox,
      )

# Outward vertex letter labels (rotation-proof)
for pt, label in [(A, "A"), (B, "B"), (C, "C"), (D, "D")]:
  n_pt = np.linalg.norm(pt)
  pos = pt + 0.55 * (pt / n_pt) if n_pt > 1e-3 else pt
  ax.text(
      pos[0],
      pos[1],
      label,
      ha="center",
      va="center",
      fontsize=12,
      fontweight="bold",
  )

# Plot canvas boundaries
ax.set_xlim(-10.5, 10.5)
ax.set_ylim(-9.0, 9.0)
ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.5)
ax.axhline(0, color="gray", linewidth=0.5, linestyle=":")
ax.axvline(0, color="gray", linewidth=0.5, linestyle=":")
ax.set_title(
    f"Current Shape: {shape_name} | Rotation: {rotation_deg}°",
    fontsize=13,
    fontweight="bold",
    pad=12,
)

st.pyplot(fig)

# Metrics Grid
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sides AB & AD", f"{s_AB:.1f}, {s_DA:.1f}")
col2.metric("Sides BC & CD", f"{s_BC:.1f}, {s_CD:.1f}")
col3.metric("Angle A / C", f"{ang_A:.0f}° / {ang_C:.0f}°")
col4.metric("Angle B / D", f"{ang_B:.0f}° / {ang_D:.0f}°")

# Dynamic Property Checklist
st.markdown("### **Property Checklist**")
c1, c2, c3, c4 = st.columns(4)
c1.checkbox(
    "Adjacent sides equal in pairs",
    value=bool(has_kite_sides or is_equilateral),
    disabled=True,
)
c2.checkbox(
    "Opposite sides parallel", value=bool(is_parallelogram), disabled=True
)
c3.checkbox(
    "Diagonals Perpendicular (90°)",
    value=bool(diagonals_perpendicular),
    disabled=True,
)
c4.checkbox("Diagonals Equal", value=bool(diagonals_equal), disabled=True)

# Educational Insight Cards
if "Kite" in shape_name:
  st.info(
      "**Kite Identified:** Pulling vertex C broke the parallelism of opposite"
      " sides, but preserved symmetry across diagonal AC. Adjacent sides remain"
      f" equal in pairs ($AB = AD = {s_AB:.1f}$ and $BC = CD = {s_BC:.1f}$). The"
      " diagonals remain **perpendicular ($90^\\circ$)**, and opposite angles B"
      f" and D remain equal ({ang_B:.0f}°)."
  )
elif shape_name == "Square":
  st.success(
      "**Square Identified:** A regular quadrilateral that belongs"
      " simultaneously to the **Rectangle**, **Rhombus**, and **Kite**"
      " families. Diagonals are both **equal** and **perpendicular**."
  )
elif shape_name == "Rhombus (Non-Square)":
  st.info(
      "**Rhombus Identified:** All four sides are equal ($a = b$) and Pull ="
      " 1.0. Diagonals are perpendicular ($90^\\circ$), but unequal in length."
  )
elif shape_name == "Rectangle (Non-Square)":
  st.info(
      "**Rectangle Identified:** Four right angles with opposite sides parallel"
      " and equal. Diagonals are equal, but not perpendicular."
  )
elif shape_name == "Degenerate Line Segment":
  st.warning(
      "**Degenerate State:** The shape has flattened completely into a line"
      " segment."
  )
else:
  st.warning(
      "**General Parallelogram / Quadrilateral:** Opposite sides are not equal"
      " in adjacent pairs or opposite angles do not match."
  )
