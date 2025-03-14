"""
Script Execution Module

This module provides secure functions for executing hardware control scripts
with proper error handling, timeout management, and output parsing.
"""

import os
import re
import subprocess
import logging
import time
import threading
from flask import current_app
from datetime import datetime

from .script_inventory import get_script_path, get_script_info

# Configure logging
logger = logging.getLogger(__name__)

class ScriptExecutionError(Exception):
    """Exception raised for script execution errors."""
    
    def __init__(self, message, stdout=None, stderr=None, return_code=None):
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        super().__init__(self.message)

class ScriptExecutionResult:
    """Class to hold script execution results."""
    
    def __init__(self, success, output=None, error=None, parsed_output=None, execution_time=None):
        self.success = success
        self.output = output
        self.error = error
        self.parsed_output = parsed_output
        self.execution_time = execution_time
        self.timestamp = datetime.now()
    
    def __str__(self):
        if self.success:
            return f"Success: {self.output}"
        return f"Error: {self.error}"


def execute_script(script_name, parameters=None, working_dir=None, timeout=None):
    """
    Securely execute a script with proper error handling.
    
    Args:
        script_name: The name of the script in the inventory
        parameters: Optional list of parameters to pass to the script
        working_dir: Optional working directory for script execution
        timeout: Optional timeout in seconds
        
    Returns:
        ScriptExecutionResult object with execution results
        
    Raises:
        ScriptExecutionError: If the script execution fails
    """
    # Get script information
    script_info = get_script_info(script_name)
    if not script_info:
        raise ValueError(f"Script '{script_name}' not found in inventory")
        
    # Get absolute script path
    script_path = get_script_path(script_name)
    if not script_path or not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_name}")
    
    # Use script's timeout if not specified
    if timeout is None:
        timeout = script_info.get('timeout', 60)
    
    # Prepare command
    command = []
    
    # Add sudo if required
    if script_info.get('requires_sudo', False):
        command.append("/usr/bin/sudo")
        
    # Add python interpreter if it's a Python script
    if script_path.endswith('.py'):
        command.append("python3")
        
    # Add the script path
    command.append(script_path)
    
    # Add parameters if provided
    if parameters:
        command.extend(parameters)
    
    # Log the command being executed
    logger.info(f"Executing: {' '.join(command)}")
    
    # Set working directory
    if not working_dir:
        working_dir = os.path.dirname(script_path)
    
    # Additional debug info for troubleshooting
    logger.info(f"Working directory: {working_dir}")
    logger.info(f"Script directory contents: {os.listdir(working_dir) if os.path.exists(working_dir) else 'Directory not found'}")
        
    start_time = time.time()
    
    try:
        # Execute the command with subprocess
        result = subprocess.run(
            command,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False  # Important for security
        )
        
        execution_time = time.time() - start_time
        
        # Check for errors in the output
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        # Log the output
        logger.debug(f"Script output: {stdout}")
        if stderr:
            logger.warning(f"Script error output: {stderr}")
            
        # More detailed logging for debugging
        logger.debug(f"Command executed: {' '.join(command)}")
        logger.debug(f"Working directory: {working_dir}")
        logger.debug(f"Return code: {result.returncode}")
        
        # Check return code
        if result.returncode != 0:
            error_msg = f"Script '{script_name}' failed with return code {result.returncode}"
            logger.error(error_msg)
            return ScriptExecutionResult(
                success=False,
                output=stdout,
                error=f"{error_msg}: {stderr}",
                execution_time=execution_time
            )
        
        # Try to parse JSON output first if it's a wrapper script
        parsed_output = None
        json_parsed = None
        
        # Check if output might be JSON
        if stdout and (stdout.strip().startswith('{') and stdout.strip().endswith('}')):  
            try:
                json_parsed = json.loads(stdout)
                logger.debug(f"Successfully parsed JSON output: {json_parsed}")
                
                # If it's JSON, use its success value directly
                if 'success' in json_parsed:
                    if not json_parsed['success']:
                        error_msg = json_parsed.get('error', "Unknown error")
                        logger.error(f"Script reported error via JSON: {error_msg}")
                        return ScriptExecutionResult(
                            success=False,
                            output=json_parsed.get('output', stdout),
                            error=error_msg,
                            parsed_output=json_parsed.get('image_path'),
                            execution_time=json_parsed.get('execution_time', execution_time)
                        )
                    
                    # If successful, extract parsed output if available
                    parsed_output = json_parsed.get('image_path')
                    
                    # Return success with the JSON data
                    return ScriptExecutionResult(
                        success=True,
                        output=json_parsed.get('output', stdout),
                        error=None,
                        parsed_output=parsed_output,
                        execution_time=json_parsed.get('execution_time', execution_time)
                    )
            except json.JSONDecodeError as e:
                # Not JSON, continue with regular parsing
                logger.debug(f"Output is not valid JSON: {e}")
        
        # Standard parsing for non-JSON outputs
        # Parse output if pattern exists
        output_pattern = script_info.get('output_pattern')
        if output_pattern and stdout:
            match = re.search(output_pattern, stdout)
            if match:
                parsed_output = match.group(1) if match.groups() else match.group(0)
        
        # Check for success pattern
        success_pattern = script_info.get('success_pattern')
        if success_pattern and not re.search(success_pattern, stdout):
            logger.warning(f"Success pattern not found in script output: {success_pattern}")
            # Still continue if return code was 0
        
        # Check for error patterns
        error_patterns = script_info.get('error_patterns', [])
        for pattern in error_patterns:
            match = re.search(pattern, stdout) or re.search(pattern, stderr)
            if match:
                error_msg = f"Error pattern found in script output: {match.group(0)}"
                logger.error(error_msg)
                return ScriptExecutionResult(
                    success=False,
                    output=stdout,
                    error=error_msg,
                    execution_time=execution_time
                )
        
        # If we got here, the script executed successfully
        return ScriptExecutionResult(
            success=True,
            output=stdout,
            error=stderr if stderr else None,
            parsed_output=parsed_output,
            execution_time=execution_time
        )
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        error_msg = f"Script '{script_name}' timed out after {timeout} seconds"
        logger.error(error_msg)
        return ScriptExecutionResult(
            success=False,
            output=None,
            error=error_msg,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error executing script '{script_name}': {str(e)}"
        logger.error(error_msg)
        return ScriptExecutionResult(
            success=False,
            output=None,
            error=error_msg,
            execution_time=execution_time
        )


def execute_script_async(script_name, parameters=None, working_dir=None, timeout=None, callback=None):
    """
    Execute a script asynchronously in a separate thread.
    
    Args:
        script_name: The name of the script in the inventory
        parameters: Optional list of parameters to pass to the script
        working_dir: Optional working directory for script execution
        timeout: Optional timeout in seconds
        callback: Optional callback function to call with the result
        
    Returns:
        Thread object that is executing the script
    """
    def run_script():
        result = execute_script(script_name, parameters, working_dir, timeout)
        if callback:
            callback(result)
    
    thread = threading.Thread(target=run_script)
    thread.daemon = True  # Make thread a daemon so it doesn't block application exit
    thread.start()
    
    return thread


def check_script_conflicts(script_name):
    """
    Check if running a script would conflict with scheduled or running operations.
    
    Args:
        script_name: The name of the script to check
        
    Returns:
        Tuple of (has_conflict, conflict_description) where has_conflict is a boolean
        and conflict_description is a string describing the conflict if one exists
    """
    # This is a placeholder for conflict detection logic
    # In a real implementation, this would check:
    # 1. Currently running scripts
    # 2. Scheduled operations in cron
    # 3. Hardware resource conflicts
    
    # For now, we always return no conflict
    return (False, None)


def get_running_scripts():
    """
    Get a list of currently running scripts.
    
    Returns:
        List of script names that are currently running
    """
    # This is a placeholder for getting running scripts
    # In a real implementation, this would check for running processes
    
    # For now, we return an empty list
    return []
