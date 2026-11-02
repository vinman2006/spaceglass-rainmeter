' ============================================================================
' SPACEGLASS — WINDOWLESS WINDOWS STARTUP LAUNCHER (Installer/start_spaceglass.vbs)
' Starts the local Python FastAPI companion backend on 127.0.0.1:8765 silently
' without flashing a console window, and launches Rainmeter if not already running.
' ============================================================================
Option Explicit

Dim fso, shell, scriptDir, projectRoot, appPyPath, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptDir)
appPyPath = fso.BuildPath(projectRoot, "Backend\app.py")

If fso.FileExists(appPyPath) Then
    cmd = "pythonw.exe """ & appPyPath & """"
    On Error Resume Next
    shell.Run cmd, 0, False
    If Err.Number <> 0 Then
        Err.Clear
        shell.Run "python.exe """ & appPyPath & """", 0, False
    End If
    On Error GoTo 0
End If
