import csv
from datetime import datetime
import io
import random
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Quadrilateral Explorer & Challenge for Alice",
    layout="centered",
)

# ==============================================================================
# QUESTION BANK FOR GAME MODE
# ==============================================================================
QUESTION_BANK = [
    {
        "title": "Multi-Shape Classification",
        "question": (
            "A quadrilateral has 4 equal side lengths (6 cm each) and all 4"
            " interior angles are 90°. Which of the following shape categories"
            " does it belong to?"
        ),
        "options": [
            "Square only",
            "Rectangle only",
            "Rhombus only",
            "Square, Rectangle, Rhombus, and Parallelogram simultaneously",
        ],
        "correct": (
            "Square, Rectangle, Rhombus, and Parallelogram simultaneously"
        ),
        "explanation": (
            "In hierarchical classification, a square satisfies the definition"
            " of a rectangle (4 right angles), a rhombus (4 equal sides), and a"
            " parallelogram (2 pairs of parallel sides). It belongs to all of"
            " them simultaneously!"
        ),
    },
    {
        "title": "Deformation: Rhombus to Square",
        "question": (
            "You have a slanted (non-square) rhombus with sides of 5 cm and an"
            " acute interior angle of 60°. What single tweak will turn it into"
            " a square?"
        ),
        "options": [
            "Extend two opposite sides from 5 cm to 8 cm",
            "Widen the 60° acute angle to 90°",
            "Pull vertex C outwards along the diagonal",
            "Shorten the diagonal connecting the acute angles",
        ],
        "correct": "Widen the 60° acute angle to 90°",
        "explanation": (
            "A rhombus already has 4 equal sides. A square is simply an"
            " equiangular rhombus. Setting any angle to 90° forces all four"
            " angles to become 90°, creating a square."
        ),
    },
    {
        "title": "Deformation: Rectangle to Square",
        "question": (
            "You have a rectangle with side AB = 8 cm and side AD = 4 cm (all"
            " angles 90°). What tweak transforms it into a square?"
        ),
        "options": [
            "Rotate the rectangle clockwise by 45°",
            "Shorten the longer sides AB and CD from 8 cm to 4 cm",
            "Change angle A from 90° to 60°",
            (
                "Pull vertex C along the diagonal so the diagonals become"
                " perpendicular"
            ),
        ],
        "correct": "Shorten the longer sides AB and CD from 8 cm to 4 cm",
        "explanation": (
            "A rectangle already has four 90° angles. To make it a square, its"
            " adjacent sides must become equal in length (all 4 sides = 4 cm)."
            " Rotating it 45° only changes its orientation on the page!"
        ),
    },
    {
        "title": "The Perimeter vs. Area Trap",
        "question": (
            "A flexible wire square frame with side length 10 cm has an area"
            " of 100 cm². You push a corner sideways so it squishes into a"
            " rhombus with an acute angle of 30°. What happens to its"
            " perimeter and area?"
        ),
        "options": [
            "Perimeter decreases; area remains 100 cm²",
            "Perimeter remains 40 cm; area remains 100 cm²",
            "Perimeter remains 40 cm; area decreases to 50 cm²",
            "Both perimeter and area decrease",
        ],
        "correct": "Perimeter remains 40 cm; area decreases to 50 cm²",
        "explanation": (
            "The 4 wire rods do not change length, so Perimeter = 4 × 10 = 40"
            " cm. But the perpendicular height drops to h = 10 × sin(30°) = 5"
            " cm. The new Area = base × height = 10 × 5 = 50 cm² (cut in"
            " half)!"
        ),
    },
    {
        "title": "Parallelogram to Rhombus",
        "question": (
            "You have a parallelogram with AB = 7 cm, AD = 4 cm, and angle A ="
            " 70°. What single tweak will transform it into a rhombus?"
        ),
        "options": [
            "Change angle A from 70° to 90°",
            "Extend side AD from 4 cm to 7 cm so all 4 sides are equal",
            "Make diagonals AC and BD equal in length",
            "Pull vertex C so opposite sides are no longer parallel",
        ],
        "correct": "Extend side AD from 4 cm to 7 cm so all 4 sides are equal",
        "explanation": (
            "A rhombus is an equilateral parallelogram. Making side AD = 7 cm"
            " ensures all 4 sides are equal while keeping opposite sides"
            " parallel."
        ),
    },
    {
        "title": "Mystery Shape from Diagonals",
        "question": (
            "A quadrilateral has diagonals that bisect each other at right"
            " angles (90°), but the two diagonals have DIFFERENT lengths (d1 ="
            " 6 cm, d2 = 10 cm). What shape is it?"
        ),
        "options": [
            "Square",
            "Non-square Rhombus",
            "Non-square Rectangle",
            "Trapezium",
        ],
        "correct": "Non-square Rhombus",
        "explanation": (
            "Diagonals that are perpendicular bisectors of each other guarantee"
            " 4 equal sides (a rhombus). Since they are unequal in length, it"
            " is a non-square rhombus."
        ),
    },
    {
        "title": "Hong Kong Primary Curriculum Definition",
        "question": (
            "Under the official Hong Kong EDB Primary Mathematics curriculum,"
            " is a rectangle considered a kind of trapezium?"
        ),
        "options": [
            "Yes, because it has at least one pair of parallel sides",
            "Yes, because all parallelograms are trapeziums",
            (
                "No, because the HK curriculum defines a trapezium as having"
                " ONLY ONE pair of parallel sides"
            ),
            "No, because a trapezium cannot have right angles",
        ],
        "correct": (
            "No, because the HK curriculum defines a trapezium as having ONLY"
            " ONE pair of parallel sides"
        ),
        "explanation": (
            "In Hong Kong primary textbooks and TSA assessments, trapeziums are"
            " defined exclusively: 'only one pair of opposite sides are"
            " parallel' (只有一組對邊平行). Since rectangles have two pairs of parallel"
            " sides, they are not trapeziums in HK schools."
        ),
    },
    {
        "title": "Deformation: Rhombus to Kite",
        "question": (
            "You have a rhombus ABCD with sides of 5 cm. If you keep vertices"
            " A, B, and D fixed, but pull vertex C outward along diagonal AC so"
            " that BC = CD = 9 cm, what shape is formed?"
        ),
        "options": [
            "Parallelogram",
            "Trapezium",
            "Convex Kite",
            "Rectangle",
        ],
        "correct": "Convex Kite",
        "explanation": (
            "Opposite sides are no longer parallel, but adjacent sides are"
            " equal in two distinct pairs: AB = AD = 5 cm and BC = CD = 9 cm."
            " This is the definition of a kite!"
        ),
    },
    {
        "title": "The 'Equal Diagonals' Trap",
        "question": (
            "A student says: 'If any quadrilateral has diagonals of equal"
            " length, it MUST be a rectangle.' Is this statement correct?"
        ),
        "options": [
            "Correct, only rectangles have equal diagonals",
            (
                "Incorrect, because an isosceles trapezium also has equal"
                " diagonals"
            ),
            "Incorrect, because squares do not have equal diagonals",
            "Correct, because equal diagonals always create 90° angles",
        ],
        "correct": (
            "Incorrect, because an isosceles trapezium also has equal diagonals"
        ),
        "explanation": (
            "An isosceles trapezium has diagonals of equal length, but its"
            " angles are not 90° and it is not a rectangle. To guarantee a"
            " rectangle, the diagonals must be equal AND bisect each other."
        ),
    },
    {
        "title": "Four Right Angles",
        "question": (
            "A quadrilateral has four 90° angles. Which statement is ALWAYS"
            " true?"
        ),
        "options": [
            "It must be a square",
            "It must be a rhombus",
            "It must be a rectangle (which may or may not be a square)",
            "It cannot be a parallelogram",
        ],
        "correct": "It must be a rectangle (which may or may not be a square)",
        "explanation": (
            "Four right angles define a rectangle. We do not know if adjacent"
            " sides are equal: if they are, it's also a square; if not, it's an"
            " oblong rectangle. But it is always a rectangle."
        ),
    },
    {
        "title": "Orientation Bias Trap",
        "question": (
            "A square is rotated 45° so it balances on one corner. A classmate"
            " says: 'It is no longer a square; it is now a diamond.' Are they"
            " correct?"
        ),
        "options": [
            "Yes, rotating by 45° transforms a square into a diamond",
            (
                "No, geometric shapes are defined by sides and angles, not"
                " orientation"
            ),
            "Yes, because squares must have horizontal bases",
            "No, it is now an irregular quadrilateral",
        ],
        "correct": (
            "No, geometric shapes are defined by sides and angles, not"
            " orientation"
        ),
        "explanation": (
            "A shape's geometric identity depends only on its intrinsic"
            " properties (equal sides, 90° angles), never on its rotation on"
            " the page. It remains a square!"
        ),
    },
    {
        "title": "The 'One Pair Parallel, One Pair Equal' Trap",
        "question": (
            "A quadrilateral has side AB parallel to side CD, and side AD equal"
            " in length to side BC (AD = BC). Must this quadrilateral be a"
            " parallelogram?"
        ),
        "options": [
            "Yes, because one pair is parallel and one pair is equal",
            (
                "No, it could be an isosceles trapezium where the non-parallel"
                " legs are equal"
            ),
            "Yes, because parallel lines always have equal opposites",
            "No, it must be a kite",
        ],
        "correct": (
            "No, it could be an isosceles trapezium where the non-parallel"
            " legs are equal"
        ),
        "explanation": (
            "To guarantee a parallelogram, the SAME pair of sides must be both"
            " parallel and equal. If one pair is parallel and the other pair is"
            " equal, the figure could be an isosceles trapezium!"
        ),
    },
    {
        "title": "Parallelogram to Rectangle",
        "question": (
            "You have a parallelogram with sides 6 cm and 9 cm and an angle of"
            " 40°. What single tweak will turn it into a rectangle?"
        ),
        "options": [
            "Increase the 40° angle to 90°",
            "Lengthen the 6 cm side to 9 cm",
            "Make diagonals perpendicular to each other",
            "Shorten the 9 cm side to 6 cm",
        ],
        "correct": "Increase the 40° angle to 90°",
        "explanation": (
            "In any parallelogram, making one angle 90° forces all four angles"
            " to become 90° (since consecutive interior angles sum to 180°),"
            " producing a rectangle."
        ),
    },
    {
        "title": "Diagonals of Rectangles",
        "question": (
            "Which property is true for ALL rectangles, but NOT true for all"
            " general parallelograms?"
        ),
        "options": [
            "Opposite sides are parallel",
            "Opposite angles are equal",
            "Diagonals bisect each other",
            "Diagonals are equal in length",
        ],
        "correct": "Diagonals are equal in length",
        "explanation": (
            "All parallelograms have opposite sides parallel, opposite angles"
            " equal, and bisecting diagonals. Only rectangles and squares have"
            " diagonals that are equal in length!"
        ),
    },
]

