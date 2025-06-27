# 🤖 CENTRO DE INTELIGENCIA ARTIFICIAL

## Descripción General
El Centro de IA es una interfaz unificada que centraliza todas las funcionalidades de inteligencia artificial para la optimización de ventas y gestión de inventario en la aplicación Alen.iA Gestión.

## Acceso
**Menú Principal → Menú → 🤖 Sugerencias IA**

## Funcionalidades Principales

### 1. 📊 Dashboard IA
**Panel principal con métricas generales y alertas críticas**

#### Paneles de Información:
- **🚨 Alertas Críticas**: Productos con stock crítico que requieren atención inmediata
- **⭐ Productos Estrella**: Productos con alta rotación y mejores márgenes
- **📊 Métricas IA**: Estadísticas generales del inventario y tendencias

#### Tabla de Resumen Ejecutivo:
- Análisis de últimos 30 días
- Categorización por urgencia y estado
- Acciones sugeridas con prioridad
- Estados: URGENTE, EXCELENTE, EN PROCESO, EN ANÁLISIS, ATENCIÓN

### 2. 📦 Reposición IA
**Sistema inteligente de sugerencias de reposición de stock**

#### Configuración Dinámica:
- **Días de análisis**: 7, 15, 30, 60, 90 días
- **Stock mínimo**: 10%, 15%, 20%, 25%, 30%

#### Tabla de Análisis:
- **🚨 Urgencia**: Código de colores (🔴 Crítico, 🟡 Atención, 🟢 Normal)
- **Velocidad de Venta**: Unidades por día
- **Días Restantes**: Proyección de agotamiento
- **Sugerencia**: Cantidad recomendada para reponer

#### Algoritmo IA:
- Calcula velocidad de venta promedio
- Proyecta días restantes con stock actual
- Sugiere stock para 30 días de operación
- Prioriza por urgencia (sin stock, crítico, urgente, atención)

### 3. 💰 Optimización de Precios IA
**Análisis inteligente para optimización de precios y márgenes**

#### Análisis de Oportunidades:
- **Rotación vs Margen**: Identifica oportunidades de ajuste
- **Precios Sugeridos**: Recomendaciones basadas en performance
- **Razones**: Justificación de cada sugerencia

#### Lógica de Sugerencias:
- **🔻 Reducir Precio**: Baja rotación + alto margen (>40%) → Reducir 10%
- **🔺 Aumentar Precio**: Alta rotación + bajo margen (<30%) → Aumentar 10%
- **✅ Precio Óptimo**: Balance adecuado entre rotación y margen

### 4. 📈 Análisis IA
**Análisis avanzado de tendencias y comportamiento de productos**

#### Tendencias por Marca:
- Top 5 marcas por volumen de ventas
- Análisis de performance por marca
- Identificación de marcas estrella

#### Productos Sin Movimiento:
- Detecta productos sin ventas en 60 días
- Sugerencias de promociones
- Evaluación para descontinuación

#### Categorización Inteligente:
- **⭐ Estrella**: >10 ventas en 30 días
- **📈 Crecimiento**: 5-10 ventas en 30 días
- **🔄 Estable**: 1-5 ventas en 30 días
- **⚠️ Lento**: Sin ventas en 30 días

## Funciones Auxiliares

### 🔄 Actualizar
- Recalcula todos los análisis con datos actuales
- Actualiza métricas y sugerencias
- Confirmación visual de actualización

### 📄 Exportar Todo
- Genera reporte CSV completo
- Incluye todas las secciones de análisis
- Nombre automático con fecha actual
- Formato: `Centro_IA_Completo_YYYY-MM-DD.csv`

## Criterios de Análisis

### Stock Crítico:
- Productos con ≤7 días de stock restante
- Productos con ≤5 unidades en inventario

### Producto Estrella:
- ≥10 ventas en los últimos 30 días
- Alta rotación y buenos márgenes

### Velocidad de Venta:
- Promedio de unidades vendidas por día
- Base para proyecciones de stock

### Prioridades:
- **100**: Sin stock (crítico)
- **80**: ≤3 días restantes (muy urgente)
- **60**: ≤7 días restantes (urgente)
- **40**: ≤14 días restantes (atención)
- **20**: >14 días restantes (normal)

## Diseño y UX

### Colores por Función:
- **Dashboard**: Azul cian (#00BCD4)
- **Reposición**: Verde (#4CAF50)
- **Precios**: Naranja (#FF9800)
- **Análisis**: Púrpura (#9C27B0)

### Navegación:
- Botones de cambio de vista en panel superior
- Interfaz intuitiva con iconos descriptivos
- Botón "Volver" para regresar al menú

### Tablas Profesionales:
- Diseño limpio con ttk.Treeview
- Anchos de columna optimizados
- Headers centrados y descriptivos
- Limitación de filas para mejor rendimiento

## Beneficios del Sistema

1. **Centralización**: Todas las funciones IA en una sola interfaz
2. **Eficiencia**: Análisis automático sin intervención manual
3. **Precisión**: Algoritmos basados en datos reales de ventas
4. **Flexibilidad**: Configuración adaptable según necesidades
5. **Exportación**: Reportes completos para análisis externo
6. **Actualización**: Datos siempre actualizados
7. **Usabilidad**: Interfaz profesional y fácil de usar

## Tecnologías Utilizadas
- **Python + Tkinter**: Interfaz gráfica
- **ttk.Treeview**: Tablas profesionales
- **Algoritmos Propios**: Lógica de IA personalizada
- **CSV Export**: Generación de reportes
- **Análisis Temporal**: Evaluación por períodos configurables

---
*Desarrollado para Alen.iA Gestión - Sistema de Gestión de Stock y Ventas*
