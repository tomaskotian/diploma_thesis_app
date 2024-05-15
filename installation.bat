@REM echo off
set INSTALL_PATH=%cd%\python
set PYTHON_PATH=%cd%\python\python.exe
cd %cd%

echo Downloading Python installer...
curl -o %INSTALL_PATH%\python-installer.exe https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe
echo Python installer downloaded successfully.
echo Installing Python...
%INSTALL_PATH%\python-installer.exe /uninstall  /passive 
%INSTALL_PATH%\python-installer.exe /install  /passive TargetDir=%INSTALL_PATH%

echo Venv creating...
%PYTHON_PATH% -m venv venv

echo Start venv...
call venv\Scripts\activate.bat

echo Pip instalation...
pip install -r sources\libs\requirements.txt

echo Deactive venv...
call venv\Scripts\deactivate.bat
pause