; Inno Setup Script
; Installiere Inno Setup: https://jrsoftware.org/isinfo.php
; Dann kompilieren mit: ISCC.exe installer.iss

#define MyAppName "AutoClicker"
#define MyAppVersion "1.0"
#define MyAppPublisher "Aurora Development"
#define MyAppExeName "AutoClicker.exe"
#define MyUpdateExeName "update.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=AutoClicker_v{#MyAppVersion}_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktopverkn&uuml;pfung erstellen"; GroupDescription: "Zus&auml;tzliche Symbole:"
Name: "autostart"; Description: "AutoClicker beim Windows-Start automatisch starten"; GroupDescription: "Autostart:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyUpdateExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Nach Updates suchen"; Filename: "{app}\{#MyUpdateExeName}"; WorkingDir: "{app}"
Name: "{group}\Deinstallieren"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{commonstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "AutoClicker starten"; Flags: postinstall nowait skipifsilent
