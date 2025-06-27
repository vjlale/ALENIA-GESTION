@echo off
REM Script para crear el ejecutable de ALENIA GESTIÓN
REM Autor: Sistema de Gestión Pilchero
REM Fecha: 2025

echo ========================================
echo    ALENIA GESTIÓN - BUILD SCRIPT
echo ========================================
echo.

echo [1/4] Verificando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo [2/4] Limpiando archivos anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [3/4] Creando ejecutable con PyInstaller...
pyinstaller --clean ALENIA_GESTION.spec
if %errorlevel% neq 0 (
    echo ERROR: Fallo al crear el ejecutable
    pause
    exit /b 1
)

echo.
echo [4/4] Copiando archivos adicionales...
copy "productos.json" "dist\" >nul 2>&1
copy "ventas.json" "dist\" >nul 2>&1
copy "ventas_historico_2025.json" "dist\" >nul 2>&1
copy "modelo_productos.csv" "dist\" >nul 2>&1
copy "*.csv" "dist\" >nul 2>&1

echo.
echo ========================================
echo          BUILD COMPLETADO!
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\ALENIA_GESTION.exe
echo.
echo Para probar el ejecutable:
echo 1. Navega a la carpeta 'dist'
echo 2. Ejecuta ALENIA_GESTION.exe
echo.
echo ========================================

pause