# ==============================================================================
# MODE SELECTOR IN SIDEBAR
# ==============================================================================
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio(
    "Choose Mode:",
    ["🔍 Interactive Explorer", "🎮 Challenge Game Mode (10 Qs)"],
    index=0,
)

# ==============================================================================
# MODE 1: INTERACTIVE EXPLORER
# ==============================================================================
if app_mode == "🔍 Interactive Explorer":
  st.title("Quadrilateral Explorer for Alice")
  st.write(
      "Adjust **side lengths**, **angles**, **rotate the shape**, and **pull"
      " vertex C** to see how a **Square** transforms into a **Rectangle**,"
      " **Rhombus**, **Parallelogram**, or **Kite**."
  )

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

  st.sidebar.header("Geometry Controls")
  st.sidebar.button(
      "🔄 Reset to Square", on_click=reset_to_square, use_container_width=True
  )
  st.sidebar.markdown("---")

  side_a = st.sidebar.slider(
      "Side a: Base side AB",
      min_value=1.0,
      max_value=10.0,
      step=0.5,
      key="side_a",
      help="Controls base side AB (and CD when in parallelogram mode).",
  )

  side_b = st.sidebar.slider(
      "Side b: Adjacent side AD",
      min_value=1.0,
      max_value=10.0,
      step=0.5,
      key="side_b",
      help="Controls adjacent side AD (and BC when in parallelogram mode).",
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
      "Rotate Shape Clockwise (°)",
      min_value=0,
      max_value=360,
      step=5,
      key="rotation_deg",
      help="Rotates the entire quadrilateral clockwise around its center.",
  )

  st.sidebar.markdown("---")
  show_diagonals = st.sidebar.checkbox("Show Diagonals", value=True)
  show_angle_markers = st.sidebar.checkbox("Show Angle Markers", value=True)
  show_side_labels = st.sidebar.checkbox(
      "Show Side Lengths on Edges", value=True
  )

  # Mathematics of vertices
  half_theta_rad = np.radians(angle_deg / 2)
  u_AB = np.array([np.cos(half_theta_rad), -np.sin(half_theta_rad)])
  u_AD = np.array([np.cos(half_theta_rad), np.sin(half_theta_rad)])

  A_raw = np.array([0.0, 0.0])
  B_raw = A_raw + side_a * u_AB
  D_raw = A_raw + side_b * u_AD

  vec_AC_parallelogram = (B_raw - A_raw) + (D_raw - A_raw)
  C_raw = A_raw + pull_c * vec_AC_parallelogram

  center = (A_raw + B_raw + C_raw + D_raw) / 4.0
  A_base = A_raw - center
  B_base = B_raw - center
  C_base = C_raw - center
  D_base = D_raw - center

  s_AB = np.linalg.norm(B_base - A_base)
  s_BC = np.linalg.norm(C_base - B_base)
  s_CD = np.linalg.norm(D_base - C_base)
  s_DA = np.linalg.norm(A_base - D_base)

  len_ac = np.linalg.norm(C_base - A_base)
  len_db = np.linalg.norm(B_base - D_base)

  def compute_interior_angle(V, V1, V2):
    v1 = V1 - V
    v2 = V2 - V
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
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

  if angle_deg in (0, 180):
    shape_name = "Degenerate Line Segment"
    color = "#7F8C8D"
  elif is_concave and has_kite_sides:
    shape_name = "Dart / Arrowhead (Concave Kite)"
    color = "#E74C3C"
  elif has_kite_sides:
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

  # Clockwise rotation
  rot_rad = np.radians(-rotation_deg)
  cos_r, sin_r = np.cos(rot_rad), np.sin(rot_rad)
  R = np.array([[cos_r, -sin_r], [sin_r, cos_r]])

  A = A_base @ R.T
  B = B_base @ R.T
  C = C_base @ R.T
  D = D_base @ R.T
  vertices = np.array([A, B, C, D])

  fig, ax = plt.subplots(figsize=(7.5, 7.5))
  polygon = patches.Polygon(
      vertices,
      closed=True,
      facecolor=color,
      alpha=0.32,
      edgecolor=color,
      linewidth=3,
  )
  ax.add_patch(polygon)

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

  def draw_right_angle_symbol(
      ax, V, V1, V2, size=0.45, color="#1E8449", lw=1.8
  ):
    n1, n2 = np.linalg.norm(V1 - V), np.linalg.norm(V2 - V)
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

  def draw_angle_arc(ax, V, V1, V2, deg_val, color="#D35400"):
    v1 = V1 - V
    v2 = V2 - V
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
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

  # Auto-expanding dynamic canvas bounds
  max_extent = max(np.max(np.abs(vertices)), 7.5) + 1.8
  ax.set_xlim(-max_extent, max_extent)
  ax.set_ylim(-max_extent, max_extent)
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

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Sides AB & AD", f"{s_AB:.1f}, {s_DA:.1f}")
  col2.metric("Sides BC & CD", f"{s_BC:.1f}, {s_CD:.1f}")
  col3.metric("Angle A / C", f"{ang_A:.0f}° / {ang_C:.0f}°")
  col4.metric("Angle B / D", f"{ang_B:.0f}° / {ang_D:.0f}°")

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

