; DoganAI Compliance Kit - NSIS Installer Script
; Creates a professional Windows installer for the portable application

!define APPNAME "DoganAI Compliance Kit"
!define COMPANYNAME "DoganAI Lab"
!define DESCRIPTION "Saudi Arabia Regulatory Compliance Platform"
!define VERSIONMAJOR 2
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://doganai.com/support"
!define UPDATEURL "https://doganai.com/updates"
!define ABOUTURL "https://doganai.com"
!define INSTALLSIZE 512000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES64\${COMPANYNAME}\${APPNAME}"
LicenseData "assets\LICENSE.txt"
Name "${APPNAME}"
Icon "assets\icon.ico"
outFile "DoganAI-Compliance-Kit-Setup.exe"

!include LogicLib.nsh

page license
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    
    ; Copy all files
    file /r "build\*.*"
    
    ; Create uninstaller
    writeUninstaller "$INSTDIR\uninstall.exe"
    
    ; Start menu shortcuts
    createDirectory "$SMPROGRAMS\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\assets\icon.ico"
    createShortCut "$SMPROGRAMS\${COMPANYNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Desktop shortcut
    createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\assets\icon.ico"
    
    ; Registry information for add/remove programs
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\assets\icon.ico$\""
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    writeRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    writeRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    writeRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    writeRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    writeRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    writeRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; Firewall rules (optional)
    nsExec::ExecToLog 'netsh advfirewall firewall add rule name="${APPNAME} Backend" dir=in action=allow protocol=TCP localport=8000'
    nsExec::ExecToLog 'netsh advfirewall firewall add rule name="${APPNAME} Frontend" dir=in action=allow protocol=TCP localport=3000'
    
sectionEnd

section "uninstall"
    ; Remove firewall rules
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="${APPNAME} Backend"'
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="${APPNAME} Frontend"'
    
    ; Remove Start Menu launcher
    delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${COMPANYNAME}\Uninstall.lnk"
    rmDir "$SMPROGRAMS\${COMPANYNAME}"
    
    ; Remove desktop shortcut
    delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove files
    rmDir /r "$INSTDIR"
    
    ; Remove uninstaller information from the registry
    deleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
sectionEnd
