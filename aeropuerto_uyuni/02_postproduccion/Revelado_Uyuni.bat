@echo off
rem Revelado de serie - Aeropuerto de Uyuni
rem Arrastra la carpeta con las fotos sobre este archivo. Abre la aplicacion en el navegador.
rem Requiere uv (https://docs.astral.sh/uv/): instala solo Python, numpy y Pillow la primera vez.
setlocal
if "%~1"=="" (
  echo.
  echo   Arrastra la carpeta con las fotos sobre este archivo .bat
  echo.
  pause
  exit /b 1
)
where uv >nul 2>nul
if errorlevel 1 (
  echo.
  echo   No encontre "uv". Instalalo desde PowerShell con:
  echo   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 ^| iex"
  echo   y vuelve a arrastrar la carpeta.
  echo.
  pause
  exit /b 1
)
uv run "%~dp0unificar_color.py" --app "%~1"
pause
