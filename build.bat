pyinstaller --noconfirm  ^
    --onedir ^
    --add-data="*.dat;." ^
    --add-data="*.png;." ^
    --name pyrl ^
    engine.py