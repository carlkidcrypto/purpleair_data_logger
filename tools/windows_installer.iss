; Inno Setup Script for PurpleAir Data Logger
; Cross-platform PurpleAir Air-Quality Telemetry Engine

#ifndef AppVersion
#define AppVersion "2026.11.3a0"
#endif

#ifndef SourceExe
#define SourceExe "..\dist\PurpleAirDataLogger.exe"
#endif

[Setup]
AppId={{B7C9F812-3D4A-491B-8E72-554F912A6D3C}
AppName=PurpleAir Data Logger
AppVersion={#AppVersion}
AppVerName=PurpleAir Data Logger {#AppVersion}
AppPublisher=carlkidcrypto
AppPublisherURL=https://carlkidcrypto.github.io/purpleair_data_logger/
AppSupportURL=https://github.com/carlkidcrypto/purpleair_data_logger/issues
AppUpdatesURL=https://github.com/carlkidcrypto/purpleair_data_logger/releases
DefaultDirName={autopf}\PurpleAirDataLogger
DefaultGroupName=PurpleAir Data Logger
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=PurpleAirDataLogger-Windows-x64-Setup
SetupIconFile=..\purpleair_data_logger\gui\static\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "envPath"; Description: "Add application to PATH environment variable (allows running 'purpleair-data-logger' or 'PurpleAirDataLogger' from command prompt)"; Flags: unchecked

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "PurpleAirDataLogger.exe"; Flags: ignoreversion
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "purpleair-data-logger.exe"; Flags: ignoreversion
Source: "..\purpleair_data_logger\gui\static\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\PurpleAir Data Logger"; Filename: "{app}\PurpleAirDataLogger.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{autodesktop}\PurpleAir Data Logger"; Filename: "{app}\PurpleAirDataLogger.exe"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Tasks: envPath; Check: NeedsAddPath(ExpandConstant('{app}'))

[Run]
Filename: "{app}\PurpleAirDataLogger.exe"; Description: "{cm:LaunchProgram,PurpleAir Data Logger}"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + UpperCase(Param) + ';', ';' + UpperCase(OrigPath) + ';') = 0;
end;
