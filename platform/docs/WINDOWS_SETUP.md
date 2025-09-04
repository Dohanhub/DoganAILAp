# DoganAI Compliance Kit - Windows Setup Guide

## 🚀 Quick Start - Windows Icon Created!

### ✅ Desktop Shortcut Ready

A **DoganAI Compliance Kit** icon has been created on your desktop and in the Start Menu!

---

## 🖱️ How to Use

### **Method 1: Desktop Icon (Recommended)**
1. **Double-click** the "DoganAI Compliance Kit" icon on your desktop
2. The application will automatically:
   - Start the API server
   - Start the web application
   - Open your browser to the app
3. Wait for the browser to open (usually takes 10-15 seconds)

### **Method 2: Start Menu**
1. Click the **Start** button
2. Search for "DoganAI Compliance Kit"
3. Click the application to launch

### **Method 3: Manual Launch**
```batch
# Navigate to the DoganAI directory
cd "D:\Dogan-Ai\ShahinKit\DoganAI-Compliance-Kit"

# Run the launcher
start-doganai.bat
```

---

## 🌐 Access Points

Once launched, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3001 | Primary web interface |
| **Workflow Simulator** | http://localhost:3001/simulate | Interactive compliance workflow |
| **Health Monitor** | http://localhost:3001/health | System status dashboard |
| **API Documentation** | http://localhost:8000/docs | Technical API reference |

---

## 📋 Prerequisites

### **Required Software**
- ✅ **Python 3.8+** (Already installed)
- ✅ **Node.js 20+** (Already installed)
- ✅ **Windows 10/11** (Compatible)

### **First Time Setup**
If this is your first time running DoganAI:

1. **Install Dependencies** (one-time setup):
   ```batch
   cd "D:\Dogan-Ai\ShahinKit\DoganAI-Compliance-Kit"
   pip install -r requirements.txt
   cd doganai-monorepo\apps\web
   npm install
   ```

2. **Build the Application** (one-time setup):
   ```batch
   cd "D:\Dogan-Ai\ShahinKit\DoganAI-Compliance-Kit\doganai-monorepo\packages\sdk"
   npm run build
   ```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **"Python not found" Error**
- Ensure Python is installed and added to PATH
- Download from: https://python.org

#### **"Node.js not found" Error**
- Ensure Node.js is installed and added to PATH
- Download from: https://nodejs.org

#### **Port Already in Use**
- Close any existing DoganAI instances
- Restart your computer if needed
- Check Task Manager for running processes

#### **Browser Doesn't Open**
- Manually navigate to: http://localhost:3001
- Check Windows Firewall settings
- Try a different browser

### **Manual Troubleshooting**

1. **Check Services**:
   ```batch
   netstat -an | findstr :8000
   netstat -an | findstr :3001
   ```

2. **Restart Services**:
   ```batch
   taskkill /f /im python.exe
   taskkill /f /im node.exe
   ```

3. **Clean Restart**:
   - Close all DoganAI windows
   - Double-click the desktop icon again

---

## 🎯 Features Available

### **✅ Core Features**
- **Bilingual Interface**: English and Arabic support
- **Workflow Simulator**: 7-step compliance process
- **Real-time Monitoring**: Live system status
- **API Integration**: Complete REST API
- **Cross-platform**: Web, desktop, mobile ready

### **✅ Saudi Compliance**
- **NCA Regulations**: Network and cybersecurity
- **CMA Guidelines**: Capital market authority
- **MOI Requirements**: Ministry of interior
- **MoH Standards**: Ministry of health

---

## 📞 Support

### **Quick Help**
- **Application Issues**: Check the console window for error messages
- **Performance**: Ensure sufficient RAM (4GB+ recommended)
- **Network**: Verify no firewall blocking localhost connections

### **Advanced Support**
- **Logs Location**: `D:\Dogan-Ai\ShahinKit\DoganAI-Compliance-Kit\logs\`
- **Configuration**: `D:\Dogan-Ai\ShahinKit\DoganAI-Compliance-Kit\config\`
- **Database**: SQLite files in project directory

---

## 🎉 Success!

**DoganAI Compliance Kit is now ready to use on Windows!**

**Next Steps:**
1. 🖱️ **Double-click the desktop icon** to launch
2. 🌐 **Explore the web interface** at http://localhost:3001
3. 🎨 **Try the workflow simulator** for interactive compliance
4. 📊 **Monitor system health** and performance
5. 📱 **Access from any device** on your network

---

*DoganAI Compliance Kit - AI-powered compliance solution for Saudi regulations*