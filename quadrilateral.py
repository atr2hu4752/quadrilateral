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
# QUESTION BANK LOADER (READS DIRECTLY FROM GOOGLE SHEETS)
# ==============================================================================
GOOGLE_SHEET_ID = "1OrTQ0UonsxQIWsid-GLcH-X8UcO4_Eu6ivlTUs7-wds"
GOOGLE_SHEET_TAB = "Quadrilateral"
SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq"
    f"?tqx=out:csv&sheet={GOOGLE_SHEET_TAB}"
)


@st.cache_data(ttl=60)
def load_question_bank():
  """Loads questions from Google Sheets (with fallback to local questions.csv).

  Caches for 60 seconds so slider movements are instant while Sheet edits sync
  automatically.
  """
  try:
    df = pd.read_csv(SHEET_CSV_URL)
  except Exception:
    local_path = Path(__file__).parent / "questions.csv"
    if local_path.exists():
      df = pd.read_csv(local_path)
    else:
      st.error(
          "Could not load questions from Google Sheets or local"
          " questions.csv."
      )
      return []

  bank = []
  for _, row in df.iterrows():
    if pd.isna(row.get("question")):
      continue

    # Extract options cleanly
    raw_options = {
        "a": (
            str(row["option_a"]).strip() if pd.notna(row.get("option_a")) else ""
        ),
        "b": (
            str(row["option_b"]).strip() if pd.notna(row.get("option_b")) else ""
        ),
        "c": (
            str(row["option_c"]).strip() if pd.notna(row.get("option_c")) else ""
        ),
        "d": (
            str(row["option_d"]).strip() if pd.notna(row.get("option_d")) else ""
        ),
    }

    # Automatically add 'A. ', 'B. ', 'C. ', 'D. ' prefixes
    display_options = [f"{k.upper()}. {v}" for k, v in raw_options.items() if v]

    # Map the correct single letter (a, b, c, or d) to the display string
    correct_key = (
        str(row["correct"]).strip().lower()
        if pd.notna(row.get("correct"))
        else "a"
    )
    correct_display = (
        f"{correct_key.upper()}. {raw_options.get(correct_key, '')}"
    )

    bank.append({
        "id": (
            int(row["id"])
            if "id" in row and pd.notna(row["id"])
            else len(bank) + 1
        ),
        "title": str(row.get("title", "Question")).strip(),
        "question": str(row["question"]).strip(),
        "options": display_options,
        "correct": correct_display,
        "explanation": (
            str(row.get("explanation", "")).strip()
            if pd.notna(row.get("explanation"))
            else ""
        ),
    })

  return bank


# Load all questions
QUESTION_BANK = load_question_bank()


# ==============================================================================
# MODE SELECTOR IN SIDEBAR
# ==============================================================================
st.sidebar.title("Navigation")
total_questions_count = len(QUESTION_BANK)
app_mode = st.sidebar.radio(
    "Choose Mode:",
    [
        "🔍 Interactive Explorer",
        f"🎮 Challenge Game Mode ({total_questions_count} Qs)",
    ],
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
# MODE 2: CHALLENGE GAME MODE (ALL QUESTIONS INCLUDED)
# ==============================================================================
if app_mode.startswith("🎮 Challenge Game Mode"):
  st.title("🎮 Quadrilateral Challenge")
  st.write(
      f"Test your geometry skills across **all {total_questions_count}"
      " questions** loaded from your question bank!"
  )

  # Initialize Session State
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

  def start_new_game(name, shuffle_order=False):
    st.session_state.player_name = name if name.strip() else "Alice"
    # Take ALL questions from the bank
    questions = [dict(q) for q in QUESTION_BANK]
    if shuffle_order:
      random.shuffle(questions)
    st.session_state.selected_questions = questions
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.game_log = []
    st.session_state.game_active = True
    st.session_state.game_finished = False
    st.session_state.current_answered = False

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

  # SCREEN 1: Welcome & Setup
  if not st.session_state.game_active and not st.session_state.game_finished:
    st.markdown("### 🏆 Welcome to the Challenge!")
    name_input = st.text_input(
        "Enter Player Name:",
        value=st.session_state.player_name,
        placeholder="e.g. Alice",
    )
    shuffle_choice = st.checkbox("Randomize question order", value=False)

    st.info(
        f"**Round Details:**\n"
        f"- Contains all **{total_questions_count} questions** currently in the Google Sheet.\n"
        "- Clear explanations provided after each question.\n"
        "- You can end early at any time and download your progress report."
    )

    if st.button("🚀 Start Challenge", use_container_width=True, type="primary"):
      start_new_game(name_input, shuffle_order=shuffle_choice)
      st.rerun()

  # SCREEN 2: Active Question View
  elif st.session_state.game_active and not st.session_state.game_finished:
    current_q_idx = st.session_state.q_index
    total_q = len(st.session_state.selected_questions)
    current_q = st.session_state.selected_questions[current_q_idx]

    # Top Status Bar
    col_top1, col_top2 = st.columns([3, 1])
    col_top1.write(
        f"👤 **Player:** `{st.session_state.player_name}` | 🎯 **Score:**"
        f" `{st.session_state.score}/{current_q_idx}`"
    )
    if col_top2.button("⏹️ End Game Early", use_container_width=True):
      st.session_state.game_active = False
      st.session_state.game_finished = True
      st.rerun()

    st.progress(current_q_idx / total_q)
    st.markdown(f"#### Question {current_q_idx + 1} of {total_q}")
    st.markdown(f"### **{current_q['title']}**")
    st.write(current_q["question"])

    user_choice = st.radio(
        "Select your answer:",
        current_q["options"],
        key=f"q_{current_q_idx}",
        disabled=st.session_state.current_answered,
    )

    if not st.session_state.current_answered:
      if st.button(
          "Submit Answer ✔️", type="primary", use_container_width=True
      ):
        is_correct = user_choice == current_q["correct"]
        if is_correct:
          st.session_state.score += 1

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
      last_entry = st.session_state.game_log[-1]
      if last_entry["is_correct"]:
        st.success("🎉 **Correct! Well done!**")
      else:
        st.error(
            f"❌ **Incorrect.** The correct answer is: **{current_q['correct']}**"
        )

      if current_q["explanation"]:
        st.info(f"💡 **Explanation:** {current_q['explanation']}")

      is_last_q = current_q_idx == total_q - 1
      btn_label = (
          "🏆 See Final Results" if is_last_q else "Next Question ➡️"
      )

      if st.button(btn_label, type="primary", use_container_width=True):
        if is_last_q:
          st.session_state.game_active = False
          st.session_state.game_finished = True
        else:
          st.session_state.q_index += 1
          st.session_state.current_answered = False
        st.rerun()

  # SCREEN 3: Summary & Log Download
  elif st.session_state.game_finished:
    total_q = len(st.session_state.selected_questions)
    attempted = len(st.session_state.game_log)
    final_score = st.session_state.score

    if attempted == total_q and final_score >= int(0.8 * total_q):
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
        if item["explanation"]:
          st.write(f"**Explanation:** {item['explanation']}")

    st.markdown("---")
    if st.button("🔄 Play Again", type="primary", use_container_width=True):
      start_new_game(st.session_state.player_name)
      st.rerun()
