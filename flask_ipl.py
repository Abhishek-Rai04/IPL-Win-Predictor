from flask import Flask, render_template_string, request
import pickle
import os
import pandas as pd

app = Flask(__name__)

# Load the model
try:
    model_path = 'pipe_rf.pkl'
    with open(model_path, 'rb') as f:
        pipe = pickle.load(f)
except Exception as e:
    print(f"Error loading model: {e}")
    pipe = None

# Teams and cities
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

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>IPL Win Predictor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 200px; }
        select, input { width: 200px; padding: 5px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .result { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>IPL Win Predictor</h1>
    <form method="post">
        <div class="form-group">
            <label for="batting_team">Batting Team:</label>
            <select id="batting_team" name="batting_team" required>
                {% for team in teams %}
                    <option value="{{ team }}" {% if team == batting_team %}selected{% endif %}>{{ team }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label for="bowling_team">Bowling Team:</label>
            <select id="bowling_team" name="bowling_team" required>
                {% for team in teams %}
                    {% if team != batting_team %}
                        <option value="{{ team }}" {% if team == bowling_team %}selected{% endif %}>{{ team }}</option>
                    {% endif %}
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label for="city">City:</label>
            <select id="city" name="city" required>
                {% for city in cities %}
                    <option value="{{ city }}" {% if city == selected_city %}selected{% endif %}>{{ city }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label for="runs_left">Runs Left:</label>
            <input type="number" id="runs_left" name="runs_left" min="0" max="300" value="{{ runs_left }}" required>
        </div>
        
        <div class="form-group">
            <label for="balls_left">Balls Left:</label>
            <input type="number" id="balls_left" name="balls_left" min="1" max="120" value="{{ balls_left }}" required>
        </div>
        
        <div class="form-group">
            <label for="wickets_remaining">Wickets Remaining:</label>
            <input type="number" id="wickets_remaining" name="wickets_remaining" min="1" max="10" value="{{ wickets_remaining }}" required>
        </div>
        
        <div class="form-group">
            <label for="target">Target:</label>
            <input type="number" id="target" name="target" min="1" max="300" value="{{ target }}" required>
        </div>
        
        <button type="submit">Predict</button>
    </form>
    
    {% if prediction is not none %}
    <div class="result">
        <h3>Prediction Result:</h3>
        <p>Win Probability for {{ batting_team }}: <strong>{{ "%.2f"|format(prediction * 100) }}%</strong></p>
    </div>
    {% endif %}
    
    {% if error %}
    <div class="error" style="color: red; margin-top: 20px;">
        <p>{{ error }}</p>
    </div>
    {% endif %}
    
    <script>
        // Update bowling team options when batting team changes
        document.getElementById('batting_team').addEventListener('change', function() {
            const battingTeam = this.value;
            const bowlingTeamSelect = document.getElementById('bowling_team');
            const currentBowlingTeam = bowlingTeamSelect.value;
            
            // Store current bowling team options
            const bowlingTeams = Array.from(bowlingTeamSelect.options).map(opt => opt.value);
            
            // Clear and repopulate options
            bowlingTeamSelect.innerHTML = '';
            bowlingTeams.forEach(team => {
                if (team !== battingTeam) {
                    const option = document.createElement('option');
                    option.value = team;
                    option.textContent = team;
                    bowlingTeamSelect.appendChild(option);
                }
            });
            
            // Try to keep the same selection if possible
            if (bowlingTeams.includes(currentBowlingTeam) && currentBowlingTeam !== battingTeam) {
                bowlingTeamSelect.value = currentBowlingTeam;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def predict():
    prediction = None
    error = None
    
    # Default values
    default_values = {
        'batting_team': teams[0],
        'bowling_team': teams[1],
        'city': cities[0],
        'runs_left': 50,
        'balls_left': 60,
        'wickets_remaining': 5,
        'target': 150
    }
    
    if request.method == 'POST':
        try:
            # Get form data
            batting_team = request.form.get('batting_team', teams[0])
            bowling_team = request.form.get('bowling_team', teams[1])
            city = request.form.get('city', cities[0])
            runs_left = int(request.form.get('runs_left', 50))
            balls_left = int(request.form.get('balls_left', 60))
            wickets_remaining = int(request.form.get('wickets_remaining', 5))
            target = int(request.form.get('target', 150))
            
            # Calculate CRR and RRR
            current_score = target - runs_left
            crr = round((current_score * 6) / (120 - balls_left), 2) if (120 - balls_left) > 0 else 0
            rrr = round((runs_left * 6) / balls_left, 2) if balls_left > 0 else 0
            
            # Create input DataFrame
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
            
            # Make prediction
            if pipe is not None:
                result = pipe.predict_proba(input_df)
                prediction = result[0][1]  # Probability of batting team winning
            else:
                error = "Model not loaded. Please check the logs."
                
        except Exception as e:
            error = f"Error: {str(e)}"
            print(error)
            
        return render_template_string(HTML,
                                   teams=teams,
                                   cities=cities,
                                   batting_team=batting_team,
                                   bowling_team=bowling_team,
                                   selected_city=city,
                                   runs_left=runs_left,
                                   balls_left=balls_left,
                                   wickets_remaining=wickets_remaining,
                                   target=target,
                                   prediction=prediction,
                                   error=error)
    
    # For GET request, use default values
    return render_template_string(HTML,
                               teams=teams,
                               cities=cities,
                               batting_team=default_values['batting_team'],
                               bowling_team=default_values['bowling_team'],
                               selected_city=default_values['city'],
                               runs_left=default_values['runs_left'],
                               balls_left=default_values['balls_left'],
                               wickets_remaining=default_values['wickets_remaining'],
                               target=default_values['target'],
                               prediction=prediction,
                               error=error)

if __name__ == '__main__':
    if pipe is None:
        print("Warning: Model could not be loaded. The app will run but predictions will fail.")
    print("Starting IPL Win Predictor on http://localhost:5000")
    app.run(debug=True, port=5000)
