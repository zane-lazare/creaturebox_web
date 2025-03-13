# Troubleshooting Guide

This guide provides solutions to common issues you might encounter with the Creaturebox Web Interface.

## Installation Issues

### Installation Script Fails

**Symptoms**: The installation script exits with an error.

**Possible Causes and Solutions**:

- **Python Version**: Ensure you have Python 3.9 or higher installed. Check with `python3 --version`.
- **Permission Issues**: Run the script with sudo (`sudo ./scripts/install.sh`).
- **Missing Dependencies**: Make sure your system is up to date (`sudo apt update && sudo apt upgrade`).
- **Network Issues**: Check your internet connection to download dependencies.

### Service Won't Start

**Symptoms**: The Creaturebox Web service won't start after installation.

**Possible Causes and Solutions**:

- **Check the status**: Run `sudo systemctl status creaturebox-web`.
- **Check logs**: Run `sudo journalctl -u creaturebox-web` to see error messages.
- **Path issues**: Ensure the paths in the service file are correct.
- **Permission problems**: Check file and directory permissions.

## Authentication Issues

### Can't Log In

**Symptoms**: Unable to log in despite using the correct password.

**Possible Causes and Solutions**:

- **Default Password**: The default password is `creaturebox`.
- **Cookies or Cache**: Try clearing your browser's cache and cookies.
- **Session Issues**: Restart the service (`sudo systemctl restart creaturebox-web`).

### Session Expires Too Quickly

**Symptoms**: You are logged out too frequently.

**Solutions**:

- Check your browser's cookie settings.
- Adjust the session lifetime in the configuration.

## UI Issues

### Interface Doesn't Load Properly

**Symptoms**: The web interface appears broken or unstyled.

**Solutions**:

- Clear your browser cache.
- Try a different browser.
- Check browser console for errors.
- Ensure all static files are properly served.

### Mobile Display Problems

**Symptoms**: Interface doesn't display correctly on mobile devices.

**Solutions**:

- Ensure you're using a modern, up-to-date browser.
- Try rotating your device.
- Check zoom level settings.

## System Integration Issues

### System Information Not Showing

**Symptoms**: Dashboard shows zeros or dashes for system metrics.

**Solutions**:

- Check if the service has permissions to access system information.
- Verify the integration paths are correctly configured.
- Restart the service.

### Camera Controls Not Working

**Symptoms**: Unable to control the camera or lights.

**Solutions**:

- Check hardware connections.
- Verify the software has permissions to access hardware.
- Check integration paths and configuration.

## Performance Issues

### Slow Interface

**Symptoms**: The web interface is slow to respond.

**Solutions**:

- Check system resource usage.
- Clean up old log files or photos if disk space is low.
- Restart the service or the Raspberry Pi.

### High CPU or Memory Usage

**Symptoms**: The service is consuming excessive resources.

**Solutions**:

- Check for memory leaks or runaway processes.
- Monitor the logs for errors causing loops.
- Verify that background tasks complete properly.
- Limit the number of concurrent operations.

## File System Issues

### Cannot View Photos

**Symptoms**: Photos are not visible in the interface or show as broken links.

**Solutions**:

- Check that the photos directory path is configured correctly.
- Verify file permissions allow the web service to read files.
- Ensure photo files have correct extensions (.jpg, .png, etc.).
- Check for corrupted image files.

### Upload or Download Errors

**Symptoms**: Cannot upload or download files.

**Solutions**:

- Check disk space availability.
- Verify write permissions on target directories.
- Check for file size limitations in your configuration.
- Ensure temporary directories are properly configured.

## Network Issues

### Cannot Access Interface Remotely

**Symptoms**: Unable to access the web interface from other devices.

**Solutions**:

- Check firewall settings on the Raspberry Pi (`sudo iptables -L`).
- Verify the service is bound to the correct network interface (not just localhost).
- Ensure port 80 (or your configured port) is accessible.
- Check if Nginx is properly configured and running.

### Intermittent Connection Issues

**Symptoms**: The connection to the interface drops or times out.

**Solutions**:

- Check network stability between your device and the Raspberry Pi.
- Verify there are no conflicting services using the same port.
- Check for resource constraints that might cause the service to become unresponsive.

## Update Issues

### Failed Update

**Symptoms**: Unable to update the software or changes don't take effect.

**Solutions**:

- Check permissions on application directories.
- Verify there is sufficient disk space.
- Ensure all services are properly restarted after update.
- Check logs for specific error messages during the update process.

## Logging Issues

### Missing or Incomplete Logs

**Symptoms**: Logs are not being generated or are missing important information.

**Solutions**:

- Check log directory permissions.
- Verify log configuration in config files.
- Ensure log rotation is set up properly.
- Check disk space for the log partition.

## Getting Help

If you're unable to resolve an issue using this troubleshooting guide:

1. Check the complete logs for detailed error messages.
2. Take screenshots of any error messages or unusual behavior.
3. Note the exact steps that reproduce the issue.
4. Note your system specifications and installation method.
5. Contact support with this information.

## Common Commands for Troubleshooting

Here are some useful commands for troubleshooting:

```bash
# Check service status
sudo systemctl status creaturebox-web

# View service logs
sudo journalctl -u creaturebox-web

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep creaturebox

# Restart the service
sudo systemctl restart creaturebox-web

# Test nginx configuration
sudo nginx -t

# Check open ports
sudo netstat -tuln

# Check Python version
python3 --version

# Check for network connectivity
ping -c 4 google.com
```
