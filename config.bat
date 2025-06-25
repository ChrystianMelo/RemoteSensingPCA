@echo off
echo Creating virtual environment...
py -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip and installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete!
pause