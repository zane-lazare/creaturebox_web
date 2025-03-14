"""
Background task processing for the Photos module.

Handles thumbnail generation and other long-running tasks in a way that's 
resistant to interruptions like system shutdowns.
"""

import os
import time
import json
import logging
import threading
import queue
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Task status constants
STATUS_PENDING = 'pending'
STATUS_PROCESSING = 'processing'
STATUS_COMPLETED = 'completed'
STATUS_FAILED = 'failed'
STATUS_INTERRUPTED = 'interrupted'

# Task queue and worker thread
task_queue = queue.Queue()
worker_thread = None
worker_running = False
task_registry = {}

# Task state persistence
TASKS_STATE_FILE = None  # Will be set at initialization


def initialize(base_dir: str) -> None:
    """Initialize the task system with proper state file location."""
    global TASKS_STATE_FILE
    
    # Set the state file path
    state_dir = os.path.join(base_dir, 'instance', 'state')
    os.makedirs(state_dir, exist_ok=True)
    TASKS_STATE_FILE = os.path.join(state_dir, 'photo_tasks.json')
    
    # Load any existing tasks
    _load_tasks_state()
    
    # Start the worker thread
    start_worker()


def start_worker() -> None:
    """Start the background worker thread if not already running."""
    global worker_thread, worker_running
    
    if worker_thread is None or not worker_thread.is_alive():
        worker_running = True
        worker_thread = threading.Thread(target=_worker_loop, daemon=True)
        worker_thread.start()
        logger.info("Background worker thread started")


def stop_worker(wait: bool = True, timeout: int = 5) -> None:
    """
    Stop the background worker thread.
    
    Args:
        wait: Whether to wait for current task to complete
        timeout: Maximum time to wait in seconds
    """
    global worker_running
    
    if worker_thread and worker_thread.is_alive():
        logger.info("Stopping background worker thread...")
        worker_running = False
        
        # Clear the queue to prevent processing additional tasks
        while not task_queue.empty():
            try:
                task_queue.get_nowait()
                task_queue.task_done()
            except queue.Empty:
                break
        
        # Add a sentinel task to unblock the worker
        task_queue.put(None)
        
        # Wait for the worker to finish current task
        if wait and worker_thread.is_alive():
            worker_thread.join(timeout)
            if worker_thread.is_alive():
                logger.warning("Worker thread did not terminate gracefully within timeout")
        
        # Save current state
        _save_tasks_state()
        logger.info("Background worker thread stopped")


def _worker_loop() -> None:
    """Main worker thread loop."""
    global worker_running
    logger.info("Worker loop started")
    
    while worker_running:
        try:
            # Get the next task
            task = task_queue.get(timeout=1.0)
            
            # Check for sentinel task
            if task is None:
                task_queue.task_done()
                continue
            
            task_id = task.get('id')
            
            # Process the task
            try:
                logger.info(f"Processing task {task_id}: {task.get('type')}")
                task['status'] = STATUS_PROCESSING
                task['started_at'] = time.time()
                _save_tasks_state()  # Save state before processing
                
                # Execute the task function
                result = task['func'](*task.get('args', []), **task.get('kwargs', {}))
                
                # Update task state
                task['status'] = STATUS_COMPLETED
                task['completed_at'] = time.time()
                task['result'] = result
                
                logger.info(f"Task {task_id} completed successfully")
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {str(e)}")
                task['status'] = STATUS_FAILED
                task['error'] = str(e)
            finally:
                _save_tasks_state()  # Save state after processing
                task_queue.task_done()
        
        except queue.Empty:
            # Timeout - opportunity to check if we should keep running
            pass
        except Exception as e:
            logger.error(f"Error in worker loop: {str(e)}")
    
    # Mark incomplete tasks as interrupted
    for task_id, task in task_registry.items():
        if task['status'] in (STATUS_PENDING, STATUS_PROCESSING):
            task['status'] = STATUS_INTERRUPTED
    
    # Save final state before exit
    _save_tasks_state()
    logger.info("Worker loop exited")


