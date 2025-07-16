from flask import Flask, render_template
import psutil
from datetime import datetime

app = Flask(__name__)

INTERVAL = 60
prev_sent, prev_recv = 0, 0
prev_read, prev_write = 0, 0

@app.route("/")
def index():
    return render_template(
        "index.html",  # Make sure this file exists in the 'templates' folder
        users=get_logged_in_users(),
        stats=get_system_info(),
        net=get_network_speed(),
        disk_io=get_disk_io_speed(),
        processes=get_processes()
    )





def get_logged_in_users():
    users = psutil.users()
    return [f"{u.name} ({u.host}) at {datetime.fromtimestamp(u.started).strftime('%Y-%m-%d %H:%M:%S')}" for u in users]


def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "cpu": cpu_usage,
        "ram_used": round(ram.used / (1024 ** 3), 2),
        "ram_total": round(ram.total / (1024 ** 3), 2),
        "disk_used": round(disk.used / (1024 ** 3), 2),
        "disk_total": round(disk.total / (1024 ** 3), 2)
    }


def get_network_speed():
    global prev_sent, prev_recv
    current = psutil.net_io_counters()
    sent_speed = (current.bytes_sent - prev_sent) / INTERVAL
    recv_speed = (current.bytes_recv - prev_recv) / INTERVAL
    prev_sent, prev_recv = current.bytes_sent, current.bytes_recv
    return {
        "upload_kbps": round(sent_speed / 1024, 2),
        "download_kbps": round(recv_speed / 1024, 2)
    }


def get_disk_io_speed():
    global prev_read, prev_write
    current = psutil.disk_io_counters()
    read_speed = (current.read_bytes - prev_read) / INTERVAL
    write_speed = (current.write_bytes - prev_write) / INTERVAL
    prev_read, prev_write = current.read_bytes, current.write_bytes
    return {
        "read_kbps": round(read_speed / 1024, 2),
        "write_kbps": round(write_speed / 1024, 2)
    }


def get_processes():
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'status', 'memory_info']):
        try:
            mem_info = p.info['memory_info']
            if mem_info:  # Make sure it's not None
                mem_mb = round(mem_info.rss / (1024 ** 2), 2)
                procs.append({
                    'pid': p.info['pid'],
                    'name': p.info['name'],
                    'status': p.info['status'],
                    'memory': mem_mb
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            continue
    return sorted(procs, key=lambda x: x['memory'], reverse=True)





if __name__ == "__main__":
    print("🚀 System Monitor Web Server running at http://127.0.0.1:5000/")
    app.run(debug=True)
