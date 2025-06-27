@echo off
REM Script de empaquetado para distribución de ALENIA GESTIÓN
REM Crea un paquete completo listo para distribución

echo ==========================================
echo   ALENIA GESTIÓN - PACKAGE BUILDER
echo ==========================================
echo.

REM Verificar que el ejecutable existe
if not exist "dist\ALENIA_GESTION.exe" (
    echo ERROR: El ejecutable no existe. Ejecuta primero build_exe.bat
    pause
    exit /b 1
)

echo [1/5] Creando directorio de distribución...
if exist "release" rmdir /s /q "release"
mkdir "release\ALENIA_GESTION"

echo.
echo [2/5] Copiando ejecutable principal...
copy "dist\ALENIA_GESTION.exe" "release\ALENIA_GESTION\"

echo.
echo [3/5] Copiando recursos necesarios...
copy "LOGO APP.png" "release\ALENIA_GESTION\" >nul 2>&1
copy "7.PNG" "release\ALENIA_GESTION\" >nul 2>&1
copy "productos.json" "release\ALENIA_GESTION\" >nul 2>&1
copy "ventas.json" "release\ALENIA_GESTION\" >nul 2>&1
copy "modelo_productos.csv" "release\ALENIA_GESTION\" >nul 2>&1

echo.
echo [4/5] Copiando documentación...
copy "README.md" "release\ALENIA_GESTION\" >nul 2>&1
copy "INSTALACION.md" "release\ALENIA_GESTION\" >nul 2>&1
copy "CHANGELOG.md" "release\ALENIA_GESTION\" >nul 2>&1
copy "LICENSE" "release\ALENIA_GESTION\" >nul 2>&1

echo.
echo [5/5] Creando archivo de información...
echo ALENIA GESTIÓN v1.0.0 > "release\ALENIA_GESTION\VERSION.txt"
echo Ejecutar: ALENIA_GESTION.exe >> "release\ALENIA_GESTION\VERSION.txt"
echo GitHub: https://github.com/vjlale/ALENIA-GESTION >> "release\ALENIA_GESTION\VERSION.txt"

echo.
echo ==========================================
echo      PAQUETE LISTO PARA DISTRIBUCIÓN
echo ==========================================
echo.
echo Ubicación: release\ALENIA_GESTION\
echo.
echo Contenido del paquete:
dir "release\ALENIA_GESTION\"
echo.
echo Para distribuir: Comprime la carpeta o copia directamente
echo ==========================================

pause
