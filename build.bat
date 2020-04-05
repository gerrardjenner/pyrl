pyinstaller --noconfirm  ^
    --onedir ^
    --add-data="*.dat;." ^
    --add-data="*.png;." ^
    --name pyrl ^
    engine.py



powershell Compress-Archive -Path dist/pyrl -DestinationPath dist/pyrl.zip -Update
