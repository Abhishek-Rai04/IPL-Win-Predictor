from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Test</title>
</head>
<body>
    <h1>Flask Test Page</h1>
    <p>If you can see this, Flask is working!</p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    print("Starting Flask app on http://localhost:5000")
    app.run(debug=True, port=5000)
