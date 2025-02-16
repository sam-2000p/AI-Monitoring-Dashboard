from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import psutil
import time
import threading
import datetime

app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Database Model
class SystemMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cpu = db.Column(db.Float, nullable=False)
    memory = db.Column(db.Float, nullable=False)
    disk = db.Column(db.Float, nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Function to collect system metrics and store them in DB
def collect_metrics():
    with app.app_context():  # Fix: Ensure the function runs in the app context
        while True:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            new_entry = SystemMetrics(cpu=cpu, memory=memory, disk=disk)
            db.session.add(new_entry)
            db.session.commit()

            time.sleep(5)  # Collect every 5 seconds

# Start data collection in a separate thread
threading.Thread(target=collect_metrics, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/metrics')
def get_metrics():
    latest_metrics = SystemMetrics.query.order_by(SystemMetrics.id.desc()).limit(10).all()
    metrics_list = [{"timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 
                     "cpu": m.cpu, "memory": m.memory, "disk": m.disk} 
                    for m in latest_metrics]
    return jsonify(metrics_list)

if __name__ == '__main__':
    app.run(debug=True)
