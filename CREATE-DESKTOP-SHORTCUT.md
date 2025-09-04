# How to Create a Desktop Shortcut for DoganAI Compliance Kit

## Method 1: Simple Right-Click Method (Recommended)

1. **Navigate to your project folder:**
   ```
   D:\Dogan-Ai\Deployment\DoganAI-Compliance-Kit
   ```

2. **Right-click on `Launch-DoganAI.bat`**

3. **Select "Create shortcut"**

4. **Move the shortcut to your desktop**

5. **Rename it to "DoganAI Compliance Kit"** (optional)

## Method 2: Manual Shortcut Creation

1. **Right-click on your desktop**

2. **Select "New" → "Shortcut"**

3. **Browse to and select:**
   ```
   D:\Dogan-Ai\Deployment\DoganAI-Compliance-Kit\Launch-DoganAI.bat
   ```

4. **Click "Next"**

5. **Name it "DoganAI Compliance Kit"**

6. **Click "Finish"**

## Method 3: PowerShell Script (Advanced)

Run this command in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_desktop_shortcut.ps1
```

## What the Shortcut Does

When you double-click the desktop icon, it will:

1. ✅ Check if all required files are present
2. ✅ Verify Python, Node.js, and Docker are installed
3. ✅ Start the API server (if Python is available)
4. ✅ Start the web interface (if Node.js is available)
5. ✅ Open your browser to the application

## Troubleshooting

If the shortcut doesn't work:

1. **Check that all dependencies are installed:**
   - Python 3.11+
   - Node.js LTS
   - Docker Desktop

2. **Run the diagnostic:**
   ```
   diagnose-issues.bat
   ```

3. **Try the fixed version:**
   ```
   Start-All-Fixed.bat
   ```

## Success!

Once created, you'll have a one-click desktop icon that launches your DoganAI Compliance Kit application! 🎉
