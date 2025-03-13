"""
Utility functions for the system module.

These functions handle system metrics collection, log parsing, and process management.
"""

import os
import psutil
import platform
import datetime
import time
import re
import subprocess
from pathlib import Path
import json
from flask import current_app

def get_system_metrics():
    """
    Get comprehensive system metrics.
    
    Returns:
        dict: System metrics including CPU, memory, disk usage, etc.
    """
    # Basic system info
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = get_disk_usage()
    temperature = get_temperature()
    uptime = get_uptime()
    
    # Network info
    network_io = psutil.net_io_counters()
    
    # Try to get IP address
    ip_address = "Unknown"
    try:
        # Use network interfaces to get IP address instead of hostname command
        network_if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in network_if_addrs.items():
            # Skip loopback interfaces
            if interface_name.startswith('lo'):
                continue
            # Look for IPv4 addresses
            for address in interface_addresses:
                if address.family == 2:  # AF_INET (IPv4)
                    ip_address = address.address
                    break
            if ip_address != "Unknown":
                break
    except Exception as e:
        current_app.logger.warning(f"Error getting IP address: {str(e)}")
        pass
    
    # Get Raspberry Pi model
    pi_model = "Unknown"
    try:
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as f:
                pi_model = f.read().strip()
    except Exception:
        pass
    
    # System load
    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
    
    return {
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count(logical=True),
            'physical_cores': psutil.cpu_count(logical=False),
            'load_avg_1min': load_avg[0],
            'load_avg_5min': load_avg[1],
            'load_avg_15min': load_avg[2]
        },
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'total_formatted': format_bytes(memory.total),
            'available_formatted': format_bytes(memory.available),
            'used_formatted': format_bytes(memory.used)
        },
        'disk': {
            'total': disk['total'],
            'used': disk['used'],
            'free': disk['free'],
            'percent': disk['percent'],
            'total_formatted': format_bytes(disk['total']),
            'used_formatted': format_bytes(disk['used']),
            'free_formatted': format_bytes(disk['free'])
        },
        'temperature': temperature,
        'uptime': uptime,
        'uptime_formatted': format_uptime(uptime),
        'network': {
            'bytes_sent': network_io.bytes_sent,
            'bytes_recv': network_io.bytes_recv,
            'bytes_sent_formatted': format_bytes(network_io.bytes_sent),
            'bytes_recv_formatted': format_bytes(network_io.bytes_recv)
        },
        'system': {
            'platform': platform.platform(),
            'pi_model': pi_model,
            'ip_address': ip_address,
            'hostname': platform.node(),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }

def get_disk_usage(path='/'):
    """
    Get disk usage for the specified path.
    
    Args:
        path (str): Path to check disk usage for
        
    Returns:
        dict: Disk usage information
    """
    disk_usage = psutil.disk_usage(path)
    return {
        'total': disk_usage.total,
        'used': disk_usage.used,
        'free': disk_usage.free,
        'percent': disk_usage.percent
    }

def get_temperature():
    """
    Get CPU temperature.
    
    Returns:
        float: CPU temperature in Celsius or None if not available
    """
    # First try the Raspberry Pi specific method
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            return float(f.read()) / 1000.0
    except (FileNotFoundError, IOError, ValueError):
        pass
    
    # Try using psutil (requires newer version)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Look for CPU temperature in various keys based on system
            for name, entries in temps.items():
                if name.lower() in ['cpu_thermal', 'cpu-thermal', 'coretemp']:
                    if entries:
                        return entries[0].current
    except (AttributeError, IndexError):
        pass
    
    # Temperature not available
    return None

def get_uptime():
    """
    Get system uptime in seconds.
    
    Returns:
        int: System uptime in seconds
    """
    return int(time.time() - psutil.boot_time())

