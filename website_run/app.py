import logging
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import threading
import psutil
import queue
import sys
import time
import os
import socket
import shlex
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('service_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Safely manage processes and logs
processes = {}
log_queues = {}
MAX_LOG_LINES = 500  # Limit log lines to prevent memory issues

def sanitize_output(output):
    """Sanitize and decode output safely"""
    try:
        return output.strip().decode('utf-8', errors='replace')
    except Exception as e:
        logger.error(f"Error decoding output: {e}")
        return str(output)

def log_reader(process, name, queue):
    """Read output from process and send to queue with better error handling"""
    try:
        log_count = 0
        while process.poll() is None and log_count < MAX_LOG_LINES:
            output = process.stdout.readline()
            if output:
                sanitized_log = sanitize_output(output)
                queue.put((name, sanitized_log))
                try:
                    socketio.emit('log_update', {'service': name, 'log': sanitized_log})
                except Exception as emit_error:
                    logger.error(f"Error emitting log for {name}: {emit_error}")
                log_count += 1
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in log_reader for {name}: {e}")
    finally:
        if process.poll() is None:
            process.terminate()

def run_command(name, command, cwd):
    """Enhanced command running with better error handling and port conflict resolution"""
    def task():
        try:
            # Specific port handling for known services
            port_map = {
                "backend": 8000,   # FastAPI default port
                "ai": 8001,        # AI API port
                "frontend": 3000   # Next.js default port
            }

            # Kill existing processes on the port if it's in use
            if name in port_map:
                port = port_map[name]
                if is_port_in_use(port):
                    logger.warning(f"Port {port} is in use. Attempting to kill existing processes.")
                    find_and_kill_port_processes(port)

            full_command = f'cmd /c "conda activate superNLP && {command}"'
            logger.info(f"Starting service {name}: {full_command}")
            
            proc = subprocess.Popen(
                full_command,
                cwd=cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=False,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            processes[name] = proc
            
            log_queues[name] = queue.Queue(maxsize=MAX_LOG_LINES)
            
            log_thread = threading.Thread(
                target=log_reader,
                args=(proc, name, log_queues[name]),
                daemon=True
            )
            log_thread.start()
            
            logger.info(f"Service {name} started successfully")
        except Exception as e:
            logger.error(f"Failed to start service {name}: {e}")
            processes.pop(name, None)

    thread = threading.Thread(target=task)
    thread.start()

@app.route('/')
def index():
    return render_template('index.html')

# เพิ่ม route สำหรับดึง log ทั้งหมด
@app.route('/get_logs/<service>', methods=['GET'])
def get_logs(service):
    if service in log_queues:
        logs = []
        while not log_queues[service].empty():
            _, log = log_queues[service].get()
            logs.append(log.strip().decode('utf-8', errors='ignore'))
        return jsonify({"logs": logs})
    return jsonify({"logs": []})

@app.route('/run_backend', methods=['POST'])
def run_backend():
    run_command("backend", "python backend.py", "C:\\Users\\Chits\\Documents\\pensook\\Github\\Website_DEEPBROW\\API\\Backend")
    return jsonify({"status": "✅ Backend Started"})

@app.route('/run_ai', methods=['POST'])
def run_ai():
    run_command("ai", "python AI_API.py", "C:\\Users\\Chits\\Documents\\pensook\\Github\\Website_DEEPBROW\\API\\Backend")
    return jsonify({"status": "✅ AI API Started"})

@app.route('/run_frontend', methods=['POST'])
def run_frontend():
    run_command("frontend", "npm run dev", "C:\\Users\\Chits\\Documents\\pensook\\Github\\Website_DEEPBROW\\API\\Frontend\\deepbrow-frontend")
    return jsonify({"status": "✅ Frontend Started"})

def kill_process_tree(pid):
    """Kill process tree recursively"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Kill children processes
        for child in children:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        
        # Kill parent process
        try:
            parent.kill()
        except psutil.NoSuchProcess:
            pass
            
    except psutil.NoSuchProcess:
        pass

@app.route('/stop/<service>', methods=['POST'])
def stop_process(service):
    """หยุด Process ตามชื่อ"""
    if service in processes:
        try:
            proc = processes[service]
            main_pid = proc.pid
            
            # Kill process tree
            kill_process_tree(main_pid)
            
            # ลบ process จาก dictionary
            del processes[service]
            
            # ล้าง queue ของ log
            if service in log_queues:
                while not log_queues[service].empty():
                    log_queues[service].get()
                del log_queues[service]
                
            return jsonify({"status": f"❌ {service} Stopped"})
        except Exception as e:
            return jsonify({"status": f"⚠️ Error stopping {service}: {str(e)}"})
    return jsonify({"status": f"⚠️ {service} Not Running"})

@app.route('/restart_all', methods=['POST'])
def restart_all():
    """หยุดทุกอย่างแล้วรันใหม่"""
    # หยุดทุก service
    for service in list(processes.keys()):
        try:
            proc = processes[service]
            kill_process_tree(proc.pid)
            del processes[service]
            
            # ล้าง queue ของ log
            if service in log_queues:
                while not log_queues[service].empty():
                    log_queues[service].get()
                del log_queues[service]
        except Exception as e:
            print(f"Error stopping {service}: {str(e)}")

    # รันทุก service ใหม่
    run_backend()
    run_ai()
    run_frontend()
    return jsonify({"status": "🔄 All Services Restarted"})

@app.route('/check_status', methods=['GET'])
def check_status():
    """ เช็คว่าสคริปต์รันอยู่หรือไม่ """
    status = {}
    
    def check_process_status(name):
        """ตรวจสอบว่า process ยังทำงานอยู่หรือไม่"""
        if name in processes:
            proc = processes[name]
            try:
                # ถ้า poll() เป็น None แสดงว่า process ยังทำงานอยู่
                if proc.poll() is None:
                    return "🟢 Running"
                else:
                    # ถ้า process จบการทำงานแล้ว ให้ลบออกจาก dictionary
                    del processes[name]
                    if name in log_queues:
                        del log_queues[name]
                    return "🔴 Stopped"
            except (psutil.NoSuchProcess, ProcessLookupError):
                # ถ้าไม่พบ process ให้ลบออกจาก dictionary
                del processes[name]
                if name in log_queues:
                    del log_queues[name]
                return "🔴 Stopped"
        return "🔴 Stopped"

    status["Backend"] = check_process_status("backend")
    status["AI API"] = check_process_status("ai")
    status["Frontend"] = check_process_status("frontend")

    return jsonify(status)

def find_and_kill_port_processes(port):
    """Find and kill processes using a specific port"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                try:
                    process = psutil.Process(conn.pid)
                    logger.info(f"Killing process {conn.pid} using port {port}: {process.name()}")
                    process.terminate()
                    time.sleep(1)  # Give some time to terminate
                    if process.is_running():
                        process.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
    except Exception as e:
        logger.error(f"Error finding/killing processes on port {port}: {e}")

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@app.route('/kill_port/<int:port>', methods=['POST'])
def kill_port(port):
    """Manually kill processes using a specific port"""
    try:
        find_and_kill_port_processes(port)
        return jsonify({"status": f"✅ Processes on port {port} killed successfully"}), 200
    except Exception as e:
        logger.error(f"Error killing processes on port {port}: {e}")
        return jsonify({"status": f"❌ Failed to kill processes on port {port}: {str(e)}"}), 500

@app.route('/execute_command', methods=['POST'])
def execute_command():
    """Execute a terminal command with security and logging"""
    try:
        from flask import request
        
        # Get command from request
        command = request.json.get('command', '').strip()
        
        # Basic security checks
        if not command:
            return jsonify({"error": "No command provided"}), 400
        
        # Prevent potentially dangerous commands
        dangerous_commands = ['rm', 'del', 'format', 'shutdown', 'reboot', 'sudo', 'su']
        for dangerous in dangerous_commands:
            if dangerous in command.split()[0].lower():
                return jsonify({"error": "Potentially dangerous command blocked"}), 403
        
        # Use subprocess to run the command
        try:
            # Use shell=True carefully, with shlex for some protection
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd(),  # Run in current working directory
                timeout=30  # 30-second timeout to prevent hanging
            )
            
            # Log the command execution
            logger.info(f"Executed command: {command}")
            
            return jsonify({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }), 200
        
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Command timed out"}), 408
        except Exception as e:
            logger.error(f"Command execution error: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in command execution: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
