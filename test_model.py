import pickle
import os

try:
    model_path = 'pipe_rf.pkl'
    print(f"Attempting to load model from: {os.path.abspath(model_path)}")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
