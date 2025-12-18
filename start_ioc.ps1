# Set-ExecutionPolicy -ExecutionPolicy Undefined -Scope LocalMachine

Push-Location  .\MyProject\iocBoot\iocMyProject
..\..\bin\windows-x64\MyProject.exe .\st.cmd
Pop-Location