def format_uptime(seconds):
    """
    Format uptime in seconds to a human-readable string.
    
    Args:
        seconds (int): Uptime in seconds
        
    Returns:
        str: Formatted uptime string (e.g. "2d 5h 30m")
    """
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def format_bytes(bytes_value):
    """
    Format bytes to a human-readable string.
    
    Args:
        bytes_value (int): Bytes value
        
    Returns:
        str: Formatted string (e.g. "1.2 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024 or unit == 'TB':
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024

def get_log_file_list():
    """
    Get a list of available log files.
    
    Returns:
        list: List of log file information (dict with name, path, size, modified)
    """
    log_files = []
    
    # Check app logs directory
    app_logs_dir = Path(current_app.root_path).parent / 'logs'
    if app_logs_dir.exists():
        for file in app_logs_dir.glob('*.log*'):
            stats = file.stat()
            log_files.append({
                'name': file.name,
                'path': str(file),
                'size': stats.st_size,
                'size_formatted': format_bytes(stats.st_size),
                'modified': datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Check system logs - focused on relevant ones
    system_logs = [
        '/var/log/syslog', 
        '/var/log/auth.log',
        '/var/log/daemon.log',
        '/var/log/messages'
    ]
    
    # Add creaturebox-specific logs if they exist
    creaturebox_logs = Path('/var/log').glob('creaturebox*.log')
    system_logs.extend([str(log) for log in creaturebox_logs])
    
    for log_path in system_logs:
        log_file = Path(log_path)
        if log_file.exists() and log_file.is_file():
            try:
                stats = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stats.st_size,
                    'size_formatted': format_bytes(stats.st_size),
                    'modified': datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            except (PermissionError, OSError):
                # Skip files we can't access
                pass
    
    # Sort by modified time (newest first)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    return log_files

def get_logs(log_file, max_lines=1000):
    """
    Get log entries from a log file.
    
    Args:
        log_file (str): Name of the log file to read
        max_lines (int): Maximum number of lines to read
        
    Returns:
        list: List of log entries (each a dict with timestamp, level, message, etc.)
    """
    log_entries = []
    
    # Check app logs directory first
    app_logs_dir = Path(current_app.root_path).parent / 'logs'
    app_log_path = app_logs_dir / log_file
    
    # Check system logs if not found in app logs
    system_log_path = Path('/var/log') / log_file
    
    log_path = app_log_path if app_log_path.exists() else system_log_path
    
    if not log_path.exists():
        return log_entries
    
    try:
        # Use tail-like approach to get the last N lines
        # This is more efficient for large log files
        with open(log_path, 'r', errors='replace') as f:
            # Read the last chunk of the file that should contain max_lines
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            
            # Estimate bytes to read based on average line length
            avg_line_length = 200  # Estimate
            bytes_to_read = min(file_size, avg_line_length * max_lines)
            
            # Read the last chunk
            f.seek(max(0, file_size - bytes_to_read), os.SEEK_SET)
            lines = f.readlines()
            
            # Take the last max_lines
            lines = lines[-max_lines:]
            
            # Parse each line
            for line in lines:
                entry = parse_log_line(line.strip())
                if entry:
                    log_entries.append(entry)
    except (PermissionError, OSError) as e:
        current_app.logger.error(f"Error reading log file {log_file}: {str(e)}")
    
    return log_entries

def parse_log_line(line):
    """
    Parse a log line into structured data.
    
    Args:
        line (str): Log line to parse
        
    Returns:
        dict: Parsed log entry or None if parsing failed
    """
    # Default entry with raw line
    entry = {
        'raw': line,
        'timestamp': None,
        'level': 'UNKNOWN',
        'message': line,
        'source': None
    }
    
    # Try several common log formats
    
    # Format: 2023-01-01 12:34:56,789 ERROR: message [in file.py:123]
    flask_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) ([A-Z]+): (.*?) \[in (.*?):(\d+)\]', line)
    if flask_match:
        entry['timestamp'] = flask_match.group(1)
        entry['level'] = flask_match.group(2)
        entry['message'] = flask_match.group(3)
        entry['source'] = f"{flask_match.group(4)}:{flask_match.group(5)}"
        return entry
    
    # Format: Jan  1 12:34:56 hostname service[123]: message
    syslog_match = re.match(r'([A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}) (\S+) ([^:]+): (.*)', line)
    if syslog_match:
        entry['timestamp'] = syslog_match.group(1)
        entry['source'] = f"{syslog_match.group(2)} {syslog_match.group(3)}"
        entry['message'] = syslog_match.group(4)
        
        # Try to determine log level from message
        if re.search(r'\b(ERROR|CRITICAL|FATAL)\b', entry['message'], re.IGNORECASE):
            entry['level'] = 'ERROR'
        elif re.search(r'\bWARN(?:ING)?\b', entry['message'], re.IGNORECASE):
            entry['level'] = 'WARNING'
        elif re.search(r'\bINFO\b', entry['message'], re.IGNORECASE):
            entry['level'] = 'INFO'
        elif re.search(r'\bDEBUG\b', entry['message'], re.IGNORECASE):
            entry['level'] = 'DEBUG'
        return entry
    
    # Format: 2023-01-01T12:34:56.789Z LEVEL message
    iso_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z) ([A-Z]+) (.*)', line)
    if iso_match:
        entry['timestamp'] = iso_match.group(1)
        entry['level'] = iso_match.group(2)
        entry['message'] = iso_match.group(3)
        return entry
    
    # If no format matched, just return the default entry
    return entry

def filter_logs(logs, severity=None, start_date=None, end_date=None, search=None):
    """
    Filter log entries by various criteria.
    
    Args:
        logs (list): List of log entries
        severity (str): Severity level to filter by
        start_date (str): Start date for filtering (YYYY-MM-DD)
        end_date (str): End date for filtering (YYYY-MM-DD)
        search (str): Search term to filter by
        
    Returns:
        list: Filtered log entries
    """
    filtered_logs = logs
    
    # Filter by severity
    if severity:
        filtered_logs = [log for log in filtered_logs if log.get('level') == severity.upper()]
    
    # Filter by date range
    if start_date or end_date:
        # Convert to datetime objects for comparison
        if start_date:
            try:
                start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                start_dt = None
        else:
            start_dt = None
            
        if end_date:
            try:
                # Add one day to end_date to include the entire end date
                end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
            except ValueError:
                end_dt = None
        else:
            end_dt = None
        
        # Filter logs with timestamp
        filtered_logs = [
            log for log in filtered_logs 
            if log.get('timestamp') and is_log_in_date_range(log.get('timestamp'), start_dt, end_dt)
        ]
    
    # Filter by search term
    if search:
        search_lower = search.lower()
        filtered_logs = [
            log for log in filtered_logs 
            if search_lower in log.get('raw', '').lower() or 
               search_lower in log.get('message', '').lower()
        ]
    
    return filtered_logs

def is_log_in_date_range(timestamp_str, start_dt, end_dt):
    """
    Check if a log timestamp is within a date range.
    
    Args:
        timestamp_str (str): Timestamp string from log
        start_dt (datetime): Start datetime or None
        end_dt (datetime): End datetime or None
        
    Returns:
        bool: True if log is in range, False otherwise
    """
    # Try to parse timestamp - handle multiple formats
    timestamp_dt = None
    
    # Try common formats
    formats = [
        '%Y-%m-%d %H:%M:%S,%f',  # 2023-01-01 12:34:56,789
        '%Y-%m-%dT%H:%M:%S.%fZ',  # 2023-01-01T12:34:56.789Z
        '%b %d %H:%M:%S'  # Jan  1 12:34:56
    ]
    
    for fmt in formats:
        try:
            timestamp_dt = datetime.datetime.strptime(timestamp_str, fmt)
            break
        except ValueError:
            continue
    
    # If we couldn't parse the timestamp, assume it's in range
    if timestamp_dt is None:
        return True
    
    # Check against date range
    if start_dt and timestamp_dt < start_dt:
        return False
    if end_dt and timestamp_dt > end_dt:
        return False
    
    return True

def get_process_info(name=None):
    """
    Get information about running processes.
    
    Args:
        name (str): Optional name filter
        
    Returns:
        list: List of process information
    """
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent', 'create_time']):
        try:
            proc_info = proc.info
            
            # Skip if name filter is provided and doesn't match
            if name and name.lower() not in proc_info['name'].lower():
                continue
                
            processes.append({
                'pid': proc_info['pid'],
                'name': proc_info['name'],
                'username': proc_info['username'],
                'memory_percent': proc_info['memory_percent'],
                'cpu_percent': proc_info['cpu_percent'],
                'create_time': datetime.datetime.fromtimestamp(proc_info['create_time']).strftime('%Y-%m-%d %H:%M:%S'),
                'uptime_seconds': int(time.time() - proc_info['create_time']),
                'uptime': format_uptime(int(time.time() - proc_info['create_time']))
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by memory usage (highest first)
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    
    return processes

def run_subprocess(cmd, timeout=10):
    """
    Run a subprocess securely with timeout.
    
    Args:
        cmd (list): Command and arguments as a list
        timeout (int): Timeout in seconds
        
    Returns:
        dict: Result with stdout, stderr, and return code
    """
    try:
        # Using subprocess.run with explicit arguments for security
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Don't raise exception on non-zero return code
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }
