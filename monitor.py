import psutil
import sqlite3
import time
import logging

# Configure logging
logging.basicConfig(filename="monitor.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Database setup
conn = sqlite3.connect("monitoring.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        cpu_usage REAL,
        memory_usage REAL,
        disk_usage REAL
    )
""")
conn.commit()

def get_metrics():
    """Collects system metrics (CPU, Memory, Disk usage)."""
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    }

def save_metrics(metrics):
    """Stores the collected metrics in the SQLite database."""
    cursor.execute("INSERT INTO system_metrics (cpu_usage, memory_usage, disk_usage) VALUES (?, ?, ?)",
                   (metrics["cpu"], metrics["memory"], metrics["disk"]))
    conn.commit()

def monitor():
    """Continuously monitors system metrics and logs them."""
    while True:
        metrics = get_metrics()
        logging.info(f"CPU: {metrics['cpu']}%, Memory: {metrics['memory']}%, Disk: {metrics['disk']}%")
        
        # Save to DB
        save_metrics(metrics)

        # Print to console for debugging
        print(f"CPU: {metrics['cpu']}% | Memory: {metrics['memory']}% | Disk: {metrics['disk']}%")

        # Check for high usage alerts
        if metrics["cpu"] > 80:
            print("🚨 High CPU Usage!")
        if metrics["memory"] > 80:
            print("🚨 High Memory Usage!")
        if metrics["disk"] > 90:
            print("🚨 Disk Almost Full!")

        time.sleep(5)  # Adjust monitoring interval

if __name__ == "__main__":
    print("📊 System Monitoring Started...")
    monitor()
