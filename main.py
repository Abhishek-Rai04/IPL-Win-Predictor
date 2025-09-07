import streamlit as st
import pickle
import pandas as pd
import os
import sys
import traceback
import warnings
warnings.filterwarnings('ignore')

# Add scikit-learn to the path for model compatibility
import sys
sys.path.append(os.path.dirname(os.path.dirname(pd.__file__)) + '\\Lib\\site-packages')

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

st.title('IPL Win Predictor')

try:
    model_path = 'pipe_rf.pkl'
    logger.info(f"Looking for model at: {os.path.abspath(model_path)}")
    
    if not os.path.exists(model_path):
        error_msg = f"Model file '{os.path.abspath(model_path)}' not found."
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()
    
    logger.info("Loading model with joblib...")
    try:
        import joblib
        pipe = joblib.load(model_path)
        logger.info("Model loaded successfully with joblib")
    except Exception as e:
        logger.error(f"Failed to load model with joblib: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try one more time with pickle as fallback
        try:
            logger.info("Trying with pickle...")
            with open(model_path, 'rb') as f:
                pipe = pickle.load(f)
            logger.info("Model loaded successfully with pickle")
        except Exception as e2:
            error_msg = f"Failed to load model with pickle: {str(e2)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            st.error("""
                Failed to load the model. This is likely due to version incompatibility.
                Please try one of these solutions:
                1. Install Python 3.8 or 3.9 (recommended for better compatibility)
                2. Contact support for a model compatible with Python 3.12
                """)
            st.stop()
    
except Exception as e:
    error_msg = f"Error loading model: {str(e)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    st.error(f"Failed to load the model. Please check the logs for details.")
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

batting_team = st.selectbox('Batting Team', teams)
bowling_team = st.selectbox('Bowling Team', [team for team in teams if team != batting_team])
city = st.selectbox('City', cities)
runs_left = st.number_input('Runs Left', min_value=0, max_value=300, value=50)
balls_left = st.number_input('Balls Left', min_value=1, max_value=120, value=60)
wickets_remaining = st.number_input('Wickets Remaining', min_value=1, max_value=10, value=5)
target = st.number_input('Target', min_value=1, max_value=300, value=150)
current_score = target - runs_left
crr = round((current_score * 6) / (120 - balls_left), 2) if (120 - balls_left) > 0 else 0
rrr = round((runs_left * 6) / balls_left, 2) if balls_left > 0 else 0

if st.button('Predict'):
    try:
        logger.info("Preparing input data...")
        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets_remaining': [wickets_remaining],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })
        logger.debug(f"Input data: {input_df}")
        
        logger.info("Making prediction...")
        result = pipe.predict_proba(input_df)
        logger.info(f"Prediction result: {result}")
        
        st.success(f"Win Probability for {batting_team}: {result[0][1]*100:.2f}%")
        
    except Exception as e:
        error_msg = f"Error during prediction: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        st.error("An error occurred during prediction. Please check the logs for details.")
        st.error(f"Error details: {str(e)}")