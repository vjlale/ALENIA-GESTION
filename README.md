# 🚀 ALENIA GESTIÓN

## Sistema Integral de Gestión de Stock y Ventas

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**ALENIA GESTIÓN** es un sistema completo de gestión de inventario y ventas desarrollado en Python con interfaz gráfica moderna. Diseñado especialmente para pequeñas y medianas empresas que necesitan un control eficiente de su stock y ventas.

## 🎯 Características Principales

### 📦 Gestión de Stock
- **Control de Inventario**: Registro completo de productos con marca, descripción, color, talle y cantidad
- **Precios Inteligentes**: Cálculo automático de precios de venta y precios amigos basados en porcentajes
- **Carga Masiva**: Importación de productos desde archivos CSV
- **Reportes Detallados**: Visualización de stock actual y productos con bajo inventario

### 💰 Sistema de Ventas
- **Carrito de Compras**: Interfaz intuitiva para agregar productos y calcular totales
- **Múltiples Precios**: Soporte para precio normal y precio amigo
- **Cálculo de IVA**: Incorporación automática de impuestos
- **Historial de Ventas**: Registro completo de todas las transacciones

### 🤖 Inteligencia Artificial
- **Sugerencias de Productos**: Recomendaciones basadas en tendencias de venta
- **Análisis de Inventario**: Identificación de productos de alta y baja rotación
- **Predicciones de Demanda**: Estimaciones de productos que necesitan reposición
- **Optimización de Precios**: Sugerencias para maximizar la rentabilidad

### 📊 Reportes y Análisis
- **Cierre de Caja**: Resumen diario de ventas y ganancias
- **Análisis Temporal**: Comparación de ventas por períodos
- **Exportación de Datos**: Generación de reportes en formato CSV
- **Dashboard Visual**: Métricas clave en tiempo real

## 🎨 Diseño Moderno

La aplicación cuenta con un diseño visual completamente renovado:

- **Paleta de Colores Moderna**: Gradientes púrpura y magenta con acentos en verde neón
- **Iconografía Actualizada**: Iconos modernos para cada función
- **Distribución Optimizada**: Interfaz responsive adaptada para resolución 1280x720
- **Experiencia de Usuario**: Navegación intuitiva y feedback visual

## 🛠️ Instalación

### Para Usuarios (Ejecutable)

1. Descarga el archivo `ALENIA_GESTION.exe` desde [Releases](https://github.com/tuusuario/ALENIA-GESTION/releases)
2. Ejecuta el archivo
3. ¡Listo! La aplicación se iniciará automáticamente

### Para Desarrolladores

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/ALENIA-GESTION.git
cd ALENIA-GESTION

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

## 🔧 Crear Ejecutable

Para generar tu propio archivo ejecutable:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear el ejecutable usando el archivo .spec
pyinstaller ALENIA_GESTION.spec

# El ejecutable se creará en la carpeta dist/
```

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **RAM**: Mínimo 4GB recomendado
- **Espacio en Disco**: 100MB para instalación
- **Resolución**: 1280x720 píxeles mínimo

## 🗂️ Estructura del Proyecto

```
ALENIA-GESTION/
├── main.py                 # Archivo principal de la aplicación
├── requirements.txt        # Dependencias de Python
├── ALENIA_GESTION.spec    # Configuración de PyInstaller
├── README.md              # Este archivo
├── .gitignore             # Archivos ignorados por Git
├── LOGO APP.png           # Logo principal
├── 7.PNG                  # Logo secundario
├── productos.json         # Base de datos de productos
├── ventas.json           # Historial de ventas
├── ventas_historico_2025.json # Archivo de respaldo
└── modelo_productos.csv   # Plantilla para carga masiva
```

## 🚀 Uso Rápido

1. **Primer Inicio**: Al abrir la aplicación, se creará automáticamente la base de datos
2. **Agregar Productos**: Usa "📦 Productos" > "➕ Alta Producto" para agregar tu inventario
3. **Realizar Ventas**: Accede a "💰 Venta" para procesar transacciones
4. **Ver Reportes**: Consulta "📊 Reportes" para análisis de tu negocio
5. **IA Inteligente**: Explora "🤖 Sugerencias IA" para optimizar tu gestión

## 🎯 Funcionalidades Avanzadas

### Carga Masiva de Productos
- Importa productos desde archivos CSV
- Formato: `marca,descripcion,color,talle,cantidad,precio_costo,porcentaje_venta,porcentaje_amigo`
- Validación automática de datos

### Centro de Inteligencia Artificial
- **Análisis de Tendencias**: Identifica patrones de venta
- **Sugerencias de Reposición**: Lista productos con bajo stock
- **Optimización de Precios**: Maximiza la rentabilidad
- **Predicción de Demanda**: Anticipa necesidades futuras

### Reportes Personalizables
- Exportación en múltiples formatos
- Filtros por fecha, producto o categoría
- Gráficos y visualizaciones
- Cálculos automáticos de rentabilidad

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tuusuario/ALENIA-GESTION/issues)
- **Documentación**: Consulta este README y los comentarios en el código
- **Email**: tucorreo@ejemplo.com

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🌟 Características Futuras

- [ ] Integración con APIs de proveedores
- [ ] Módulo de compras y proveedores
- [ ] Aplicación móvil complementaria
- [ ] Sincronización en la nube
- [ ] Módulo de facturación electrónica
- [ ] Dashboard web
- [ ] Integración con código de barras
- [ ] Múltiples sucursales

## 🎉 Agradecimientos

- Desarrollado con ❤️ para la comunidad de pequeñas empresas
- Inspirado en las necesidades reales de gestión comercial
- Interfaz moderna basada en las últimas tendencias de UX/UI

---

**ALENIA GESTIÓN** - *Gestión inteligente para el éxito de tu negocio* 🚀
