@echo off
echo Activating virtual environment...
call venv\Scripts\activate

echo Deleting previous results...
rmdir /s /q "data\Results"
rmdir /s /q "data\PCA Components"

echo Running project...
py src\main.py
pause