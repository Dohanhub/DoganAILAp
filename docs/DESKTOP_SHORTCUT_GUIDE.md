# DoganAI Compliance Kit - Desktop Shortcut Creation Guide

## ??? Create Desktop Shortcut (Windows)

### **Method 1: Automatic Creation**
Run this PowerShell command as Administrator:

```powershell
# Run this in PowerShell as Administrator
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\DoganAI Compliance Kit.lnk")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c cd /d `"$PWD`" && DoganAI_Launcher.bat"
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.IconLocation = "$PWD\doganai_icon.ico"
$Shortcut.Description = "DoganAI Compliance Kit - Saudi Arabia Enterprise Solution"
$Shortcut.WindowStyle = 1
$Shortcut.Save()
Write-Host "? Desktop shortcut created successfully!"
```

### **Method 2: Manual Creation**

1. **Right-click** on your desktop
2. Select **"New" ? "Shortcut"**
3. For the location, enter:
   ```
   cmd.exe /c cd /d "D:\Dogan-Ai\ShahinKit\DoganAI-Compliance-Kit" && DoganAI_Launcher.bat
   ```
   *(Replace the path with your actual DoganAI folder path)*

4. Click **"Next"**
5. Name it: **"DoganAI Compliance Kit"**
6. Click **"Finish"**

### **Method 3: Copy & Paste Shortcut**

1. Right-click on `DoganAI_Launcher.bat`
2. Select **"Send to" ? "Desktop (create shortcut)"**
3. Rename the shortcut to **"DoganAI Compliance Kit"**

## ?? Custom Icon Setup

### **Download DoganAI Icon**
Create a custom icon file:

```bash
# Create icon directory
mkdir icons

# You can add your custom icon file as 'doganai_icon.ico'
# Or use the default Windows terminal icon
```

### **Set Custom Icon**
1. Right-click the desktop shortcut
2. Select **"Properties"**
3. Click **"Change Icon..."**
4. Browse to your `doganai_icon.ico` file
5. Click **"OK"**

## ?? Quick Launch Features

Your desktop shortcut will open a menu with these options:

```
????????????????????????????????????????????????
?              Choose an Option:               ?
????????????????????????????????????????????????
?  1. ?? Quick Demo (See Performance)         ?
?  2. ?? Start Web API Server                  ?
?  3. ?? Run Performance Tests                 ?
?  4. ?? Setup & Install Dependencies         ?
?  5. ?? Open Documentation                    ?
?  6. ? Exit                                  ?
????????????????????????????????????????????????
```

## ?? What Each Option Does

### **1. ?? Quick Demo**
- Shows performance improvements
- Tests cache, batch processing, compression
- Real Saudi bank scenario simulation
- **No dependencies required**

### **2. ?? Start Web API Server**
- Launches FastAPI server at `http://localhost:8000`
- Auto-installs dependencies if missing
- Provides web interface and API endpoints
- Shows health metrics and performance stats

### **3. ?? Run Performance Tests**
- Comprehensive performance testing
- Concurrent request testing
- Memory usage analysis
- Cache efficiency measurement

### **4. ?? Setup & Install Dependencies**
- Installs all Python packages
- Sets up FastAPI, Redis, monitoring
- Configures security components
- Prepares for production deployment

### **5. ?? Open Documentation**
- Opens README, integration guide
- Shows testing instructions
- Links to online documentation
- API documentation access

## ?? One-Click Access

After creating the shortcut, you can:

1. **Double-click** the desktop icon
2. **Choose option 1** for immediate demo
3. **Choose option 2** to start the web server
4. **Browse to** `http://localhost:8000` for web interface

## ?? Troubleshooting

### **Shortcut Doesn't Work:**
1. Check the path in shortcut properties
2. Make sure `DoganAI_Launcher.bat` exists
3. Verify Python is installed and in PATH

### **Python Not Found:**
1. Install Python from https://python.org
2. Make sure "Add to PATH" is checked during installation
3. Restart command prompt and try again

### **Dependencies Missing:**
1. Use option 4 in the launcher menu
2. Or manually run: `pip install fastapi uvicorn aioredis`

## ?? You're Ready!

Your DoganAI Compliance Kit is now available as a desktop application with one-click access to all features!

**Just double-click the desktop icon and choose what you want to do!** ??????