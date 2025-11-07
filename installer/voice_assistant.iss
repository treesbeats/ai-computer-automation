#define AppVersion GetStringParameter("AppVersion", "1.0.0")

[Setup]
AppName=ChatGPT Voice Assistant
AppVersion={#AppVersion}
AppPublisher=AI Developer
DefaultDirName={autopf}\ChatGPT Voice Assistant
DefaultGroupName=ChatGPT Voice Assistant
UninstallDisplayIcon={app}\VoiceAssistantDashboard.exe
OutputDir={#SourcePath}\Output
OutputBaseFilename=VoiceAssistantSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\VoiceAssistantDashboard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\ChatGPT Voice Assistant"; Filename: "{app}\VoiceAssistantDashboard.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\ChatGPT Voice Assistant"; Filename: "{app}\VoiceAssistantDashboard.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\VoiceAssistantDashboard.exe"; Description: "Launch ChatGPT Voice Assistant"; Flags: nowait postinstall skipifsilent
