#Requires AutoHotkey v2.0
#SingleInstance Force

Dependenciesinstalled := 0
Dependenciesinstalled := IniRead(A_ScriptDir "\config.ini", "Main", "DependenciesInstalled", 0)

myGui := Gui()
	myGui.Add("GroupBox", "x8 y8 w284 h147", "Settings")
    myGui.Add("Text", "x216 y168 w67 h23 +0x200", "(STOP IS F2)")
    myGui.Add("Text", "x16 y104 w120 h23 +0x200", "Webhook Link")
	myGui.Add("Text", "x16 y24 w147 h23 +0x200", "Private Server Link (For Joins)")

	Start := myGui.Add("Button", "x16 y168 w80 h23", "&Start")
    PLink := myGui.Add("Edit", "x16 y56 w270 h21", "")
    WLink := myGui.Add("Edit", "x16 y128 w270 h21", "")

    PLink.Text := "https://www.roblox.com/share?code=.......&type=Server"
    WLink.Text := "https://discord.com/api/webhooks/......."

    IniRead(A_ScriptDir "\config.ini", "Main", "WebhookLink", WLink.Text)
    IniRead(A_ScriptDir "\config.ini", "Main", "PSLink", PLink.Text)

    WLink.OnEvent('Change', (*) => IniWrite(WLink.Value, A_ScriptDir "\config.ini", "Main", "WebhookLink"))
    PLink.OnEvent('Change', (*) => IniWrite(PLink.Value, A_ScriptDir "\config.ini", "Main", "PSLink"))
    Start.OnEvent('Click', (*) => Startfunc())

	myGui.OnEvent('Close', (*) => ExitApp())
	myGui.Title := "RexzysBiomeScoper V1.0"
    myGui.Show()

F2::Run("UI.ahk")

Startfunc(*) {
    global Dependenciesinstalled
    myGui.Hide()
    if Dependenciesinstalled = 0{
    userResponse := MsgBox("There are Requirements for Running this Script:`n`n- Python3`n- Keyboard`n- Requests`n`nWould you Like to Install these Dependencies via this Script?`n(PLEASE DO NOT DO ANYTHING WHILE IT INSTALLES THE DEPENDENCIES)`n`n(If you already have them installed just go through the setup and dont insall python again)", "WARING", "4116")
    if (userResponse = "Yes"){
    Run("https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe")
    Sleep(3000)
    MsgBox("Please Run the File and Countinue with the Setup after that press OK")
    Sleep(1000)
    RunWait("cmd.exe /c pip install keyboard requests", "")
    MsgBox("Dependencies Installed, You can now use the Script")
    Dependenciesinstalled := 1
    IniWrite(Dependenciesinstalled, A_ScriptDir "\config.ini", "Main", "DependenciesInstalled")
    myGui.Show()
    return
    } else if (userResponse = "No"){
	myGui.Show()
    return
    }}
    Run(A_ScriptDir "\main.pyw")
    
    ExitApp()

}