# ==============================================================================
# MODE 2: CHALLENGE GAME MODE
# ==============================================================================
else:
  st.title("🎮 Quadrilateral Challenge")
  st.write(
      "Test your geometry skills! 10 multiple-choice questions on shape"
      " properties, transformations, and tricky traps."
  )

  # Initialize Game Session State
  if "game_active" not in st.session_state:
    st.session_state.game_active = False
  if "game_finished" not in st.session_state:
    st.session_state.game_finished = False
  if "player_name" not in st.session_state:
    st.session_state.player_name = "Alice"
  if "q_index" not in st.session_state:
    st.session_state.q_index = 0
  if "score" not in st.session_state:
    st.session_state.score = 0
  if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []
  if "game_log" not in st.session_state:
    st.session_state.game_log = []
  if "current_answered" not in st.session_state:
    st.session_state.current_answered = False

  # Function to start or restart game
  def start_new_game(name):
    st.session_state.player_name = name if name.strip() else "Alice"
    st.session_state.selected_questions = random.sample(
        QUESTION_BANK, min(10, len(QUESTION_BANK))
    )
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.game_log = []
    st.session_state.game_active = True
    st.session_state.game_finished = False
    st.session_state.current_answered = False

  # Function to generate downloadable CSV log
  def generate_csv_log():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Round Timestamp",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ])
    writer.writerow(["Player Name", st.session_state.player_name])
    writer.writerow([
        "Final Score",
        f"{st.session_state.score} /"
        f" {len(st.session_state.selected_questions)}",
    ])
    writer.writerow([])
    writer.writerow([
        "Q#",
        "Question Title",
        "Question Prompt",
        "Your Answer",
        "Correct Answer",
        "Result",
        "Explanation",
    ])
    for item in st.session_state.game_log:
      writer.writerow([
          item["q_num"],
          item["title"],
          item["question"],
          item["user_choice"],
          item["correct"],
          "CORRECT" if item["is_correct"] else "INCORRECT",
          item["explanation"],
      ])
    return output.getvalue().encode("utf-8-sig")

  # SCREEN 1: Welcome & Name Input Screen
  if not st.session_state.game_active and not st.session_state.game_finished:
    st.markdown("### 🏆 Welcome to the Challenge!")
    name_input = st.text_input(
        "Enter Player Name:",
        value=st.session_state.player_name,
        placeholder="e.g. Alice",
    )

    st.info(
        "**Rules & Structure:**\n"
        "- 10 questions in this round.\n"
        "- You will identify shapes, predict transformation tweaks, and tackle"
        " tricky curriculum edge-cases.\n"
        "- Immediate explanation provided after each answer.\n"
        "- You can end early at any time and download your progress report."
    )

    if st.button("🚀 Start Challenge", use_container_width=True, type="primary"):
      start_new_game(name_input)
      st.rerun()

  # SCREEN 2: Active Gameplay Screen
  elif st.session_state.game_active and not st.session_state.game_finished:
    current_q_idx = st.session_state.q_index
    total_q = len(st.session_state.selected_questions)
    current_q = st.session_state.selected_questions[current_q_idx]

    # Top Navigation Banner
    col_top1, col_top2 = st.columns([3, 1])
    col_top1.write(
        f"👤 **Player:** `{st.session_state.player_name}` | 🎯 **Score:**"
        f" `{st.session_state.score}/{current_q_idx}`"
    )
    if col_top2.button("⏹️ End Game Early", use_container_width=True):
      st.session_state.game_active = False
      st.session_state.game_finished = True
      st.rerun()

    st.progress((current_q_idx) / total_q)
    st.markdown(f"#### Question {current_q_idx + 1} of {total_q}")
    st.markdown(f"### **{current_q['title']}**")
    st.write(current_q["question"])

    # Radio options for multiple choice
    user_choice = st.radio(
        "Select your answer:",
        current_q["options"],
        key=f"q_{current_q_idx}",
        disabled=st.session_state.current_answered,
    )

    # Submission & Feedback controls
    if not st.session_state.current_answered:
      if st.button(
          "Submit Answer ✔️", type="primary", use_container_width=True
      ):
        is_correct = user_choice == current_q["correct"]
        if is_correct:
          st.session_state.score += 1

        # Record to log
        st.session_state.game_log.append({
            "q_num": current_q_idx + 1,
            "title": current_q["title"],
            "question": current_q["question"],
            "user_choice": user_choice,
            "correct": current_q["correct"],
            "is_correct": is_correct,
            "explanation": current_q["explanation"],
        })
        st.session_state.current_answered = True
        st.rerun()
    else:
      # Display Answer Result
      last_entry = st.session_state.game_log[-1]
      if last_entry["is_correct"]:
        st.success("🎉 **Correct! Well done!**")
      else:
        st.error(
            f"❌ **Incorrect.** The correct answer is: **{current_q['correct']}**"
        )

      st.info(f"💡 **Explanation:** {current_q['explanation']}")

      # Next Question / View Results Button
      is_last_q = current_q_idx == total_q - 1
      btn_label = (
          "🏆 See Final Results"
          if is_last_q
          else "Next Question ➡️"
      )

      if st.button(btn_label, type="primary", use_container_width=True):
        if is_last_q:
          st.session_state.game_active = False
          st.session_state.game_finished = True
        else:
          st.session_state.q_index += 1
          st.session_state.current_answered = False
        st.rerun()

  # SCREEN 3: Game Finished / Summary & Download Screen
  elif st.session_state.game_finished:
    total_q = len(st.session_state.selected_questions)
    attempted = len(st.session_state.game_log)
    final_score = st.session_state.score

    if attempted == total_q and final_score >= 8:
      st.balloons()
      st.success(
          f"🌟 Outstanding, {st.session_state.player_name}! You scored"
          f" **{final_score} / {total_q}**!"
      )
    else:
      st.info(
          f"Game Complete, {st.session_state.player_name}! You scored"
          f" **{final_score} / {attempted}** (Attempted {attempted} of"
          f" {total_q})."
      )

    # Download Log Button
    csv_bytes = generate_csv_log()
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📥 Download Detailed Game Log (CSV)",
        data=csv_bytes,
        file_name=(
            f"quadrilateral_challenge_{st.session_state.player_name}_{date_str}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("📋 Round Review")
    for item in st.session_state.game_log:
      status_icon = "✅" if item["is_correct"] else "❌"
      with st.expander(
          f"{status_icon} Question {item['q_num']}: {item['title']}"
      ):
        st.write(f"**Question:** {item['question']}")
        st.write(f"**Your Answer:** {item['user_choice']}")
        if not item["is_correct"]:
          st.write(f"**Correct Answer:** {item['correct']}")
        st.write(f"**Explanation:** {item['explanation']}")

    st.markdown("---")
    if st.button("🔄 Play Again", type="primary", use_container_width=True):
      start_new_game(st.session_state.player_name)
      st.rerun()
