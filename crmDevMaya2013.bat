::Get active directory
SET mypath=%~dp0

set MAYA_SCRIPT_PATH=D:\DEVELOPMENT\SOFTWARE DEVELOPMENT;

::Set python path
set PYTHONPATH=%PYTHONPATH%;C:\Program Files\Autodesk\Maya2013.5\Python\Lib\site-packages;%mypath:~0,-1%;A:\constellationRenderManager

::Call maya
"C:\Program Files\Autodesk\Maya2013\bin\maya.exe"