::Get active directory
SET mypath=%~dp0

::Set python path
set PYTHONPATH=%PYTHONPATH%;%mypath:~0,-1%;<constellationRender folder location>

::Call maya
::sample >> "C:\Program Files\Autodesk\Maya2013.5\bin\maya.exe"
<maya.exe location>