def enqueue_task(
    task_type: str, 
    func: Callable, 
    *args, 
    **kwargs
) -> str:
    """
    Enqueue a new task to be processed in the background.
    
    Args:
        task_type: Type of task (used for identification)
        func: Function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Task ID
    """
    # Generate a unique ID
    task_id = f"{task_type}_{int(time.time())}_{len(task_registry) + 1}"
    
    # Create task record
    task = {
        'id': task_id,
        'type': task_type,
        'status': STATUS_PENDING,
        'created_at': time.time(),
        'func': func,
        'args': args,
        'kwargs': kwargs
    }
    
    # Register the task
    task_registry[task_id] = task
    
    # Add to processing queue
    task_queue.put(task)
    logger.info(f"Task {task_id} ({task_type}) enqueued")
    
    # Make sure worker is running
    start_worker()
    
    # Save task state
    _save_tasks_state()
    
    return task_id


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        Task status information
    """
    task = task_registry.get(task_id)
    if not task:
        return {'status': 'unknown', 'error': 'Task not found'}
    
    # Return a sanitized copy without the function and arguments
    status = {k: v for k, v in task.items() if k not in ('func', 'args', 'kwargs')}
    return status


def get_all_tasks(task_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get status of all tasks, optionally filtered by type.
    
    Args:
        task_type: Optional type to filter by
        
    Returns:
        List of task status information
    """
    tasks = []
    for task_id, task in task_registry.items():
        if task_type is None or task.get('type') == task_type:
            # Return a sanitized copy
            status = {k: v for k, v in task.items() if k not in ('func', 'args', 'kwargs')}
            tasks.append(status)
    
    # Sort by creation time, newest first
    tasks.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    return tasks


def _save_tasks_state() -> None:
    """Save task registry to disk for persistence across restarts."""
    if not TASKS_STATE_FILE:
        logger.warning("Task state file not configured, state will not persist")
        return
        
    try:
        # Create a serializable copy of the registry
        serializable_tasks = {}
        for task_id, task in task_registry.items():
            # Skip completed tasks older than a day to prevent the state file from growing too large
            if (task.get('status') == STATUS_COMPLETED and 
                task.get('completed_at', 0) < time.time() - 86400):
                continue
                
            # Create a copy without the function and arguments
            task_copy = {k: v for k, v in task.items() if k not in ('func', 'args', 'kwargs')}
            serializable_tasks[task_id] = task_copy
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(TASKS_STATE_FILE), exist_ok=True)
        
        # Write atomically by using a temporary file
        temp_file = f"{TASKS_STATE_FILE}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(serializable_tasks, f, indent=2)
        
        # Rename to final location (atomic on most platforms)
        os.replace(temp_file, TASKS_STATE_FILE)
        
    except Exception as e:
        logger.error(f"Error saving task state: {str(e)}")


def _load_tasks_state() -> None:
    """Load task registry from disk."""
    global task_registry
    
    if not TASKS_STATE_FILE:
        logger.warning("Task state file not configured, no state will be loaded")
        return
        
    if not os.path.exists(TASKS_STATE_FILE):
        logger.info("No task state file found, starting with empty registry")
        return
        
    try:
        with open(TASKS_STATE_FILE, 'r') as f:
            loaded_tasks = json.load(f)
        
        # Restore tasks but mark processing ones as interrupted
        for task_id, task in loaded_tasks.items():
            if task['status'] in (STATUS_PENDING, STATUS_PROCESSING):
                task['status'] = STATUS_INTERRUPTED
                task['error'] = "Task was interrupted by system shutdown"
            
            # Add to registry (function will be None)
            task_registry[task_id] = task
        
        logger.info(f"Loaded {len(loaded_tasks)} tasks from state file")
        
    except Exception as e:
        logger.error(f"Error loading task state: {str(e)}")
        # Start with empty registry
        task_registry = {}


def cleanup_tasks(max_age_days: int = 7) -> int:
    """
    Clean up old completed and failed tasks.
    
    Args:
        max_age_days: Maximum age of tasks to keep in days
        
    Returns:
        Number of tasks removed
    """
    max_age = time.time() - (max_age_days * 86400)
    to_remove = []
    
    for task_id, task in task_registry.items():
        # Remove completed/failed tasks older than max_age
        if task['status'] in (STATUS_COMPLETED, STATUS_FAILED):
            created_at = task.get('created_at', 0)
            if created_at < max_age:
                to_remove.append(task_id)
    
    # Remove the tasks
    for task_id in to_remove:
        task_registry.pop(task_id, None)
    
    # Save the updated registry
    _save_tasks_state()
    
    return len(to_remove)
