::Launch client service

::Get active directory
SET mypath=%~dp0

set PYTHONPATH=%mypath:~0,-1%;

::Call client service
::Change python source path when installing
"Y:\TECH\Python27\Python.exe" %mypath:~0,-1%\crClientService.py