import streamlit as st
import pickle
import numpy as np
import os

st.title('IPL Win Predictor')

# Load the trained model (Random Forest)
model_path = 'pipe_rf.pkl'
if not os.path.exists(model_path):
    st.error(f"Model file '{model_path}' not found. Please train your model and save it as '{model_path}'.")
    st.stop()

try:
    pipe = pickle.load(open(model_path, 'rb'))
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

teams = [
    'Kolkata Knight Riders', 'Chennai Super Kings', 'Kings XI Punjab',
    'Rajasthan Royals', 'Mumbai Indians', 'Delhi Capitals',
    'Royal Challengers Bangalore', 'Sunrisers Hyderabad'
]
cities = [
    'Hyderabad', 'Pune', 'Rajkot', 'Indore', 'Bangalore', 'Mumbai',
    'Kolkata', 'Delhi', 'Chandigarh', 'Kanpur', 'Jaipur', 'Chennai',
    'Cape Town', 'Port Elizabeth', 'Durban', 'Centurion', 'East London',
    'Johannesburg', 'Kimberley', 'Bloemfontein', 'Ahmedabad', 'Cuttack',
    'Nagpur', 'Dharamsala', 'Visakhapatnam', 'Raipur', 'Ranchi', 'Abu Dhabi',
    'Sharjah', 'Mohali', 'Bengaluru'
]

batting_team = st.selectbox('Select Batting Team', sorted(teams))
bowling_team = st.selectbox('Select Bowling Team', sorted(teams))
city = st.selectbox('Select Host City', sorted(cities))

col1, col2, col3 = st.columns(3)

with col1:
    runs_left = st.number_input('Runs Left', min_value=0, max_value=300, value=50)
with col2:
    balls_left = st.number_input('Balls Left', min_value=1, max_value=120, value=60)
with col3:
    wickets_remaining = st.number_input('Wickets Remaining', min_value=1, max_value=10, value=5)

target = st.number_input('Target Score', min_value=1, max_value=300, value=150)
current_score = target - runs_left
crr = round((current_score * 6) / (120 - balls_left), 2) if (120 - balls_left) > 0 else 0
rrr = round((runs_left * 6) / balls_left, 2) if balls_left > 0 else 0

if st.button('Predict Probability'):
    try:
        input_df = np.array([[batting_team, bowling_team, city, runs_left, balls_left,
                              wickets_remaining, target, crr, rrr]])
        result = pipe.predict_proba(input_df)
        win_prob = result[0][1] * 100
        st.markdown(f"### Win Probability for {batting_team}: {win_prob:.2f}%")
    except Exception as e:
        st.error(f"Prediction error: {e}")