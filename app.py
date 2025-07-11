import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objs as go
import os
import time

TEAM_LOGOS = {
    "Chennai Super Kings": "csk-removebg-preview.png",
    "Sunrisers Hyderabad": "srh-removebg-preview (1).png",
    "Delhi Capitals": "dc-removebg-preview.png",
    "Kolkata Knight Riders": "kkr-removebg-preview.png",
    "Royal Challengers Bangalore": "rcb_logo-removebg-preview.png",
    "Rajasthan Royals": "rr-removebg-preview.png",
    "Mumbai Indians": "mumbai-removebg-preview.png",
    "Kings XI Punjab": "pbks-removebg-preview.png"
}

st.set_page_config(page_title="IPL Win Predictor", layout="wide")

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Open+Sans:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Open Sans', sans-serif !important;
        background: linear-gradient(120deg, rgba(200,220,255,0.18) 0%, rgba(220,240,255,0.10) 100%) !important;
        min-height: 100vh;
    }
    .block-container {
        padding-top: 0rem !important;
    }
    .ipl-header {
        background: linear-gradient(90deg, #0a1d4e 0%, #17408b 100%);
        border-radius: 0 0 32px 32px;
        box-shadow: 0 8px 32px 0 rgba(0,153,255,0.10);
        padding: 32px 18px 18px 18px;
        margin-bottom: 32px;
        text-align: center;
        position: relative;
        border-bottom: none;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        width: 100vw;
        left: 50%;
        transform: translateX(-50%);
    }
    .ipl-title {
        font-family: 'Oswald', 'Inter', Arial, sans-serif !important;
        font-size: 3.8rem !important;
        font-weight: 800 !important;
        color: #fff !important;
        letter-spacing: 2px;
        text-shadow: 0 2px 12px rgba(0,153,255,0.18);
        margin-bottom: 0.2em;
    }
    .ipl-subtitle {
        font-size: 1.7rem !important;
        color: #e3f2fd !important;
        margin-bottom: 0.2em;
        font-family: 'Open Sans', sans-serif !important;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .team-card {
        background: none;
        border-radius: 18px;
        box-shadow: none;
        padding: 0 !important;
        margin-bottom: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 420px;
        height: 320px;
        min-width: 420px;
        min-height: 320px;
        margin-top: 0 !important;
        justify-content: center;
        overflow: hidden;
    }
    .team-logo-large {
        width: 320px;
        height: 320px;
        min-width: 320px;
        min-height: 320px;
        object-fit: contain;
        border-radius: 12px;
        background: none;
        border: none;
        box-shadow: none;
        margin: 0;
        padding: 0;
        display: block;
    }
    .vs-text {
        font-family: 'Oswald', 'Open Sans', Arial, sans-serif !important;
        font-size: 4.2rem !important;
        font-weight: 900 !important;
        color: #0057e7 !important;
        margin: 0 32px 0 32px;
        align-self: center;
        text-shadow: 0 2px 12px rgba(0,153,255,0.10);
        display: flex;
        align-items: center;
        height: 100%;
        margin-top: 180px !important;
    }
    .team-selection-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-top: -48px !important;
        margin-bottom: 0;
        padding-top: 0 !important;
    }
    .prob-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 48px;
        margin-top: 36px;
        margin-bottom: 0;
        background: none !important;
        box-shadow: none !important;
        border: none !important;
    }
    .prob-logo {
        width: 300px;
        height: 300px;
        object-fit: contain;
        border-radius: 12px;
        background: none;
        border: none;
        box-shadow: none;
        margin: 0;
        padding: 0;
        display: block;
    }
    .prob-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        margin-left: 24px;
    }
    .prob-anim {
        font-size: 6.2rem !important;
        font-weight: 900 !important;
        color: #fff !important;
        margin-left: 0;
        margin-right: 0;
        display: inline-block;
        vertical-align: middle;
    }
    .prob-label {
        font-size: 2.7rem !important;
        font-weight: 700 !important;
        color: #fff !important;
        margin-left: 0;
        display: inline-block;
        vertical-align: middle;
        text-shadow: 0 2px 12px rgba(0,153,255,0.18);
    }
    .stButton > button {
        background: rgba(0,153,255,0.85) !important;
        color: #fff !important;
        font-family: 'Oswald', 'Open Sans', Arial, sans-serif !important;
        font-size: 3.2rem !important;
        font-weight: 900 !important;
        border-radius: 24px !important;
        padding: 1.2em 4em !important;
        box-shadow: 0 4px 24px 0 rgba(0,153,255,0.13);
        border: none !important;
        transition: all 0.2s cubic-bezier(.4,0,.2,1);
    }
    .stButton > button:hover {
        background: #ff4b5c !important;
        color: #fff !important;
        filter: brightness(1.15);
        transform: scale(1.09);
        box-shadow: 0 0 16px 2px #ff4b5c44;
    }
    .stButton > button:active {
        background: #ff4b5c !important;
        color: #fff !important;
        filter: brightness(1.2);
        transform: scale(1.13);
        box-shadow: 0 0 24px 4px #ff4b5c66;
    }
    .match-details-label {
        font-size: 2.7rem !important;
        font-weight: 700 !important;
        color: #0057e7 !important;
        margin-bottom: 18px;
        margin-top: 0px;
        letter-spacing: 1px;
        font-family: 'Oswald', 'Open Sans', Arial, sans-serif !important;
    }
    label, .stNumberInput label, .stSelectbox label {
        font-size: 2.1rem !important;
        font-weight: 600 !important;
        color: #0057e7 !important;
        font-family: 'Oswald', 'Open Sans', Arial, sans-serif !important;
    }
    .select-label {
        font-size: 2.7rem !important;
        font-weight: 800 !important;
        color: #0057e7 !important;
        font-family: 'Oswald', 'Open Sans', Arial, sans-serif !important;
        margin-bottom: 0.2em;
    }
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 2.1rem !important;
        font-family: 'Open Sans', Arial, sans-serif !important;
        min-height: 3.2em !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        min-height: 2.4em !important;
        font-size: 1.4rem !important;
        font-family: 'Open Sans', Arial, sans-serif !important;
        padding-top: 0.3em !important;
        padding-bottom: 0.3em !important;
        line-height: 1.7rem !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    .stSelectbox div[data-baseweb="select"] input {
        font-size: 1.4rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
def show_logo_and_title():
    st.markdown('''
        <div class="ipl-header">
            <div style="display: flex; align-items: center; justify-content: center; gap: 18px;">
                <div class="ipl-title">🏏 IPL Win Predictor</div>
            </div>
            <div class="ipl-subtitle">Predict the probability of winning an IPL match based on current match stats.</div>
        </div>
    ''', unsafe_allow_html=True)

# --- LOGO PATH ---
def get_logo_path(team_name):
    filename = TEAM_LOGOS.get(team_name)
    if filename:
        return f"logos/{filename}"
    return None

# --- TEAM SELECTION UI ---
def team_selection_ui(teams):
    st.markdown('<div class="team-selection-row">', unsafe_allow_html=True)
    col1, col_vs, col2 = st.columns([5,1,5], gap="large")
    with col1:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown('<div class="select-label">Batting Team</div>', unsafe_allow_html=True)
        batting_team = st.selectbox(
            '',
            teams,
            key="batting_team",
            index=teams.index('Mumbai Indians'),
            help="Select the batting team",
            placeholder="Search or select batting team..."
        )
        batting_logo = get_logo_path(batting_team)
        if batting_logo and os.path.exists(batting_logo):
            st.image(batting_logo, use_container_width=False, width=320)
        else:
            st.image('logos/placeholder.png', use_container_width=False, width=320)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_vs:
        st.markdown('<div style="display: flex; align-items: center; justify-content: center; height: 320px;"><span class="vs-text" style="margin-top: 180px;">V/S</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.markdown('<div class="select-label">Bowling Team</div>', unsafe_allow_html=True)
        bowling_team = st.selectbox(
            '',
            teams,
            key="bowling_team",
            index=teams.index('Chennai Super Kings'),
            help="Select the bowling team",
            placeholder="Search or select bowling team..."
        )
        bowling_logo = get_logo_path(bowling_team)
        if bowling_logo and os.path.exists(bowling_logo):
            st.image(bowling_logo, use_container_width=False, width=320)
        else:
            st.image('logos/placeholder.png', use_container_width=False, width=320)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return batting_team, bowling_team

# --- ENHANCED MATCH DETAILS FORM ---
def input_form(teams, cities):
    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="match-details-label">Match Details</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        target = st.number_input('Target', min_value=1, max_value=300, value=150)
        score = st.number_input('Current Score', min_value=0, max_value=300, value=50)
    with col2:
        overs = st.number_input('Overs Completed', min_value=0.0, max_value=20.0, value=5.0, step=0.1)
        wickets_down = st.number_input('Wickets Remaining', min_value=0, max_value=10, value=2)
    with col3:
        selected_city = st.selectbox('Host City', sorted(cities))
    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
    return target, score, overs, wickets_down, selected_city

# --- LOAD MODEL ---
def load_model():
    with open("pipe.pkl", "rb") as file:
        return pickle.load(file)

# --- MATCH STATE CHART ---
def show_match_state_chart(target, score, overs, wickets_down):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 20], y=[target, target], mode='lines', name='Target',
        line=dict(color='#43a047', width=4, dash='dash'),
        hoverinfo='none',
    ))
    fig.add_trace(go.Bar(
        x=[overs], y=[score], name='Current Runs',
        marker_color='#0057e7', width=0.7,
        hoverinfo='x+y',
    ))
    fig.add_trace(go.Scatter(
        x=[overs], y=[score], mode='markers+text', name='Wickets',
        marker=dict(size=22, color='#d11141', symbol='x'),
        text=[f"Wkts: {wickets_down}"], textposition='top center',
        hoverinfo='x+y+text',
    ))
    fig.update_layout(
        title="Match State: Runs vs Overs",
        xaxis_title="Overs",
        yaxis_title="Runs",
        xaxis=dict(range=[0, 20], dtick=2, showgrid=True, gridcolor='#e5e5e5', zeroline=False),
        yaxis=dict(range=[0, max(target, score) + 20], showgrid=True, gridcolor='#e5e5e5', zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
        template="plotly_white",
        font=dict(family="Inter, Open Sans, Arial, sans-serif", size=18)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- ANIMATED PROBABILITY DISPLAY ---
def show_probability_result(batting_team, win):
    batting_logo = get_logo_path(batting_team)
    st.markdown('<div class="prob-row" style="gap: 0;">', unsafe_allow_html=True)
    if batting_logo and os.path.exists(batting_logo):
        st.markdown('<div style="display: flex; align-items: center;">', unsafe_allow_html=True)
        st.image(batting_logo, width=150, output_format="PNG", clamp=True, channels="RGBA", caption=None)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="display: flex; flex-direction: column; justify-content: center; align-items: flex-start; margin-left: 32px;">', unsafe_allow_html=True)
    placeholder = st.empty()
    for i in range(0, int(round(win*100))+1, 1):
        placeholder.markdown(f'<span class="prob-anim">{i}%</span>', unsafe_allow_html=True)
        time.sleep(0.025)
    st.markdown('<span class="prob-label">Winning Chance</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    show_logo_and_title()

    teams = [
        'Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
        'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
        'Rajasthan Royals', 'Delhi Capitals'
    ]
    cities = [
        'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
        'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
        'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
        'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
        'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
        'Sharjah', 'Mohali', 'Bengaluru'
    ]

    batting_team, bowling_team = team_selection_ui(teams)
    target, score, overs, wickets_down, selected_city = input_form(teams, cities)
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    show_match_state_chart(target, score, overs, wickets_down)

    pipe = load_model()
    col_btn, col_prob = st.columns([1,2])
    with col_btn:
        predict = st.button('Predict Probability')
    with col_prob:
        if predict:
            runs_left = target - score
            balls_left = 120 - int(overs*6)
            wickets_left = 10 - wickets_down
            crr = score/overs if overs > 0 else 0
            rrr = (runs_left*6)/balls_left if balls_left > 0 else 0

            input_df = pd.DataFrame({
                'batting_team':[batting_team],
                'bowling_team':[bowling_team],
                'city':[selected_city],
                'runs_left':[runs_left],
                'balls_left':[balls_left],
                'wickets':[wickets_left],
                'total_runs_x':[target],
                'crr':[crr],
                'rrr':[rrr]
            })

            result = pipe.predict_proba(input_df)
            win = result[0][1]
            show_probability_result(batting_team, win)

if __name__ == "__main__":
    main()
