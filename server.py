from flask import Flask, render_template
#import requests
import static.engine


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate")
def generate():
    return render_template("generate.html")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")

@app.route('/engine/', methods=['POST'])
def run_engine():
    content = request.json
    print(request)



if __name__ == "__main__":
    app.run(debug=True)