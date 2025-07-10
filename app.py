# app.py – ultra-slow version
import time
import streamlit as st
from skyfield.api import load
import plotly.graph_objects as go

st.set_page_config(page_title="Solar System Simulator", layout="wide")

# ── 세션 상태 초기화 ────────────────────────────
if "t" not in st.session_state:
    ts = load.timescale()
    st.session_state.t = ts.now()
if "running" not in st.session_state:
    st.session_state.running = False
ts = load.timescale()

# ── 사이드바 UI ────────────────────────────────
st.sidebar.title("🔭 제어")
picked_date = st.sidebar.date_input("날짜", st.session_state.t.utc_datetime().date())
picked_hour = st.sidebar.slider("시", 0, 23, st.session_state.t.utc_datetime().hour)

if st.sidebar.button("▶️ / ⏸️"):
    st.session_state.running = not st.session_state.running

# ★ 아주 느린 배속 슬라이더 (0.01 ~ 2 h/s)
step_hours = st.sidebar.slider("배속 (시간/초)", 0.01, 2.0, 0.5, 0.01)

# 슬라이더 값으로 현재 시점 세팅
st.session_state.t = ts.utc(picked_date.year, picked_date.month, picked_date.day, picked_hour)

# ── BSP + 천체 정의 ────────────────────────────
planets = load("de440s.bsp")
bodies = {
    "Sun": "sun",
    "Mercury": "mercury barycenter",
    "Venus": "venus barycenter",
    "Earth": "earth barycenter",
    "Mars": "mars barycenter",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
}

def make_fig(t):
    fig = go.Figure()
    for name, key in bodies.items():
        x, y, z = planets[key].at(t).position.au
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode="markers+text",
            marker=dict(size=4 if name != "Sun" else 8),
            text=[name],
            name=name,
        ))
    fig.update_layout(scene=dict(aspectmode="data"), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

placeholder = st.empty()
info = st.empty()

# 범위(1850~2150) 검사용
BSP_START, BSP_END = 1850, 2150

while True:
    placeholder.plotly_chart(make_fig(st.session_state.t), use_container_width=True)
    info.caption(f"{st.session_state.t.utc_datetime():%Y-%m-%d %H:%M UTC} ｜ "
                 f"배속 {step_hours} h/s ｜ "
                 f"{'▶️ 재생' if st.session_state.running else '⏸️ 정지'}")

    if st.session_state.running:
        nxt = st.session_state.t + step_hours * 3600
        yr  = nxt.utc_datetime().year
        if BSP_START <= yr < BSP_END:
            st.session_state.t = nxt
            time.sleep(0.5)          # ★ 프레임 지연 0.5 초
        else:
            st.session_state.running = False
            st.warning("⚠️ 1850~2150 년 범위를 벗어나 멈췄어요.")
    else:
        break
