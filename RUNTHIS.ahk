#Requires AutoHotkey v2.0
#SingleInstance Force
TutorialCompleted := 0
TutorialCompleted := IniRead(A_ScriptDir "\config.ini", "Main", "TutorialCompleted", 0)
Dependenciesinstalled := 0
Dependenciesinstalled := IniRead(A_ScriptDir "\config.ini", "Main", "DependenciesInstalled", 0)

if TutorialCompleted = 0{
    MsgBox("This Tutorial will Show you the Steps of Setting up the Biome Scoper.`n`n(This message was shown since `"TutorialCompleted`" was 0 or not found)", "First Time Boot", "4160")
}

myGui := Gui()
	myGui.Add("GroupBox", "x8 y8 w284 h147", "Settings")
    myGui.Add("Text", "x216 y168 w67 h23 +0x200", "(STOP IS F2)")
    myGui.Add("Text", "x16 y104 w120 h23 +0x200", "Webhook Stuff")
	myGui.Add("Text", "x16 y24 w147 h23 +0x200", "Private Server Link (For Joins)")

	Start := myGui.Add("Button", "x16 y168 w80 h23", "&Start")
    BtnEdit := myGui.Add("Button", "x96 y168 w80 h23", "&Config")
    PLink := myGui.Add("Edit", "x16 y56 w270 h21", "")
    WLink := myGui.Add("Edit", "x16 y128 w270 h21", "")
    DiscordUserID := myGui.Add("Edit", "x90 y105 w190 h21", "")

    PLink.Text := "https://www.roblox.com/share?code=.......&type=Server"
    WLink.Text := "https://discord.com/api/webhooks/......."
    DiscordUserID.Text := "Your Discord User ID"

    WLink.Text := IniRead(A_ScriptDir "\config.ini", "Main", "WebhookLink", "https://discord.com/api/webhooks/.......")
    PLink.Text := IniRead(A_ScriptDir "\config.ini", "Main", "PSLink", "https://www.roblox.com/share?code=.......&type=Server")
    DiscordUserID.Text := IniRead(A_ScriptDir "\config.ini", "Main", "DiscordUserID" , "Discord User ID")

    WLink.OnEvent('Change', (*) => IniWrite(WLink.Value, A_ScriptDir "\config.ini", "Main", "WebhookLink"))
    PLink.OnEvent('Change', (*) => IniWrite(PLink.Value, A_ScriptDir "\config.ini", "Main", "PSLink"))
    DiscordUserID.OnEvent('Change', (*) => IniWrite(DiscordUserID.Value, A_ScriptDir "\config.ini", "Main", "DiscordUserID"))
    Start.OnEvent('Click', (*) => Startfunc())
    BtnEdit.OnEvent('Click', (*) => Run(A_ScriptDir "\Edit.pyw"))

	myGui.OnEvent('Close', (*) => ExitApp())
	myGui.Title := "RexzysBiomeScoper V1.2"
    myGui.Show()

    if +TutorialCompleted = 0{
    MsgBox("This is the Main GUI Here you Can Setup the Basic Serttings!`n`nSettings Include`n- Webhook Link`n- Private Server Link`n- Discord User ID`n`nMost of these Features are Recommended to have filled out.", "First Time Boot", "4160")
    }
    if TutorialCompleted = 0{
        MsgBox("Basic Info`n`nThe Script is Started via the Start Button and is Stopped Via F2.`n`nThere is also a Seperate Config Tab Go Check it out!", "First Time Boot", "4160")
        TutorialCompleted := 1
        IniWrite(TutorialCompleted, A_ScriptDir "\config.ini", "Main", "TutorialCompleted")
        Run(A_ScriptDir "\Edit.pyw")
    }
F2::Run("RUNTHIS.ahk")

Startfunc(*) {
    global Dependenciesinstalled
    myGui.Hide()
    if Dependenciesinstalled = 0{
    userResponse := MsgBox("There are Requirements for Running this Script:`n`n- Bloxstrap (With Discord Activity Traking Enabled)`n- Python3`n- Keyboard`n- Requests`n`nWould you Like to Install these Dependencies via this Script?`n(Bloxstrap cannot be installed via this script only the Install Website will be opened)`n`n(Pressing No will NOT Run the Installers and will countinue with Executing the Script)", "First Time Startup", "4116")
    if (userResponse = "Yes"){
    Run("https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe")
    Sleep(3000)
    MsgBox("Please Run the File and Countinue with the Setup after that press OK")
    Sleep(1000)
    RunWait("cmd.exe /c pip install keyboard requests", "")
    RunWait("https://github.com/bloxstraplabs/bloxstrap/releases/download/v2.9.1/Bloxstrap-v2.9.1.exe")
    MsgBox("Bloxstrap cannot be Installed via this Script, The Website will be Opened, Please Install Bloxstrap with Discord Activity Tracking Enabled, After that press OK")
    MsgBox("Dependencies Installed, You can now use the Script")
    Dependenciesinstalled := 1
    IniWrite(Dependenciesinstalled, A_ScriptDir "\config.ini", "Main", "DependenciesInstalled")
    myGui.Show()
    return
    } else if (userResponse = "No"){
    Dependenciesinstalled := 1
    IniWrite(Dependenciesinstalled, A_ScriptDir "\config.ini", "Main", "DependenciesInstalled")
	Run(A_ScriptDir "\main.py")
    myGui.Hide()
    return
    }}
    Run(A_ScriptDir "\main.py")
    
    myGui.Hide()
}

