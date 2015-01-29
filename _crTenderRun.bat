
SET mypath=%~dp0

cd /d %mypath:~0,-1%

set PYTHONPATH=%mypath:~0,-1%;

::Start crTender
::Check .py or .pyc existence.

"C:\Python27\Pythonw.exe" %mypath:~0,-1%\crTender.pyc
