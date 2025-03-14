# Troubleshooting Camera Issues

This guide provides steps to diagnose and resolve common issues with the camera control module in the Creaturebox Web Interface.

## Common Issues

### JSON Format Errors

If you see JSON-related errors in the browser console when trying to use camera functions, this typically indicates that the script output isn't being properly formatted as JSON.

**Symptoms:**
- "SyntaxError: Unexpected token in JSON at position X" in browser console
- Camera operations fail with "Invalid response format" error

**Solutions:**

1. **Check Camera Debug Page**

   Navigate to the Camera Control page and click the "Debug" button in the top-right corner to access the diagnostic page. This page will help identify path and script issues.

2. **Ensure Wrapper Scripts Exist**

   The application uses wrapper scripts to format the output from the camera scripts as JSON. Ensure these wrapper scripts exist and are executable:

   ```bash
   # Check if wrapper scripts exist
   ls -la /opt/creaturebox_web/software/TakePhoto_wrapper.py
   ls -la /opt/creaturebox_web/software/CheckCamera_wrapper.py
   
   # Make sure they're executable
   chmod +x /opt/creaturebox_web/software/TakePhoto_wrapper.py
   chmod +x /opt/creaturebox_web/software/CheckCamera_wrapper.py
   ```

3. **Run Path Validation**

   The application includes a path validation script that can automatically fix common issues:

   ```bash
   cd /opt/creaturebox_web
   python scripts/validate_paths.py --verbose --fix
   ```

4. **Test Scripts Directly**

   You can test the wrapper scripts directly to see if they produce valid JSON:

   ```bash
   python /opt/creaturebox_web/software/TakePhoto_wrapper.py
   ```

   This should output a JSON object containing `success`, `output`, and other fields.

### Modal Dialog Display Issues

If the modal dialog that shows script output has formatting issues or doesn't display properly:

**Symptoms:**
- Modal dialog appears but content is not properly formatted
- Text overflows or is cut off in the dialog

**Solutions:**

1. **Toggle Raw Output**

   The modal dialog includes a "Toggle Raw Output" button that lets you switch between formatted and raw output. This can help diagnose issues with the output format.

2. **Check Browser Console**

   Open your browser's developer tools (F12 or Ctrl+Shift+I) and check the console for any JavaScript errors that might be affecting the modal display.

3. **Clear Browser Cache**

   Clear your browser's cache and cookies to ensure you're getting the latest CSS and JavaScript files:

   ```
   Ctrl+Shift+Delete in most browsers
   ```

4. **Restart the Web Application**

   ```bash
   sudo systemctl restart creaturebox-web
   ```

### Script Path Resolution Issues

If the application can't find the camera scripts:

**Symptoms:**
- "Script not found" errors
- Camera operations fail immediately

**Solutions:**

1. **Check Script Paths**

   Use the debug page to see where the application is looking for scripts. Make sure the scripts exist in the expected locations.

2. **Update Script Inventory**

   If scripts are in a different location than expected, you can update the script inventory in:
   
   ```
   /opt/creaturebox_web/app/control/script_inventory.py
   ```

3. **Fix Permissions**

   Make sure the application has permission to execute the scripts:

   ```bash
   sudo chown -R creature:creature /opt/creaturebox_web/software
   sudo chmod -R 755 /opt/creaturebox_web/software
   ```

## Advanced Troubleshooting

### Enabling Debug Logging

To get more detailed information about script execution, you can enable debug logging:

1. Edit the logging configuration:

   ```bash
   sudo nano /opt/creaturebox_web/instance/config.py
   ```

2. Add or modify the LOG_LEVEL setting:

   ```python
   LOG_LEVEL = 'DEBUG'
   ```

3. Restart the application:

   ```bash
   sudo systemctl restart creaturebox-web
   ```

4. View the logs:

   ```bash
   sudo journalctl -u creaturebox-web -f
   ```

### Recreating Wrapper Scripts

If the wrapper scripts are missing or corrupted, you can recreate them using the path validation script:

```bash
cd /opt/creaturebox_web
python scripts/validate_paths.py --verbose --fix
```

### Testing Direct Script Execution

Sometimes it helps to test the camera scripts directly:

```bash
# Navigate to the software directory
cd /opt/creaturebox_web/software

# Test CheckCamera script
python CheckCamera.py

# Test TakePhoto script
python TakePhoto.py
```

Compare this output with what the wrapper scripts produce:

```bash
python TakePhoto_wrapper.py
```

The wrapper should produce valid JSON output that includes the original script's output.

## Reporting Issues

If you've tried the troubleshooting steps above and are still experiencing issues, collect the following information for support:

1. Output from the debug page
2. Browser console logs (press F12, then go to the Console tab)
3. Application logs:
   ```
   sudo journalctl -u creaturebox-web --since "1 hour ago"
   ```
4. Output from running the scripts directly
