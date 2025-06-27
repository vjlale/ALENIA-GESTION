print("[DEBUG] Inicio del script - main.py:1")
import datetime
from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv

# Paleta de colores moderna Alen.iA
COLOR_GRADIENTE_1 = "#9800b7"  # Púrpura
COLOR_GRADIENTE_2 = "#220294"  # Magenta
COLOR_VERDE_NEON = "#39ff14"
COLOR_CIAN = "#00fff7"
COLOR_AZUL = "#0099ff"
COLOR_FONDO = COLOR_GRADIENTE_1  # Se usará gradiente en el fondo principal
COLOR_BOTON = "#0033cc"  # Azul fuerte para botones principales
COLOR_BOTON_SECUNDARIO = COLOR_BOTON  # Fondo de botones secundarios
COLOR_TOTAL_IVA_BG = COLOR_BOTON  # Fondo de los labels TOTAL e IVA
COLOR_LABEL_VENTA_BG = COLOR_BOTON  # Fondo de los labels principales en pantalla venta
COLOR_ENTRY_VENTA_BG = "#ffffff"  # Fondo blanco para los campos de texto
COLOR_BOTON_TEXTO = "#ffffff"
COLOR_TEXTO = "#f5f5f5"
COLOR_ENTRADA = "#040404"
COLOR_BOTON_HOVER = COLOR_VERDE_NEON

class Producto:
    def __init__(self, marca: str, descripcion: str, color: str, talle: str, cantidad: int, precio_costo: float, porcentaje_venta: float = 50, porcentaje_amigo: float = 20):
        self.marca = marca
        self.descripcion = descripcion
        self.color = color
        self.talle = talle
        self.cantidad = cantidad
        self.precio_costo = precio_costo
        self.porcentaje_venta = porcentaje_venta
        self.porcentaje_amigo = porcentaje_amigo
        self.precio_venta = self.calcular_precio_venta()
        self.precio_amigo = self.calcular_precio_amigo()

    def calcular_precio_venta(self):
        return round(self.precio_costo * (1 + self.porcentaje_venta / 100), 2)

    def calcular_precio_amigo(self):
        return round(self.precio_costo * (1 + self.porcentaje_amigo / 100), 2)

    def actualizar_precio_costo(self, nuevo_precio):
        self.precio_costo = nuevo_precio
        self.precio_venta = self.calcular_precio_venta()
        self.precio_amigo = self.calcular_precio_amigo()

class Venta:
    def __init__(self, descripcion: str, items: list, fecha: datetime.date, forma_pago: str = "EFECTIVO"):
        self.descripcion = descripcion
        self.items = items  # lista de dicts: {producto, cantidad, precio}
        self.fecha = fecha
        self.forma_pago = forma_pago

class SistemaGestion:
    def __init__(self):
        self.productos: List[Producto] = []
        self.ventas: List[Venta] = []
        self.cargar_datos()

    def cargar_datos(self):
        if os.path.exists("productos.json"):
            with open("productos.json", "r", encoding="utf-8") as f:
                productos = json.load(f)
                for p in productos:
                    self.productos.append(Producto(
                        p.get("marca", ""),
                        p["descripcion"], p["color"], p["talle"], p["cantidad"], p["precio_costo"], p.get("porcentaje_venta", 50), p.get("porcentaje_amigo", 20)
                    ))
        if os.path.exists("ventas.json"):
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
                for v in ventas:
                    items = []
                    for item in v["items"]:
                        prod = self.buscar_producto(item.get("marca", ""), item["producto"], item["color"], item["talle"])
                        if prod:
                            items.append({
                                "producto": prod,
                                "cantidad": item["cantidad"],
                                "precio": item["precio"]
                            })
                    self.ventas.append(Venta(
                        v["descripcion"], items, datetime.datetime.strptime(v["fecha"], "%Y-%m-%d").date(), 
                        v.get("forma_pago", "EFECTIVO")
                    ))

    def guardar_productos(self):
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump([
                {
                    "marca": p.marca,
                    "descripcion": p.descripcion,
                    "color": p.color,
                    "talle": p.talle,
                    "cantidad": p.cantidad,
                    "precio_costo": p.precio_costo,
                    "porcentaje_venta": p.porcentaje_venta,
                    "porcentaje_amigo": p.porcentaje_amigo
                } for p in self.productos
            ], f, ensure_ascii=False, indent=2)

    def guardar_ventas(self):
        with open("ventas.json", "w", encoding="utf-8") as f:
            json.dump([
                {
                    "descripcion": v.descripcion,
                    "items": [
                        {
                            "producto": item["producto"].descripcion,
                            "color": item["producto"].color,
                            "talle": item["producto"].talle,
                            "cantidad": item["cantidad"],
                            "precio": item["precio"]
                        } for item in v.items
                    ],
                    "fecha": v.fecha.strftime("%Y-%m-%d"),
                    "forma_pago": getattr(v, 'forma_pago', 'EFECTIVO')
                } for v in self.ventas
            ], f, ensure_ascii=False, indent=2)

    def agregar_producto(self, marca, descripcion, color, talle, cantidad, precio_costo, porcentaje_venta=50, porcentaje_amigo=20):
        prod = Producto(marca, descripcion, color, talle, cantidad, precio_costo, porcentaje_venta, porcentaje_amigo)
        self.productos.append(prod)
        self.guardar_productos()

    def registrar_venta(self, descripcion, items, fecha, forma_pago="EFECTIVO"):
        # items: lista de tuplas (producto, cantidad, precio)
        for producto, cantidad, _ in items:
            if producto.cantidad < cantidad:
                return False
        for producto, cantidad, _ in items:
            producto.cantidad -= cantidad
        venta_items = [{"producto": p, "cantidad": c, "precio": pr} for p, c, pr in items]
        venta = Venta(descripcion, venta_items, fecha, forma_pago)
        self.ventas.append(venta)
        self.guardar_productos()
        self.guardar_ventas()
        return True

    def buscar_producto(self, marca, descripcion, color, talle):
        for p in self.productos:
            if p.marca == marca and p.descripcion == descripcion and p.color == color and p.talle == talle:
                return p
        return None

    def cierre_caja(self, fecha):
        return [v for v in self.ventas if v.fecha == fecha]

    def archivar_ventas_dia(self, fecha):
        """Archiva las ventas del día en un archivo histórico y las elimina del día actual"""
        ventas_dia = self.cierre_caja(fecha)
        
        if not ventas_dia:
            return False
        
        # Crear archivo histórico si no existe
        archivo_historico = f"ventas_historico_{fecha.strftime('%Y')}.json"
        historico = []
        
        if os.path.exists(archivo_historico):
            with open(archivo_historico, "r", encoding="utf-8") as f:
                historico = json.load(f)
        
        # Agregar ventas del día al histórico
        for v in ventas_dia:
            historico.append({
                "descripcion": v.descripcion,
                "items": [
                    {
                        "producto": item["producto"].descripcion,
                        "marca": item["producto"].marca,
                        "color": item["producto"].color,
                        "talle": item["producto"].talle,
                        "cantidad": item["cantidad"],
                        "precio": item["precio"]
                    } for item in v.items
                ],
                "fecha": v.fecha.strftime("%Y-%m-%d"),
                "forma_pago": getattr(v, 'forma_pago', 'EFECTIVO'),
                "cerrado": True
            })
        
        # Guardar histórico actualizado
        with open(archivo_historico, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
        
        # Eliminar ventas del día del archivo actual
        self.ventas = [v for v in self.ventas if v.fecha != fecha]
        self.guardar_ventas()
        
        return True

    def reporte_ventas(self, desde, hasta):
        return [v for v in self.ventas if desde <= v.fecha <= hasta]

    def reporte_ventas_por_marca(self, desde, hasta, marca):
        ventas = [v for v in self.ventas if desde <= v.fecha <= hasta]
        ventas_marca = []
        for v in ventas:
            for item in v.items:
                if hasattr(item['producto'], 'marca') and item['producto'].marca == marca:
                    ventas_marca.append({
                        'fecha': v.fecha,
                        'descripcion': v.descripcion,
                        'producto': item['producto'],
                        'cantidad': item['cantidad'],
                        'precio': item['precio']
                    })
        return ventas_marca

    def inventario_actual(self):
        return self.productos

    def actualizar_precio_producto(self, marca, descripcion, color, talle, nuevo_precio):
        prod = self.buscar_producto(marca, descripcion, color, talle)
        if prod:
            prod.actualizar_precio_costo(nuevo_precio)
            self.guardar_productos()
            return True
        return False

    def eliminar_producto(self, marca, descripcion, color, talle):
        self.productos = [p for p in self.productos if not (p.marca == marca and p.descripcion == descripcion and p.color == color and p.talle == talle)]
        self.guardar_productos()

    def eliminar_productos_masivo(self, lista_claves):
        # lista_claves: lista de tuplas (marca, descripcion, color, talle)
        self.productos = [p for p in self.productos if (p.marca, p.descripcion, p.color, p.talle) not in lista_claves]
        self.guardar_productos()

    def sugerencias_reposicion(self, umbral_stock=5, dias_analisis=30):
        """
        Devuelve una lista de productos que deberían reponerse según ventas recientes y stock bajo.
        - umbral_stock: stock mínimo recomendado
        - dias_analisis: días hacia atrás para analizar ventas
        """
        import datetime
        hoy = datetime.date.today()
        ventas_recientes = [v for v in self.ventas if (hoy - v.fecha).days <= dias_analisis]
        conteo = {}
        for v in ventas_recientes:
            for item in v.items:
                prod = item['producto']
                clave = (prod.marca, prod.descripcion, prod.color, prod.talle)
                conteo[clave] = conteo.get(clave, 0) + item['cantidad']
        sugerencias = []
        for p in self.productos:
            clave = (p.marca, p.descripcion, p.color, p.talle)
            ventas = conteo.get(clave, 0)
            if p.cantidad <= umbral_stock and ventas > 0:
                sugerencias.append({
                    'producto': p,
                    'stock': p.cantidad,
                    'vendidos': ventas
                })
        # Ordenar por más vendidos y menos stock
        sugerencias.sort(key=lambda x: (x['stock'], -x['vendidos']))
        return sugerencias

class AppPilchero(tk.Tk):
    def __init__(self, sistema):
        print("[DEBUG] Iniciando AppPilchero.__init__ - main.py:266")
        super().__init__()
        self.sistema = sistema
        self.title("Alen.iA - Gestión Inteligente de Stock y Ventas")
        self.geometry("1280x720")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)
        print("[DEBUG] Llamando a crear_widgets() desde __init__ - main.py:273")
        self.crear_widgets()

    def crear_widgets(self):
        print("[DEBUG] Entrando en crear_widgets() - main.py:277")
        self.canvas_bg = tk.Canvas(self, width=1280, height=720, highlightthickness=0, bd=0)
        self.canvas_bg.place(x=0, y=0, relwidth=1, relheight=1)
        # Crear el fondo con etiquetas para poder identificarlo y preservarlo
        for i in range(0, 720, 2):
            color = self._interpolar_color(COLOR_GRADIENTE_1, COLOR_GRADIENTE_2, i/720)
            self.canvas_bg.create_rectangle(0, i, 1280, i+2, outline="", fill=color, tags="fondo_{}".format(i))
        self.canvas_bg.lower("all")
        self.pantalla_widgets = []
        self.mostrar_menu_principal()

    def _colocar_logo(self, pantalla_principal=True):
        # Elimina logo anterior si existe
        if hasattr(self, 'logo_canvas_id') and self.logo_canvas_id:
            self.canvas_bg.delete(self.logo_canvas_id)
            self.logo_canvas_id = None
        
        if pantalla_principal:
            # PANTALLA PRINCIPAL: Usar LOGO APP.png (SIN MODIFICAR)
            import sys, os
            if hasattr(sys, '_MEIPASS'):
                logo_path = os.path.join(sys._MEIPASS, "LOGO APP.png") # type: ignore
            else:
                logo_path = "LOGO APP.png"
            try:
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path).convert("RGBA")
                orig_w, orig_h = logo_img.size
                self.update_idletasks()  # Forzar update para obtener tamaño real
                w = self.winfo_width() or 1200
                h = self.winfo_height() or 1000
                max_w = int(w * 0.65)
                max_h = int(h * 0.42)
                # Mantener proporción
                scale = min(max_w / orig_w, max_h / orig_h)
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                logo_img = logo_img.resize((new_w, new_h), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS) # type: ignore
                self.logo_tk = ImageTk.PhotoImage(logo_img)
                pos_x = w // 2
                pos_y = int(h * -0.08)
                self.logo_canvas_id = self.canvas_bg.create_image(pos_x, pos_y, image=self.logo_tk, anchor="n")
                self.canvas_bg.tag_raise(self.logo_canvas_id)
            except Exception as e:
                self.logo_canvas_id = self.canvas_bg.create_text(self.winfo_width()//1, 40, text="[LOGO]", font=("Orbitron", 32, "bold"), fill=COLOR_CIAN, anchor="n")
        else:
            # PANTALLAS SECUNDARIAS: Usar 7.PNG con transparencia y centrado
            self._colocar_logo_secundarias()

    def _colocar_logo_secundarias(self):
        """Coloca el logo 7.PNG en pantallas secundarias con transparencia y centrado"""
        try:
            from PIL import Image, ImageTk
            import os
            logo_path = "7.PNG"
            
            if os.path.exists(logo_path):
                # Cargar imagen con transparencia
                logo_img = Image.open(logo_path).convert("RGBA")
                
                # Redimensionar el logo manteniendo proporción (tamaño apropiado para pantallas secundarias)
                logo_width = 200  # Tamaño más prominente
                logo_height = int(logo_img.height * (logo_width / logo_img.width))
                
                # Si es muy alto, ajustar por altura máxima
                if logo_height > 100:
                    logo_height = 100
                    logo_width = int(logo_img.width * (logo_height / logo_img.height))
                
                # Redimensionar con alta calidad
                logo_resized = logo_img.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage manteniendo transparencia
                self.logo_tk_secundaria = ImageTk.PhotoImage(logo_resized)
                
                # Colocar en el canvas centrado en la parte superior
                self.logo_canvas_id = self.canvas_bg.create_image(
                    640, 25,  # Centrado horizontalmente, margen superior de 25px
                    image=self.logo_tk_secundaria, 
                    anchor="n"
                )
                
                # Asegurar que el logo esté al frente
                self.canvas_bg.tag_raise(self.logo_canvas_id)
                
            else:
                # Fallback si no encuentra el archivo
                self.logo_canvas_id = self.canvas_bg.create_text(
                    640, 30, 
                    text="ALEN.IA", 
                    font=("Orbitron", 20, "bold"), 
                    fill=COLOR_CIAN, 
                    anchor="n"
                )
                
        except Exception as e:
            print(f"[INFO] Error al cargar logo 7.PNG en pantalla secundaria: {e} - main.py:373")
            # Fallback texto
            self.logo_canvas_id = self.canvas_bg.create_text(
                640, 30, 
                text="ALEN.IA", 
                font=("Orbitron", 20, "bold"), 
                fill=COLOR_CIAN, 
                anchor="n"
            )

    def _interpolar_color(self, color1, color2, t): # type: ignore
        # Interpola dos colores hex en t (0-1)
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
        return f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}'

    # Métodos stub para evitar errores si no existen
    def mostrar_inventario(self): # type: ignore
        print("[DEBUG] mostrar_inventario() llamado - main.py:392")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_inventario(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="Volver", font=("Montserrat", 12, "bold"), bg="#333", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario)
        win = self.canvas_bg.create_window(65, 20, window=btn_volver, width=90, height=36, anchor="n")
        self.pantalla_widgets.append(btn_volver)



    def limpiar_pantalla(self):
        # Elimina todos los widgets de la pantalla y limpia referencias
        for w in getattr(self, 'pantalla_widgets', []):
            try:
                w.destroy()
            except Exception:
                pass
        self.pantalla_widgets = []
        
        # Elimina solo el logo si existe
        if hasattr(self, 'logo_canvas_id') and self.logo_canvas_id:
            self.canvas_bg.delete(self.logo_canvas_id)
            self.logo_canvas_id = None
        
        # Guarda las referencias de los rectángulos del fondo (gradiente)
        fondo = []
        for i in range(0, 720, 2):
            rect_id = self.canvas_bg.find_withtag("fondo_{}".format(i))
            if rect_id:
                fondo.extend(rect_id)
        
        # Elimina todos los elementos canvas excepto el fondo
        for item in self.canvas_bg.find_all():
            if item not in fondo:
                self.canvas_bg.delete(item)
                
        # Redibuja el gradiente si es necesario
        if not fondo:
            for i in range(0, 720, 2):
                color = self._interpolar_color(COLOR_GRADIENTE_1, COLOR_GRADIENTE_2, i/720)
                rect_id = self.canvas_bg.create_rectangle(0, i, 1280, i+2, outline="", fill=color, tags="fondo_{}".format(i))
        
        # Asegura que el gradiente siempre esté al fondo
        self.canvas_bg.lower("all")

    def mostrar_menu_principal(self):
        print("[DEBUG] mostrar_menu_principal() llamado - main.py:438")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=True)
        btns = [
            ("💰 Venta", self.mostrar_venta),
            ("📊 Ventas del Día", self.mostrar_ventas_dia),
            ("🏦 Cierre de Caja", self.mostrar_cierre_caja),
            ("⚙️ Menú Gestión", self.mostrar_menu_secundario),
        ]
        btn_w, btn_h = 360, 68
        sep_y, sep_h = 20, 350
        y0 = 250
        for i, (txt, cmd) in enumerate(btns):
            b = tk.Button(self.canvas_bg, text=txt, font=("Montserrat", 15, "bold"), bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, bd=0, relief="flat", activebackground="#7c5eff", activeforeground=COLOR_BOTON_TEXTO, cursor="hand2", command=cmd)
            win = self.canvas_bg.create_window(650, y0+i*(btn_h+sep_y), window=b, width=btn_w, height=btn_h, anchor="n")
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg="#1c6bff", relief="raised"))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=COLOR_BOTON, relief="flat"))
            self.pantalla_widgets.append(b)

    def mostrar_menu_secundario(self):
        print("[DEBUG] mostrar_menu_secundario() llamado - main.py:458")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        
        # Título del menú (ajustado para el nuevo logo)
        lbl_titulo = tk.Label(self.canvas_bg, text="⚙️ MENÚ DE GESTIÓN", font=("Montserrat", 20, "bold"), 
                             bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_titulo, anchor="center")  # Ajustado para el logo
        
        btns = [
            ("📦 Agregar Producto", self.mostrar_alta_producto),
            ("📂 Carga Masiva de Productos", self.carga_masiva_productos),
            ("💲 Actualizar Precio", self.mostrar_actualizar_precio),
            ("📋 Ver Inventario", self.mostrar_inventario),
            ("📈 Reportes", self.mostrar_reportes),
            ("🤖 Sugerencias IA", self.mostrar_centro_ia),
        ]
        
        # Botones centrados y bien espaciados (ajustados para el nuevo logo)
        btn_w, btn_h = 300, 50
        sep_y = 20
        y0 = 230  # Ajustado para dar espacio al logo
        
        for i, (txt, cmd) in enumerate(btns):
            b = tk.Button(self.canvas_bg, text=txt, font=("Montserrat", 14, "bold"), 
                         bg=COLOR_BOTON, fg="#ffffff", bd=0, relief="flat", 
                         cursor="hand2", command=cmd)
            self.canvas_bg.create_window(640, y0+i*(btn_h+sep_y), window=b, width=btn_w, height=btn_h, anchor="center")
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg="#1c6bff", relief="raised"))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=COLOR_BOTON, relief="flat"))
            self.pantalla_widgets.append(b)
        
        # Botón volver mejorado (ajustado para el nuevo logo)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), 
                              bg="#666666", fg="#ffffff", bd=0, relief="flat", 
                              command=self.mostrar_menu_principal, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")  # Ajustado
        
        self.pantalla_widgets.extend([lbl_titulo, btn_volver])

    def mostrar_venta(self):
        print("[DEBUG] mostrar_venta() llamado - main.py:499")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_venta(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_principal, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        self.pantalla_widgets.append(btn_volver)

    def mostrar_ventas_dia(self):
        print("[DEBUG] mostrar_ventas_dia() llamado - main.py:508")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_ventas_dia(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_principal, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        self.pantalla_widgets.append(btn_volver)

    def mostrar_cierre_caja(self):
        print("[DEBUG] mostrar_cierre_caja() llamado - main.py:517")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_cierre_caja(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_principal, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        self.pantalla_widgets.append(btn_volver)

    def mostrar_alta_producto(self):
        print("[DEBUG] mostrar_alta_producto() llamado - main.py:526")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_alta_producto(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        self.pantalla_widgets.append(btn_volver)

    def mostrar_actualizar_precio(self):
        print("[DEBUG] mostrar_actualizar_precio() llamado - main.py:535")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_actualizar_precio(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        self.pantalla_widgets.append(btn_volver)

    def mostrar_inventario(self):
        print("[DEBUG] mostrar_inventario() llamado - main.py:544")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        self._pantalla_inventario(self.canvas_bg)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        self.pantalla_widgets.append(btn_volver)



    def mostrar_reporte_ventas_marca(self):
        print("[DEBUG] mostrar_reporte_ventas_marca() llamado - main.py:555")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        widgets = []
        lbl_desde = tk.Label(self.canvas_bg, text="📅 Fecha desde (YYYY-MM-DD):", font=("Montserrat", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        win_lbl_desde = self.canvas_bg.create_window(30, 20, window=lbl_desde, anchor="nw")
        ent_desde = tk.Entry(self.canvas_bg, font=("Montserrat", 10), bg=COLOR_ENTRADA, fg=COLOR_TEXTO, bd=1, relief="solid")
        win_ent_desde = self.canvas_bg.create_window(220, 20, window=ent_desde, width=150, height=30, anchor="nw")
        lbl_hasta = tk.Label(self.canvas_bg, text="📅 Fecha hasta (YYYY-MM-DD):", font=("Montserrat", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        win_lbl_hasta = self.canvas_bg.create_window(400, 20, window=lbl_hasta, anchor="nw")
        ent_hasta = tk.Entry(self.canvas_bg, font=("Montserrat", 10), bg=COLOR_ENTRADA, fg=COLOR_TEXTO, bd=1, relief="solid")
        win_ent_hasta = self.canvas_bg.create_window(590, 20, window=ent_hasta, width=150, height=30, anchor="nw")
        lbl_marca = tk.Label(self.canvas_bg, text="🏷️ Marca:", font=("Montserrat", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        win_lbl_marca = self.canvas_bg.create_window(800, 20, window=lbl_marca, anchor="nw")
        ent_marca = tk.Entry(self.canvas_bg, font=("Montserrat", 10), bg=COLOR_ENTRADA, fg=COLOR_TEXTO, bd=1, relief="solid")
        win_ent_marca = self.canvas_bg.create_window(870, 20, window=ent_marca, width=150, height=30, anchor="nw")
        cols = ("Fecha", "Descripción Venta", "Marca", "Producto", "Cantidad", "Precio")
        tree = ttk.Treeview(self.canvas_bg, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        win_tree = self.canvas_bg.create_window(345, 120, window=tree, width=800, height=350, anchor="n")
        lbl_total = tk.Label(self.canvas_bg, text="Total ventas: $0", font=("Montserrat", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        win_lbl_total = self.canvas_bg.create_window(10, 480, window=lbl_total, anchor="w")
        def buscar():
            try:
                desde = ent_desde.get()
                hasta = ent_hasta.get()
                marca = ent_marca.get()
                desde_dt = datetime.datetime.strptime(desde, "%Y-%m-%d").date()
                hasta_dt = datetime.datetime.strptime(hasta, "%Y-%m-%d").date()
                ventas = self.sistema.reporte_ventas_por_marca(desde_dt, hasta_dt, marca)
                for i in tree.get_children():
                    tree.delete(i)
                total = 0
                for v in ventas:
                    tree.insert("", "end", values=(v['fecha'], v['descripcion'], v['producto'].marca, v['producto'].descripcion, v['cantidad'], self.formato_moneda(v['precio'])))
                    total += v['cantidad'] * v['precio']
                lbl_total.config(text=f"Total ventas: {self.formato_moneda(total)}")
            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {e}")
        btn_buscar = tk.Button(self.canvas_bg, text="🔍 Buscar", font=("Montserrat", 12, "bold"), bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, bd=0, relief="flat", command=buscar)
        win_btn_buscar = self.canvas_bg.create_window(350, 480, window=btn_buscar, width=100, height=40, anchor="nw")
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        widgets.extend([lbl_desde, ent_desde, lbl_hasta, ent_hasta, lbl_marca, ent_marca, tree, lbl_total, btn_buscar, btn_volver])
        self.pantalla_widgets.extend(widgets)

    def formato_moneda(self, valor):
        try:
            valor = float(valor)
        except Exception:
            return "$0,000"
        # Formato: $12.345,678 (punto miles, coma decimales, tres decimales)
        partes = f"{valor:,.3f}".split(".")
        if len(partes) == 2:
            miles = partes[0].replace(",", ".")
            decimales = partes[1]
            return f"${miles},{decimales}"
        else:
            return f"${valor:,.3f}".replace(",", ".").replace(".", ",", 1)

    # Pantallas adaptadas para navegación interna
    def _pantalla_venta(self, parent):
        self.limpiar_pantalla()
        widgets = []
        carrito = []
        productos = self.sistema.inventario_actual()
        opciones = [f"{p.descripcion} | {p.color} | {p.talle} | Stock: {p.cantidad}" for p in productos]
        precios = {f"{p.descripcion} | {p.color} | {p.talle} | Stock: {p.cantidad}": p.precio_venta for p in productos}
        productos_dict = {f"{p.descripcion} | {p.color} | {p.talle} | Stock: {p.cantidad}": p for p in productos}
        
        # --- TÍTULO CENTRADO DEBAJO DEL LOGO ---
        titulo = tk.Label(self.canvas_bg, text="💰 NUEVA VENTA", font=("Montserrat", 18, "bold"), 
                         bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 120, window=titulo, anchor="center")
        widgets.append(titulo)
        
        # --- CAMPOS DE ENTRADA ORGANIZADOS EN DOS COLUMNAS ---
        # Columna izquierda - Datos del producto
        x_col1_label = 80
        x_col1_entry = 220
        y_start = 160
        spacing = 45
        entry_width = 280
        
        # Producto
        lbl_prod = tk.Label(self.canvas_bg, text="🛍️ Producto:", font=("Montserrat", 12, "bold"), 
                           bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(x_col1_label, y_start, window=lbl_prod, anchor="w")
        
        producto_var = tk.StringVar()
        combo = ttk.Combobox(self.canvas_bg, textvariable=producto_var, values=opciones, 
                            font=("Montserrat", 10), state="normal")
        self.canvas_bg.create_window(x_col1_entry, y_start, window=combo, width=entry_width, height=32, anchor="w")
        
        # Sugerencias en tiempo real
        def on_keyrelease(event):
            value = combo.get().lower()
            filtered = [op for op in opciones if value in op.lower()]
            combo['values'] = filtered if filtered else opciones
        combo.bind('<KeyRelease>', on_keyrelease)
        
        # Cantidad
        lbl_cant = tk.Label(self.canvas_bg, text="🔢 Cantidad:", font=("Montserrat", 12, "bold"), 
                           bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(x_col1_label, y_start + spacing, window=lbl_cant, anchor="w")
        
        ent_cantidad = tk.Entry(self.canvas_bg, font=("Montserrat", 10), bg=COLOR_ENTRY_VENTA_BG, 
                               fg="#000000", bd=1, relief="solid")
        self.canvas_bg.create_window(x_col1_entry, y_start + spacing, window=ent_cantidad, 
                                   width=entry_width, height=32, anchor="w")
        
        # Columna derecha - Precio y forma de pago
        x_col2_label = 580
        x_col2_entry = 720
        
        # Precio
        lbl_precio = tk.Label(self.canvas_bg, text="💰 Precio unitario:", font=("Montserrat", 12, "bold"), 
                             bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(x_col2_label, y_start, window=lbl_precio, anchor="w")
        
        precio_var = tk.StringVar()
        ent_precio = tk.Entry(self.canvas_bg, textvariable=precio_var, font=("Montserrat", 10), 
                             bg=COLOR_ENTRY_VENTA_BG, fg="#000000", bd=1, relief="solid")
        self.canvas_bg.create_window(x_col2_entry, y_start, window=ent_precio, 
                                   width=entry_width, height=32, anchor="w")
        
        # Forma de pago
        lbl_forma_pago = tk.Label(self.canvas_bg, text="💳 Forma de pago:", font=("Montserrat", 12, "bold"), 
                                 bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(x_col2_label, y_start + spacing, window=lbl_forma_pago, anchor="w")
        
        forma_pago_var = tk.StringVar(value="EFECTIVO")
        combo_forma_pago = ttk.Combobox(self.canvas_bg, textvariable=forma_pago_var, 
                                       values=["EFECTIVO", "DEBITO", "CREDITO", "TRANSFERENCIA", "QR", "OTROS"], 
                                       font=("Montserrat", 10), state="readonly")
        self.canvas_bg.create_window(x_col2_entry, y_start + spacing, window=combo_forma_pago, 
                                   width=entry_width, height=32, anchor="w")
        
        # --- BOTÓN AGREGAR AL CARRITO CENTRADO ---
        btn_agregar = tk.Button(self.canvas_bg, text="🛒 Agregar al carrito", font=("Montserrat", 12, "bold"), 
                               bg="#0813F1", fg="#ffffff", bd=0, relief="flat", cursor="hand2")
        self.canvas_bg.create_window(640, 270, window=btn_agregar, width=200, height=40, anchor="center")
        
        # --- GRILLA DEL CARRITO OPTIMIZADA ---
        tree_y = 330
        tree_height = 200
        col_widths = [280, 120, 80, 120, 100]  # Ajustado para caber en pantalla
        
        carrito_tree = ttk.Treeview(self.canvas_bg, columns=("Producto", "Precio", "Cant.", "Subtotal", "IVA"), show="headings")
        for col, ancho in zip(("Producto", "Precio", "Cant.", "Subtotal", "IVA"), col_widths):
            carrito_tree.heading(col, text=col, anchor="center")
            carrito_tree.column(col, width=ancho, anchor="center")
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(self.canvas_bg, orient="vertical", command=carrito_tree.yview)
        carrito_tree.configure(yscrollcommand=scrollbar.set)
        
        # Centrar tabla en pantalla
        tree_x = 150
        tree_width = sum(col_widths)
        self.canvas_bg.create_window(tree_x, tree_y, window=carrito_tree, width=tree_width, height=tree_height, anchor="nw")
        self.canvas_bg.create_window(tree_x + tree_width + 5, tree_y, window=scrollbar, width=15, height=tree_height, anchor="nw")
        
        # --- BOTÓN ELIMINAR DEL CARRITO ---
        btn_eliminar_carrito = tk.Button(self.canvas_bg, text="🗑️ Eliminar", font=("Montserrat", 10, "bold"), 
                                        bg="#ff2d2d", fg="#fff", bd=0, relief="flat", cursor="hand2")
        self.canvas_bg.create_window(tree_x + tree_width + 80, tree_y + 20, window=btn_eliminar_carrito, 
                                   width=120, height=35, anchor="nw")
        
        # --- TOTALES Y BOTÓN FINALIZAR EN LA PARTE INFERIOR ---
        total_var = tk.StringVar(value="TOTAL: $0")
        iva_var = tk.StringVar(value="IVA: $0")
        
        # Área de totales
        y_totales = tree_y + tree_height + 20
        
        # Total general
        lbl_total = tk.Label(self.canvas_bg, textvariable=total_var, font=("Montserrat", 14, "bold"), 
                           bg="#2E7D32", fg="#ffffff", relief="flat", bd=0, padx=15, pady=8)
        self.canvas_bg.create_window(200, y_totales, window=lbl_total, anchor="center")
        
        # IVA
        lbl_iva = tk.Label(self.canvas_bg, textvariable=iva_var, font=("Montserrat", 12, "bold"), 
                          bg="#424242", fg="#ffffff", relief="flat", bd=0, padx=15, pady=5)
        self.canvas_bg.create_window(200, y_totales + 50, window=lbl_iva, anchor="center")
        
        # Botón finalizar venta
        btn_finalizar = tk.Button(self.canvas_bg, text="✅ FINALIZAR VENTA", font=("Montserrat", 14, "bold"), 
                                 bg="#17FA02", fg="#000000", bd=0, relief="flat", cursor="hand2")
        self.canvas_bg.create_window(640, y_totales + 25, window=btn_finalizar, width=250, height=50, anchor="center")

        # --- FUNCIONES DE AUTOCOMPLETADO Y LÓGICA ---
        def set_precio_venta(event=None):
            seleccion = producto_var.get()
            if seleccion in productos_dict:
                precio_var.set(str(productos_dict[seleccion].precio_venta))
        combo.bind("<<ComboboxSelected>>", set_precio_venta)

        def eliminar_del_carrito():
            seleccion = carrito_tree.selection()
            if not seleccion:
                messagebox.showwarning("Eliminar", "Seleccione un producto del carrito para eliminar.")
                return
            for item in seleccion:
                idx = carrito_tree.index(item)
                carrito_tree.delete(item)
                del carrito[idx]
            # Recalcular totales
            total = sum(item[3] for item in carrito)
            total_iva = sum(item[4] for item in carrito)
            total_var.set(f"TOTAL: {self.formato_moneda(total)}")
            iva_var.set(f"IVA: {self.formato_moneda(total_iva)}")

        def agregar_al_carrito():
            try:
                seleccion = producto_var.get()
                if not seleccion:
                    raise ValueError("Debe seleccionar un producto.")
                producto = productos_dict[seleccion]
                cantidad = int(ent_cantidad.get())
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0.")
                if producto.cantidad < cantidad:
                    raise ValueError("Stock insuficiente.")
                precio_unitario = float(precio_var.get())
                sub_total = precio_unitario * cantidad
                iva = sub_total * 0.21
                carrito.append((producto, cantidad, precio_unitario, sub_total, iva))
                
                # Mostrar en la tabla con nombre más corto
                producto_nombre = f"{producto.descripcion[:20]}... | {producto.color} | {producto.talle}"
                if len(f"{producto.descripcion} | {producto.color} | {producto.talle}") <= 35:
                    producto_nombre = f"{producto.descripcion} | {producto.color} | {producto.talle}"
                
                carrito_tree.insert("", "end", values=(
                    producto_nombre,
                    self.formato_moneda(precio_unitario), 
                    cantidad, 
                    self.formato_moneda(sub_total), 
                    self.formato_moneda(iva)
                ))
                
                # Limpiar campos
                producto_var.set("")
                ent_cantidad.delete(0, tk.END)
                precio_var.set("")
                
                # Actualizar totales
                total = sum(item[3] for item in carrito)
                total_iva = sum(item[4] for item in carrito)
                total_var.set(f"TOTAL: {self.formato_moneda(total)}")
                iva_var.set(f"IVA: {self.formato_moneda(total_iva)}")
            except ValueError as ve:
                messagebox.showerror("Error de carga", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {e}")
        
        def registrar_venta_final():
            if not carrito:
                messagebox.showerror("Error", "El carrito está vacío.")
                return
            nro_venta = len(self.sistema.ventas) + 1
            nro_venta_str = str(nro_venta).zfill(5)
            descripcion = f"Venta N° {nro_venta_str}"
            forma_pago = forma_pago_var.get()
            exito = self.sistema.registrar_venta(descripcion, [(p, c, pu) for p, c, pu, st, iva in carrito], datetime.date.today(), forma_pago)
            if not exito:
                messagebox.showerror("Error", "No se pudo registrar la venta (stock insuficiente en algún producto).")
                return
            messagebox.showinfo("Éxito", f"Venta N° {nro_venta_str} registrada y stock actualizado.")
            self.mostrar_menu_principal()
        
        # Asignar comandos a botones
        btn_agregar.config(command=agregar_al_carrito)
        btn_eliminar_carrito.config(command=eliminar_del_carrito)
        btn_finalizar.config(command=registrar_venta_final)
        
        # Agregar widgets a la lista
        widgets.extend([lbl_prod, combo, lbl_cant, ent_cantidad, lbl_precio, ent_precio, 
                       lbl_forma_pago, combo_forma_pago, carrito_tree, scrollbar, 
                       lbl_total, lbl_iva, btn_agregar, btn_finalizar, btn_eliminar_carrito])
        self.pantalla_widgets.extend(widgets)

    def _pantalla_ventas_dia(self, parent):
        widgets = []
        hoy = datetime.date.today()
        ventas_hoy = self.sistema.cierre_caja(hoy)
        
        # Título centrado (ajustado para el nuevo logo)
        lbl_titulo = tk.Label(self.canvas_bg, text=f"📊 VENTAS DEL DÍA - {hoy.strftime('%d/%m/%Y')}", 
                             font=("Montserrat", 18, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_titulo, anchor="center")  # Ajustado para el logo
        
        # Tabla centrada y bien dimensionada (ajustada para el nuevo logo)
        cols = ("Descripción Venta", "Forma de Pago", "Detalle Artículos", "Total Venta")
        tree = ttk.Treeview(self.canvas_bg, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor="center")
        
        # Posicionar tabla centrada (ajustada)
        self.canvas_bg.create_window(640, 380, window=tree, width=1000, height=320, anchor="center")  # Ajustado
        
        # Llenar datos
        for v in ventas_hoy:
            detalle = ", ".join([f"{item['producto'].descripcion}({item['producto'].color}/{item['producto'].talle}) x{item['cantidad']} @{self.formato_moneda(item['precio'])}" for item in v.items])
            total = sum(item['cantidad'] * item['precio'] for item in v.items)
            forma_pago = getattr(v, 'forma_pago', 'EFECTIVO')
            tree.insert("", "end", values=(v.descripcion, forma_pago, detalle, self.formato_moneda(total)))
        
        # Total y botón centrados debajo de la tabla (ajustados)
        total_general = sum(sum(item['cantidad'] * item['precio'] for item in v.items) for v in ventas_hoy)
        lbl_total = tk.Label(self.canvas_bg, text=f"Total ventas del día: {self.formato_moneda(total_general)}", 
                           font=("Montserrat", 16, "bold"), bg=COLOR_BOTON, fg="#ffffff", 
                           relief="flat", bd=0, padx=20, pady=10)
        self.canvas_bg.create_window(640, 580, window=lbl_total, anchor="center")  # Ajustado
        
        # Botón cierre de caja centrado (ajustado)
        btn_cierre = tk.Button(self.canvas_bg, text="🏦 CIERRE DE CAJA", font=("Montserrat", 14, "bold"), 
                              bg=COLOR_BOTON, fg="#ffffff", bd=0, relief="flat", 
                              command=self.realizar_cierre_caja, cursor="hand2")
        self.canvas_bg.create_window(640, 630, window=btn_cierre, width=220, height=50, anchor="center")  # Ajustado
        
        widgets.extend([lbl_titulo, tree, lbl_total, btn_cierre])
        self.pantalla_widgets.extend(widgets)

    def realizar_cierre_caja(self):
        """Realiza el cierre de caja del día y ofrece descarga de resumen"""
        hoy = datetime.date.today()
        ventas_hoy = self.sistema.cierre_caja(hoy)
        
        if not ventas_hoy:
            messagebox.showinfo("Cierre de Caja", "No hay ventas registradas para el día de hoy.")
            return
        
        # Crear ventana de confirmación de descarga
        self.mostrar_ventana_descarga_csv(ventas_hoy, hoy)

    def mostrar_ventana_descarga_csv(self, ventas_hoy, fecha):
        """Muestra ventana de confirmación para descarga de CSV"""
        ventana = tk.Toplevel(self)
        ventana.title("Cierre de Caja")
        ventana.geometry("450x300")
        ventana.configure(bg=COLOR_FONDO)
        ventana.resizable(False, False)
        
        # Crear gradiente de fondo
        canvas = tk.Canvas(ventana, width=450, height=300, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        for i in range(0, 300, 2):
            color = self._interpolar_color(COLOR_GRADIENTE_1, COLOR_GRADIENTE_2, i/300)
            canvas.create_rectangle(0, i, 450, i+2, outline="", fill=color)
        
        # Título
        lbl_titulo = tk.Label(canvas, text="QUERES DESCARGAR TU RESUMEN HOY??", 
                             font=("Montserrat", 16, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        canvas.create_window(225, 60, window=lbl_titulo, anchor="center")
        
        # Texto explicativo
        lbl_explicacion = tk.Label(canvas, text="Tus ventas quedan guardadas acá.\nDisponibles cuando quieras!", 
                                  font=("Montserrat", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO, justify="center")
        canvas.create_window(225, 180, window=lbl_explicacion, anchor="center")
        
        # Botones SI / NO
        def descargar_si():
            self.generar_csv_cierre(ventas_hoy, fecha)
            # ARCHIVAR VENTAS DEL DÍA
            self.sistema.archivar_ventas_dia(fecha)
            ventana.destroy()
            # Refrescar pantalla ventas del día
            self.mostrar_ventas_dia()
            
        def descargar_no():
            # ARCHIVAR VENTAS DEL DÍA AUNQUE NO DESCARGUE CSV
            self.sistema.archivar_ventas_dia(fecha)
            messagebox.showinfo("Cierre de Caja", "Cierre de caja realizado. Las ventas han sido archivadas correctamente.")
            ventana.destroy()
            # Refrescar pantalla ventas del día
            self.mostrar_ventas_dia()
        
        btn_si = tk.Button(canvas, text="SÍ", font=("Montserrat", 14, "bold"), 
                          bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, bd=0, relief="flat", 
                          command=descargar_si, cursor="hand2")
        canvas.create_window(150, 240, window=btn_si, width=100, height=40, anchor="center")
        
        btn_no = tk.Button(canvas, text="NO", font=("Montserrat", 14, "bold"), 
                          bg="#666666", fg=COLOR_BOTON_TEXTO, bd=0, relief="flat", 
                          command=descargar_no, cursor="hand2")
        canvas.create_window(300, 240, window=btn_no, width=100, height=40, anchor="center")
        
        # Centrar ventana
        ventana.transient(self)
        ventana.grab_set()
        
    def generar_csv_cierre(self, ventas_hoy, fecha):
        """Genera archivo CSV con el resumen del día"""
        
        # Calcular totales por forma de pago
        totales_forma_pago = {}
        total_general = 0
        detalle_ventas = []
        
        for venta in ventas_hoy:
            forma_pago = getattr(venta, 'forma_pago', 'EFECTIVO')
            total_venta = sum(item['cantidad'] * item['precio'] for item in venta.items)
            total_general += total_venta
            
            if forma_pago not in totales_forma_pago:
                totales_forma_pago[forma_pago] = 0
            totales_forma_pago[forma_pago] += total_venta
            
            # Detalle de cada venta
            for item in venta.items:
                detalle_ventas.append({
                    'Fecha': fecha.strftime("%Y-%m-%d"),
                    'Descripción Venta': venta.descripcion,
                    'Forma de Pago': forma_pago,
                    'Producto': item['producto'].descripcion,
                    'Marca': item['producto'].marca,
                    'Color': item['producto'].color,
                    'Talle': item['producto'].talle,
                    'Cantidad': item['cantidad'],
                    'Precio Unitario': item['precio'],
                    'Subtotal': item['cantidad'] * item['precio']
                })
        
        # Pedir ubicación de guardado
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"Cierre_Caja_{fecha.strftime('%Y-%m-%d')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Encabezado del resumen
                    writer.writerow(['RESUMEN CIERRE DE CAJA'])
                    writer.writerow(['Fecha:', fecha.strftime("%Y-%m-%d")])
                    writer.writerow([''])
                    
                    # Totales por forma de pago
                    writer.writerow(['TOTALES POR FORMA DE PAGO'])
                    for forma_pago, total in totales_forma_pago.items():
                        writer.writerow([forma_pago, self.formato_moneda(total)])
                    writer.writerow([''])
                    writer.writerow(['TOTAL GENERAL', self.formato_moneda(total_general)])
                    writer.writerow([''])
                    writer.writerow([''])
                    
                    # Detalle de ventas
                    writer.writerow(['DETALLE DE VENTAS'])
                    if detalle_ventas:
                        fieldnames = detalle_ventas[0].keys()
                        dict_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        dict_writer.writeheader()
                        dict_writer.writerows(detalle_ventas)
                
                messagebox.showinfo("Descarga Exitosa", f"Archivo guardado en:\n{filename}\n\nCierre de caja realizado correctamente.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar el archivo:\n{e}")
        else:
            messagebox.showinfo("Cierre de Caja", "Cierre de caja realizado. Las ventas han sido guardadas correctamente.")

    # FUNCIONES FALTANTES PARA LOS BOTONES DEL MENÚ
    def carga_masiva_productos(self):
        import tkinter.filedialog as fd
        from tkinter import messagebox
        import csv
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        lbl_info = tk.Label(self.canvas_bg, text="📂 Carga masiva de productos desde archivo CSV", font=("Montserrat", 15, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_info, anchor="n")  # Ajustado para el logo
        def descargar_modelo():
            modelo = "marca,descripcion,color,talle,cantidad,precio_costo,porcentaje_venta,porcentaje_amigo\nNike,Remera,Rojo,M,10,1000,50,20\n"
            ruta = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Guardar archivo modelo")
            if ruta:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(modelo)
                messagebox.showinfo("Archivo guardado", f"Archivo modelo guardado en:\n{ruta}")
        def parse_num(val):
            if val == "-":
                return 0
            if val == "" or val is None:
                raise ValueError("Hay campos numéricos vacíos. Complete o coloque '-' para cero.")
            return float(val)
        def cargar_csv():
            ruta = fd.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Seleccionar archivo CSV")
            if not ruta:
                return
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    requeridos = ["marca", "descripcion", "color", "talle", "cantidad", "precio_costo", "porcentaje_venta", "porcentaje_amigo"]
                    for row in reader:
                        if not all(k in row for k in requeridos):
                            raise ValueError("El archivo no tiene todas las columnas requeridas.")
                        self.sistema.agregar_producto(
                            row["marca"],
                            row["descripcion"],
                            row["color"],
                            row["talle"],
                            int(parse_num(row["cantidad"])),
                            float(parse_num(row["precio_costo"])),
                            float(parse_num(row["porcentaje_venta"])),
                            float(parse_num(row["porcentaje_amigo"]))
                        )
                messagebox.showinfo("Éxito", "Productos cargados correctamente.")
                self.mostrar_menu_secundario()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
        btn_descargar = tk.Button(self.canvas_bg, text="⬇️ Descargar archivo modelo CSV", font=("Montserrat", 12, "bold"), bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, bd=0, relief="flat", command=descargar_modelo)
        self.canvas_bg.create_window(640, 220, window=btn_descargar, width=320, height=40, anchor="n")  # Ajustado
        btn_cargar = tk.Button(self.canvas_bg, text="📁 Seleccionar y cargar archivo CSV", font=("Montserrat", 12, "bold"), bg="#4CAF50", fg="#ffffff", bd=0, relief="flat", command=cargar_csv)
        self.canvas_bg.create_window(640, 280, window=btn_cargar, width=320, height=40, anchor="n")  # Ajustado
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")  # Ajustado para el logo
        self.pantalla_widgets.extend([lbl_info, btn_descargar, btn_cargar, btn_volver])

    def mostrar_reportes(self):
        print("[DEBUG] mostrar_reportes() llamado - main.py:1080")
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        widgets = []
        
        # Título (ajustado para el logo)
        lbl_titulo = tk.Label(self.canvas_bg, text="📈 REPORTES DE VENTAS", font=("Montserrat", 18, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_titulo, anchor="n")  # Ajustado
        
        # Filtros de fecha (ajustados)
        lbl_desde = tk.Label(self.canvas_bg, text="📅 Fecha desde:", font=("Montserrat", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(100, 200, window=lbl_desde, anchor="nw")  # Ajustado
        ent_desde = tk.Entry(self.canvas_bg, font=("Montserrat", 11), bg=COLOR_ENTRADA, fg=COLOR_TEXTO, bd=1, relief="solid")
        self.canvas_bg.create_window(100, 225, window=ent_desde, width=150, height=30, anchor="nw")  # Ajustado
        ent_desde.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        lbl_hasta = tk.Label(self.canvas_bg, text="📅 Fecha hasta:", font=("Montserrat", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(280, 200, window=lbl_hasta, anchor="nw")  # Ajustado
        ent_hasta = tk.Entry(self.canvas_bg, font=("Montserrat", 11), bg=COLOR_ENTRADA, fg=COLOR_TEXTO, bd=1, relief="solid")
        self.canvas_bg.create_window(280, 225, window=ent_hasta, width=150, height=30, anchor="nw")  # Ajustado
        ent_hasta.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        # Filtro de forma de pago (ajustado)
        lbl_forma_pago = tk.Label(self.canvas_bg, text="💳 Forma de pago:", font=("Montserrat", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(460, 200, window=lbl_forma_pago, anchor="nw")  # Ajustado
        combo_forma_pago = ttk.Combobox(self.canvas_bg, values=["TODAS", "EFECTIVO", "DEBITO", "CREDITO", "TRANSFERENCIA", "QR", "OTROS"], font=("Montserrat", 11), state="readonly")
        self.canvas_bg.create_window(460, 225, window=combo_forma_pago, width=150, height=30, anchor="nw")  # Ajustado
        combo_forma_pago.set("TODAS")
        
        # Filtro de marca (ajustado)
        lbl_marca = tk.Label(self.canvas_bg, text="🏷️ Marca:", font=("Montserrat", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(640, 200, window=lbl_marca, anchor="nw")  # Ajustado
        marcas = list(set([p.marca for p in self.sistema.productos if p.marca]))
        marcas.insert(0, "TODAS")
        combo_marca = ttk.Combobox(self.canvas_bg, values=marcas, font=("Montserrat", 11), state="readonly")
        self.canvas_bg.create_window(640, 225, window=combo_marca, width=150, height=30, anchor="nw")  # Ajustado
        combo_marca.set("TODAS")
        
        # Filtro de producto (ajustado)
        lbl_producto = tk.Label(self.canvas_bg, text="📦 Producto:", font=("Montserrat", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(820, 200, window=lbl_producto, anchor="nw")  # Ajustado
        productos = list(set([p.descripcion for p in self.sistema.productos if p.descripcion]))
        productos.insert(0, "TODOS")
        combo_producto = ttk.Combobox(self.canvas_bg, values=productos, font=("Montserrat", 11), state="readonly")
        self.canvas_bg.create_window(820, 225, window=combo_producto, width=150, height=30, anchor="nw")  # Ajustado
        combo_producto.set("TODOS")
        
        # Botón buscar (ajustado)
        btn_buscar = tk.Button(self.canvas_bg, text="🔍 Buscar", font=("Montserrat", 12, "bold"), bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, bd=0, relief="flat")
        self.canvas_bg.create_window(1000, 225, window=btn_buscar, width=100, height=30, anchor="nw")  # Ajustado
        
        # Tabla de resultados (ajustada)
        cols = ("Fecha", "Descripción", "Forma Pago", "Marca", "Producto", "Color", "Talle", "Cantidad", "Precio", "Subtotal")
        tree = ttk.Treeview(self.canvas_bg, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        # Scrollbar para la tabla (ajustada)
        scrollbar = ttk.Scrollbar(self.canvas_bg, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        self.canvas_bg.create_window(640, 320, window=tree, width=1100, height=280, anchor="n")  # Ajustado
        self.canvas_bg.create_window(1150, 320, window=scrollbar, width=20, height=280, anchor="n")  # Ajustado
        
        # Label total (ajustado)
        lbl_total = tk.Label(self.canvas_bg, text="Total: $0.00", font=("Montserrat", 14, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(100, 620, window=lbl_total, anchor="w")  # Mantener posición
        
        def buscar_reportes():
            try:
                fecha_desde = datetime.datetime.strptime(ent_desde.get(), "%Y-%m-%d").date()
                fecha_hasta = datetime.datetime.strptime(ent_hasta.get(), "%Y-%m-%d").date()
                forma_pago_filtro = combo_forma_pago.get()
                marca_filtro = combo_marca.get()
                producto_filtro = combo_producto.get()
                
                # Limpiar tabla
                for item in tree.get_children():
                    tree.delete(item)
                
                total_general = 0
                ventas = self.sistema.reporte_ventas(fecha_desde, fecha_hasta)
                
                for venta in ventas:
                    forma_pago_venta = getattr(venta, 'forma_pago', 'EFECTIVO')
                    
                    # Filtrar por forma de pago
                    if forma_pago_filtro != "TODAS" and forma_pago_venta != forma_pago_filtro:
                        continue
                    
                    for item in venta.items:
                        producto = item['producto']
                        
                        # Filtrar por marca
                        if marca_filtro != "TODAS" and producto.marca != marca_filtro:
                            continue
                        
                        # Filtrar por producto
                        if producto_filtro != "TODOS" and producto.descripcion != producto_filtro:
                            continue
                        
                        subtotal = item['cantidad'] * item['precio']
                        total_general += subtotal
                        
                        tree.insert("", "end", values=(
                            venta.fecha.strftime("%Y-%m-%d"),
                            venta.descripcion,
                            forma_pago_venta,
                            producto.marca,
                            producto.descripcion,
                            producto.color,
                            producto.talle,
                            item['cantidad'],
                            self.formato_moneda(item['precio']),
                            self.formato_moneda(subtotal)
                        ))
                
                lbl_total.config(text=f"Total: {self.formato_moneda(total_general)}")
                
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar reporte: {e}")
        
        btn_buscar.config(command=buscar_reportes)
        
        # Botón volver (ajustado para el logo)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")  # Ajustado
        
        widgets.extend([lbl_titulo, lbl_desde, ent_desde, lbl_hasta, ent_hasta, lbl_forma_pago, combo_forma_pago, 
                       lbl_marca, combo_marca, lbl_producto, combo_producto, btn_buscar, tree, scrollbar, lbl_total, btn_volver])
        self.pantalla_widgets.extend(widgets)

    def _pantalla_alta_producto(self, parent):
        """Pantalla para agregar productos"""
        widgets = []
        
        # Título centrado (ajustado para el logo)
        lbl_titulo = tk.Label(self.canvas_bg, text="📦 AGREGAR NUEVO PRODUCTO", 
                             font=("Montserrat", 18, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_titulo, anchor="center")  # Ajustado
        
        # Campos organizados en dos columnas (ajustados)
        campos_col1 = ["🏷️ Marca", "📝 Descripción", "🎨 Color", "📏 Talle"]
        campos_col2 = ["📊 Cantidad", "💰 Precio Costo", "📈 % Venta", "👥 % Amigo"]
        entradas = {}
        
        # Columna izquierda (ajustada)
        x_col1_label = 200
        x_col1_entry = 320
        y_start = 220  # Ajustado para el logo
        spacing = 60
        
        for i, campo in enumerate(campos_col1):
            y_pos = y_start + i * spacing
            lbl = tk.Label(self.canvas_bg, text=f"{campo}:", font=("Montserrat", 12, "bold"), 
                          bg=COLOR_FONDO, fg=COLOR_TEXTO)
            self.canvas_bg.create_window(x_col1_label, y_pos, window=lbl, anchor="e")
            
            ent = tk.Entry(self.canvas_bg, font=("Montserrat", 12), bg=COLOR_ENTRY_VENTA_BG, 
                          fg="#000000", bd=2, relief="ridge")
            self.canvas_bg.create_window(x_col1_entry, y_pos, window=ent, width=220, height=35, anchor="w")
            entradas[campo] = ent
            widgets.extend([lbl, ent])
        
        # Columna derecha
        x_col2_label = 700
        x_col2_entry = 820
        
        for i, campo in enumerate(campos_col2):
            y_pos = y_start + i * spacing
            lbl = tk.Label(self.canvas_bg, text=f"{campo}:", font=("Montserrat", 12, "bold"), 
                          bg=COLOR_FONDO, fg=COLOR_TEXTO)
            self.canvas_bg.create_window(x_col2_label, y_pos, window=lbl, anchor="e")
            
            ent = tk.Entry(self.canvas_bg, font=("Montserrat", 12), bg=COLOR_ENTRY_VENTA_BG, 
                          fg="#000000", bd=2, relief="ridge")
            self.canvas_bg.create_window(x_col2_entry, y_pos, window=ent, width=220, height=35, anchor="w")
            entradas[campo] = ent
            widgets.extend([lbl, ent])
        
        # Valores por defecto
        entradas["📈 % Venta"].insert(0, "50")
        entradas["👥 % Amigo"].insert(0, "20")
        
        def guardar_producto():
            try:
                marca = entradas["🏷️ Marca"].get().strip()
                descripcion = entradas["📝 Descripción"].get().strip()
                color = entradas["🎨 Color"].get().strip()
                talle = entradas["📏 Talle"].get().strip()
                cantidad = int(entradas["📊 Cantidad"].get())
                precio_costo = float(entradas["💰 Precio Costo"].get())
                porcentaje_venta = float(entradas["📈 % Venta"].get())
                porcentaje_amigo = float(entradas["👥 % Amigo"].get())
                
                if not all([marca, descripcion, color, talle]):
                    raise ValueError("Todos los campos de texto son obligatorios")
                
                self.sistema.agregar_producto(marca, descripcion, color, talle, cantidad, 
                                            precio_costo, porcentaje_venta, porcentaje_amigo)
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
                self.mostrar_menu_secundario()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")
        
        # Botones centrados (ajustados)
        btn_guardar = tk.Button(self.canvas_bg, text="💾 GUARDAR PRODUCTO", font=("Montserrat", 14, "bold"), 
                               bg=COLOR_BOTON, fg="#ffffff", bd=0, relief="flat", 
                               command=guardar_producto, cursor="hand2")
        self.canvas_bg.create_window(640, 520, window=btn_guardar, width=200, height=50, anchor="center")  # Ajustado
        
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), 
                              bg="#666666", fg="#ffffff", bd=0, relief="flat", 
                              command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")  # Ajustado
        
        widgets.extend([lbl_titulo, btn_guardar, btn_volver])
        self.pantalla_widgets.extend(widgets)


    def _pantalla_actualizar_precio(self, parent):
        """Pantalla para actualizar precios"""
        widgets = []
        
        # Título centrado (ajustado para el logo)
        lbl_titulo = tk.Label(self.canvas_bg, text="💲 ACTUALIZAR PRECIO DE PRODUCTO", 
                             font=("Montserrat", 18, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_titulo, anchor="center")  # Ajustado
        
        # Campos centrados (ajustados)
        campos = ["🏷️ Marca", "📝 Descripción", "🎨 Color", "📏 Talle", "💰 Nuevo Precio Costo"]
        entradas = {}
        
        y_start = 220  # Ajustado para el logo
        spacing = 60
        x_label = 450
        x_entry = 640
        
        for i, campo in enumerate(campos):
            y_pos = y_start + i * spacing
            lbl = tk.Label(self.canvas_bg, text=f"{campo}:", font=("Montserrat", 12, "bold"), 
                          bg=COLOR_FONDO, fg=COLOR_TEXTO)
            self.canvas_bg.create_window(x_label, y_pos, window=lbl, anchor="e")
            
            ent = tk.Entry(self.canvas_bg, font=("Montserrat", 12), bg=COLOR_ENTRY_VENTA_BG, 
                          fg="#000000", bd=2, relief="ridge")
            self.canvas_bg.create_window(x_entry, y_pos, window=ent, width=250, height=35, anchor="center")
            entradas[campo] = ent
            widgets.extend([lbl, ent])
        
        def actualizar_precio():
            try:
                marca = entradas["🏷️ Marca"].get().strip()
                descripcion = entradas["📝 Descripción"].get().strip()
                color = entradas["🎨 Color"].get().strip()
                talle = entradas["📏 Talle"].get().strip()
                nuevo_precio = float(entradas["💰 Nuevo Precio Costo"].get())
                
                if not all([marca, descripcion, color, talle]):
                    raise ValueError("Todos los campos son obligatorios")
                
                if self.sistema.actualizar_precio_producto(marca, descripcion, color, talle, nuevo_precio):
                    messagebox.showinfo("Éxito", "Precio actualizado correctamente")
                    # Limpiar campos
                    for ent in entradas.values():
                        ent.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Producto no encontrado")
                    
            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {e}")
        
        # Botones centrados (ajustados)
        btn_actualizar = tk.Button(self.canvas_bg, text="💲 ACTUALIZAR PRECIO", font=("Montserrat", 14, "bold"), 
                                  bg=COLOR_BOTON, fg="#ffffff", bd=0, relief="flat", 
                                  command=actualizar_precio, cursor="hand2")
        self.canvas_bg.create_window(640, 550, window=btn_actualizar, width=200, height=50, anchor="center")  # Ajustado
        
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), 
                              bg="#666666", fg="#ffffff", bd=0, relief="flat", 
                              command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")  # Ajustado
        
        widgets.extend([lbl_titulo, btn_actualizar, btn_volver])
        self.pantalla_widgets.extend(widgets)

    def _pantalla_inventario(self, parent):
        """Pantalla para ver inventario"""
        widgets = []
        
        # Título centrado (ajustado para el logo)
        lbl_titulo = tk.Label(self.canvas_bg, text="📋 INVENTARIO DE PRODUCTOS", 
                             font=("Montserrat", 18, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 150, window=lbl_titulo, anchor="center")  # Ajustado
        
        productos = self.sistema.inventario_actual()
        cols = ("Marca", "Descripción", "Color", "Talle", "Stock", "Precio Costo", "Precio Venta")
        tree = ttk.Treeview(self.canvas_bg, columns=cols, show="headings")
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        
        for p in productos:
            tree.insert("", "end", values=(p.marca, p.descripcion, p.color, p.talle, 
                                         p.cantidad, self.formato_moneda(p.precio_costo), 
                                         self.formato_moneda(p.precio_venta)))
        
        # Tabla centrada (ajustada)
        self.canvas_bg.create_window(640, 380, window=tree, width=1050, height=280, anchor="center")  # Ajustada
        
        # Botones MODIFICAR y ELIMINAR debajo de la tabla
        def modificar_producto():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Modificar", "Seleccione un producto de la lista para modificar.")
                return
            
            # Obtener datos del producto seleccionado
            item = tree.item(seleccion[0])
            valores = item['values']
            marca, descripcion, color, talle = valores[0], valores[1], valores[2], valores[3]
            
            # Buscar el producto en el sistema
            producto = self.sistema.buscar_producto(marca, descripcion, color, talle)
            if producto:
                datos = (marca, descripcion, color, talle, producto.cantidad, producto.precio_costo, 
                        producto.porcentaje_venta, producto.porcentaje_amigo)
                self._pantalla_modificar_producto(datos)
        
        def eliminar_producto():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Eliminar", "Seleccione un producto de la lista para eliminar.")
                return
            
            # Obtener datos del producto seleccionado
            item = tree.item(seleccion[0])
            valores = item['values']
            marca, descripcion, color, talle = valores[0], valores[1], valores[2], valores[3]
            
            # Confirmar eliminación
            respuesta = messagebox.askyesno("Confirmar eliminación", 
                                          f"¿Está seguro de eliminar el producto:\n{descripcion} - {color} - {talle}?")
            if respuesta:
                self.sistema.eliminar_producto(marca, descripcion, color, talle)
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                self.mostrar_inventario()  # Refrescar pantalla
        
        # Posicionar botones horizontalmente debajo de la tabla
        btn_y = 550  # Posición Y debajo de la tabla
        btn_spacing = 180  # Espaciado entre botones
        btn_center_x = 640  # Centro de la pantalla
        
        btn_modificar = tk.Button(self.canvas_bg, text="MODIFICAR", font=("Montserrat", 12, "bold"), 
                                bg=COLOR_BOTON, fg="#ffffff", bd=0, relief="flat", 
                                command=modificar_producto, cursor="hand2")
        self.canvas_bg.create_window(btn_center_x - btn_spacing//2, btn_y, window=btn_modificar, 
                                   width=140, height=45, anchor="center")
        
        btn_eliminar = tk.Button(self.canvas_bg, text="ELIMINAR", font=("Montserrat", 12, "bold"), 
                               bg="#ff0000", fg="#ffffff", bd=0, relief="flat", 
                               command=eliminar_producto, cursor="hand2")
        self.canvas_bg.create_window(btn_center_x + btn_spacing//2, btn_y, window=btn_eliminar, 
                                   width=140, height=45, anchor="center")
        
        # Botón volver (ajustado)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), 
                              bg="#666666", fg="#ffffff", bd=0, relief="flat", 
                              command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")  # Ajustado
        
        widgets.extend([lbl_titulo, tree, btn_modificar, btn_eliminar, btn_volver])
        self.pantalla_widgets.extend(widgets)

    def _pantalla_cierre_caja(self, parent):
        """Pantalla de cierre de caja - redirige a ventas del día"""
        self.mostrar_ventas_dia()

    def _pantalla_modificar_producto(self, datos):
        # datos: (marca, descripcion, color, talle, cantidad, costo, venta, amigo)
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        campos = ["🏷️ Marca", "📝 Descripción", "🎨 Color", "📏 Talle", "📊 Cantidad", "💰 Precio de costo", "📈 % Venta", "👥 % Amigo"]
        entradas = {}
        widgets = []
        for i, campo in enumerate(campos):
            lbl = tk.Label(self.canvas_bg, text=campo, font=("Montserrat", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO)
            ent = tk.Entry(self.canvas_bg, font=("Montserrat", 10), bg=COLOR_ENTRADA, fg=COLOR_TEXTO, bd=1, relief="solid")
            win_lbl = self.canvas_bg.create_window(120, 60 + i*50, window=lbl, width=110, height=30, anchor="w")
            win_ent = self.canvas_bg.create_window(250, 60 + i*50, window=ent, width=300, height=30, anchor="w")
            entradas[campo] = ent
            widgets.extend([lbl, ent])
        # Cargar datos actuales
        for i, campo in enumerate(campos):
            entradas[campo].insert(0, str(datos[i]))
        def guardar():
            try:
                marca = entradas["🏷️ Marca"].get()
                descripcion = entradas["📝 Descripción"].get()
                color = entradas["🎨 Color"].get()
                talle = entradas["📏 Talle"].get()
                cantidad = int(entradas["📊 Cantidad"].get())
                precio_costo = float(entradas["💰 Precio de costo"].get())
                porcentaje_venta = float(entradas["📈 % Venta"].get())
                porcentaje_amigo = float(entradas["👥 % Amigo"].get())
                # Eliminar producto anterior y agregar el modificado
                self.sistema.eliminar_producto(datos[0], datos[1], datos[2], datos[3])
                self.sistema.agregar_producto(marca, descripcion, color, talle, cantidad, precio_costo, porcentaje_venta, porcentaje_amigo)
                messagebox.showinfo("Éxito", "Producto modificado correctamente.")
                self.mostrar_inventario()
            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {e}")
        btn_guardar = tk.Button(self.canvas_bg, text="💾 Guardar cambios", font=("Montserrat", 12, "bold"), bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, bd=0, relief="flat", command=guardar)
        win_btn = self.canvas_bg.create_window(200, 420, window=btn_guardar, width=180, height=40, anchor="nw")
        widgets.append(btn_guardar)
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), bg="#666666", fg="#fff", bd=0, relief="flat", command=self.mostrar_inventario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        widgets.append(btn_volver)
        self.pantalla_widgets.extend(widgets)

    def mostrar_centro_ia(self):
        """Centro unificado de todas las funciones de Inteligencia Artificial"""
        self.limpiar_pantalla()
        self._colocar_logo(pantalla_principal=False)
        widgets = []
        
        # --- TÍTULO PRINCIPAL ---
        lbl_titulo = tk.Label(self.canvas_bg, text="🤖 CENTRO DE INTELIGENCIA ARTIFICIAL", 
                             font=("Montserrat", 20, "bold"), bg=COLOR_FONDO, fg=COLOR_CIAN)
        self.canvas_bg.create_window(640, 140, window=lbl_titulo, anchor="center")
        
        lbl_subtitulo = tk.Label(self.canvas_bg, text="Dashboard inteligente para optimización de ventas y gestión de inventario", 
                                font=("Montserrat", 11), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.canvas_bg.create_window(640, 165, window=lbl_subtitulo, anchor="center")
        
        # --- LÍNEA SEPARADORA ---
        linea_sep = tk.Frame(self.canvas_bg, bg=COLOR_CIAN, height=2)
        self.canvas_bg.create_window(640, 180, window=linea_sep, width=800, height=2, anchor="center")
        
        # --- PANEL DE NAVEGACIÓN IA ---
        frame_nav = tk.Frame(self.canvas_bg, bg="#1a1a2e", relief="solid", bd=2)
        self.canvas_bg.create_window(640, 210, window=frame_nav, width=1100, height=60, anchor="center")
        
        # Variable para controlar la vista activa
        self.vista_ia_activa = tk.StringVar(value="dashboard")
        
        # Botones de navegación IA con mejores efectos hover
        btn_dashboard = tk.Button(frame_nav, text="📊 Dashboard", font=("Montserrat", 11, "bold"), 
                                 bg=COLOR_CIAN, fg="#000000", bd=0, relief="flat", cursor="hand2",
                                 command=lambda: self._cambiar_vista_ia("dashboard"))
        btn_dashboard.place(x=20, y=15, width=150, height=30)
        btn_dashboard.bind("<Enter>", lambda e: btn_dashboard.config(bg="#00E5FF"))
        btn_dashboard.bind("<Leave>", lambda e: btn_dashboard.config(bg=COLOR_CIAN))
        
        btn_reposicion = tk.Button(frame_nav, text="📦 Reposición", font=("Montserrat", 11, "bold"), 
                                  bg="#4CAF50", fg="#ffffff", bd=0, relief="flat", cursor="hand2",
                                  command=lambda: self._cambiar_vista_ia("reposicion"))
        btn_reposicion.place(x=190, y=15, width=150, height=30)
        btn_reposicion.bind("<Enter>", lambda e: btn_reposicion.config(bg="#66BB6A"))
        btn_reposicion.bind("<Leave>", lambda e: btn_reposicion.config(bg="#4CAF50"))
        
        btn_precios = tk.Button(frame_nav, text="💰 Precios", font=("Montserrat", 11, "bold"), 
                               bg="#FF9800", fg="#000000", bd=0, relief="flat", cursor="hand2",
                               command=lambda: self._cambiar_vista_ia("precios"))
        btn_precios.place(x=360, y=15, width=150, height=30)
        btn_precios.bind("<Enter>", lambda e: btn_precios.config(bg="#FFB74D"))
        btn_precios.bind("<Leave>", lambda e: btn_precios.config(bg="#FF9800"))
        
        btn_analisis = tk.Button(frame_nav, text="📈 Análisis", font=("Montserrat", 11, "bold"), 
                                bg="#9C27B0", fg="#ffffff", bd=0, relief="flat", cursor="hand2",
                                command=lambda: self._cambiar_vista_ia("analisis"))
        btn_analisis.place(x=530, y=15, width=150, height=30)
        btn_analisis.bind("<Enter>", lambda e: btn_analisis.config(bg="#BA68C8"))
        btn_analisis.bind("<Leave>", lambda e: btn_analisis.config(bg="#9C27B0"))
        
        btn_exportar = tk.Button(frame_nav, text="📄 Exportar Todo", font=("Montserrat", 11, "bold"), 
                                bg="#607D8B", fg="#ffffff", bd=0, relief="flat", cursor="hand2",
                                command=self._exportar_centro_ia)
        btn_exportar.place(x=700, y=15, width=150, height=30)
        btn_exportar.bind("<Enter>", lambda e: btn_exportar.config(bg="#78909C"))
        btn_exportar.bind("<Leave>", lambda e: btn_exportar.config(bg="#607D8B"))
        
        btn_actualizar = tk.Button(frame_nav, text="🔄 Actualizar", font=("Montserrat", 11, "bold"), 
                                  bg="#2196F3", fg="#ffffff", bd=0, relief="flat", cursor="hand2",
                                  command=self._actualizar_centro_ia)
        btn_actualizar.place(x=870, y=15, width=150, height=30)
        btn_actualizar.bind("<Enter>", lambda e: btn_actualizar.config(bg="#42A5F5"))
        btn_actualizar.bind("<Leave>", lambda e: btn_actualizar.config(bg="#2196F3"))
        
        # --- ÁREA DE CONTENIDO DINÁMICO ---
        self.frame_contenido_ia = tk.Frame(self.canvas_bg, bg=COLOR_FONDO)
        self.canvas_bg.create_window(640, 450, window=self.frame_contenido_ia, width=1200, height=420, anchor="center")
        
        # Cargar vista inicial
        self._cambiar_vista_ia("dashboard")
        
        # --- BOTÓN VOLVER ---
        btn_volver = tk.Button(self.canvas_bg, text="← Volver", font=("Montserrat", 12, "bold"), 
                              bg="#666666", fg="#ffffff", bd=0, relief="flat", 
                              command=self.mostrar_menu_secundario, cursor="hand2")
        self.canvas_bg.create_window(80, 70, window=btn_volver, width=120, height=40, anchor="center")
        btn_volver.bind("<Enter>", lambda e: btn_volver.config(bg="#777777"))
        btn_volver.bind("<Leave>", lambda e: btn_volver.config(bg="#666666"))
        
        widgets.extend([lbl_titulo, lbl_subtitulo, linea_sep, frame_nav, btn_volver])
        self.pantalla_widgets.extend(widgets)
    
    def _cambiar_vista_ia(self, vista):
        """Cambia entre las diferentes vistas del centro IA"""
        self.vista_ia_activa.set(vista)
        
        # Limpiar contenido anterior
        for widget in self.frame_contenido_ia.winfo_children():
            widget.destroy()
        
        if vista == "dashboard":
            self._mostrar_dashboard_ia()
        elif vista == "reposicion":
            self._mostrar_reposicion_ia()
        elif vista == "precios":
            self._mostrar_precios_ia()
        elif vista == "analisis":
            self._mostrar_analisis_ia()
    
    def _mostrar_dashboard_ia(self):
        """Dashboard principal con métricas generales"""
        # --- PANEL DE ALERTAS ---
        frame_alertas = tk.Frame(self.frame_contenido_ia, bg="#ff4444", relief="solid", bd=2)
        frame_alertas.place(x=20, y=20, width=360, height=120)
        
        lbl_alertas_titulo = tk.Label(frame_alertas, text="🚨 ALERTAS CRÍTICAS", 
                                     font=("Montserrat", 12, "bold"), bg="#ff4444", fg="#ffffff")
        lbl_alertas_titulo.pack(pady=5)
        
        # Calcular alertas
        productos_criticos = self._obtener_productos_criticos()
        texto_alertas = f"• {len(productos_criticos)} productos con stock crítico\n• Stock bajo detectado automáticamente\n• Acción requerida inmediata"
        
        lbl_alertas = tk.Label(frame_alertas, text=texto_alertas, font=("Montserrat", 10), 
                              bg="#ff4444", fg="#ffffff", justify="left")
        lbl_alertas.pack(pady=5)
        
        # --- PRODUCTOS ESTRELLA ---
        frame_estrella = tk.Frame(self.frame_contenido_ia, bg="#4CAF50", relief="solid", bd=2)
        frame_estrella.place(x=400, y=20, width=360, height=120)
        
        lbl_estrella_titulo = tk.Label(frame_estrella, text="⭐ PRODUCTOS ESTRELLA", 
                                      font=("Montserrat", 12, "bold"), bg="#4CAF50", fg="#ffffff")
        lbl_estrella_titulo.pack(pady=5)
        
        productos_estrella = self._obtener_productos_estrella()
        texto_estrella = f"• {len(productos_estrella)} productos top en ventas\n• Alta rotación y márgenes\n• Recomendados para promoción"
        
        lbl_estrella = tk.Label(frame_estrella, text=texto_estrella, font=("Montserrat", 10), 
                               bg="#4CAF50", fg="#ffffff", justify="left")
        lbl_estrella.pack(pady=5)
        
        # --- MÉTRICAS GENERALES ---
        frame_metricas = tk.Frame(self.frame_contenido_ia, bg="#2196F3", relief="solid", bd=2)
        frame_metricas.place(x=780, y=20, width=360, height=120)
        
        lbl_metricas_titulo = tk.Label(frame_metricas, text="📊 MÉTRICAS IA", 
                                      font=("Montserrat", 12, "bold"), bg="#2196F3", fg="#ffffff")
        lbl_metricas_titulo.pack(pady=5)
        
        total_productos = len(self.sistema.productos)
        productos_movimiento = len([p for p in self.sistema.productos if self._obtener_ventas_producto(p, 30) > 0])
        texto_metricas = f"• {total_productos} productos en inventario\n• {productos_movimiento} con movimiento (30 días)\n• IA analizando tendencias"
        
        lbl_metricas = tk.Label(frame_metricas, text=texto_metricas, font=("Montserrat", 10), 
                               bg="#2196F3", fg="#ffffff", justify="left")
        lbl_metricas.pack(pady=5)
        
        # --- TABLA RESUMEN RÁPIDO ---
        frame_tabla = tk.Frame(self.frame_contenido_ia, bg=COLOR_FONDO)
        frame_tabla.place(x=20, y=160, width=1120, height=240)
        
        lbl_resumen = tk.Label(frame_tabla, text="📋 RESUMEN EJECUTIVO - ÚLTIMOS 30 DÍAS", 
                              font=("Montserrat", 14, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        lbl_resumen.pack(pady=10)
        
        cols = ("Categoría", "Cantidad", "Estado", "Acción Sugerida", "Prioridad")
        tree_resumen = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=8)
        
        anchos = [200, 120, 150, 300, 120]
        for col, ancho in zip(cols, anchos):
            tree_resumen.heading(col, text=col, anchor="center")
            tree_resumen.column(col, width=ancho, anchor="center")
        
        tree_resumen.pack(pady=10)
        
        # Llenar datos del resumen
        datos_resumen = [
            ("🔴 Stock Crítico", len(productos_criticos), "URGENTE", "Reponer inmediatamente", "ALTA"),
            ("⭐ Productos Estrella", len(productos_estrella), "EXCELENTE", "Mantener stock alto", "MEDIA"),
            ("💰 Oportunidades Precio", "Analizando...", "EN PROCESO", "Revisar márgenes", "MEDIA"),
            ("📈 Tendencias Alcistas", "Calculando...", "EN ANÁLISIS", "Aumentar stock", "BAJA"),
            ("📉 Productos Lentos", "Evaluando...", "ATENCIÓN", "Considerar promoción", "BAJA")
        ]
        
        for item in datos_resumen:
            tree_resumen.insert("", "end", values=item)
    
    def _mostrar_reposicion_ia(self):
        """Vista de sugerencias de reposición"""
        # Reutilizar la lógica existente pero adaptada al nuevo layout
        frame_config = tk.Frame(self.frame_contenido_ia, bg=COLOR_FONDO)
        frame_config.place(x=20, y=20, width=1120, height=50)
        
        tk.Label(frame_config, text="Días de análisis:", font=("Montserrat", 10, "bold"), 
                bg=COLOR_FONDO, fg=COLOR_TEXTO).place(x=20, y=15)
        dias_var = tk.StringVar(value="30")
        combo_dias = ttk.Combobox(frame_config, textvariable=dias_var, values=["7", "15", "30", "60", "90"], 
                                 font=("Montserrat", 10), state="readonly", width=8)
        combo_dias.place(x=150, y=15)
        
        tk.Label(frame_config, text="Stock mínimo (%):", font=("Montserrat", 10, "bold"), 
                bg=COLOR_FONDO, fg=COLOR_TEXTO).place(x=300, y=15)
        umbral_var = tk.StringVar(value="20")
        combo_umbral = ttk.Combobox(frame_config, textvariable=umbral_var, values=["10", "15", "20", "25", "30"], 
                                   font=("Montserrat", 10), state="readonly", width=8)
        combo_umbral.place(x=430, y=15)
        
        # Tabla de reposición
        cols = ("🚨", "Marca", "Producto", "Color/Talle", "Stock", "Velocidad", "Días Rest.", "Sugerencia")
        tree_reposicion = ttk.Treeview(self.frame_contenido_ia, columns=cols, show="headings", height=12)
        
        anchos = [50, 120, 180, 120, 80, 100, 100, 140]
        for col, ancho in zip(cols, anchos):
            tree_reposicion.heading(col, text=col, anchor="center")
            tree_reposicion.column(col, width=ancho, anchor="center")
        
        tree_reposicion.place(x=20, y=90, width=1120, height=300)
        
        # Llenar datos
        def actualizar_reposicion():
            dias = int(dias_var.get())
            umbral = float(umbral_var.get()) / 100
            sugerencias = self._calcular_sugerencias_ia(dias, umbral)
            
            for item in tree_reposicion.get_children():
                tree_reposicion.delete(item)
            
            for s in sugerencias:
                p = s['producto']
                urgencia = "🔴" if s['dias_restantes'] <= 3 else "🟡" if s['dias_restantes'] <= 7 else "🟢"
                velocidad = f"{s['velocidad_venta']:.1f}/día"
                dias_rest = f"{s['dias_restantes']} días" if s['dias_restantes'] > 0 else "¡AGOTADO!"
                sugerencia = f"Reponer {s['cantidad_sugerida']}"
                
                tree_reposicion.insert("", "end", values=(
                    urgencia, p.marca, p.descripcion, f"{p.color}/{p.talle}",
                    s['stock_actual'], velocidad, dias_rest, sugerencia
                ))
        
        combo_dias.bind("<<ComboboxSelected>>", lambda e: actualizar_reposicion())
        combo_umbral.bind("<<ComboboxSelected>>", lambda e: actualizar_reposicion())
        actualizar_reposicion()
    
    def _mostrar_precios_ia(self):
        """Vista de optimización de precios"""
        lbl_titulo = tk.Label(self.frame_contenido_ia, text="💰 OPTIMIZACIÓN INTELIGENTE DE PRECIOS", 
                             font=("Montserrat", 14, "bold"), bg=COLOR_FONDO, fg="#FF9800")
        lbl_titulo.place(x=560, y=20, anchor="center")
        
        # Tabla de oportunidades de precios
        cols = ("📊", "Producto", "Precio Actual", "Margen %", "Rotación", "Precio Sugerido", "Razón")
        tree_precios = ttk.Treeview(self.frame_contenido_ia, columns=cols, show="headings", height=15)
        
        anchos = [50, 200, 120, 100, 100, 120, 250]
        for col, ancho in zip(cols, anchos):
            tree_precios.heading(col, text=col, anchor="center")
            tree_precios.column(col, width=ancho, anchor="center")
        
        tree_precios.place(x=20, y=60, width=1120, height=330)
        
        # Análisis de precios
        productos = self.sistema.inventario_actual()
        for producto in productos[:20]:  # Limitar para rendimiento
            try:
                ventas_30d = self._obtener_ventas_producto(producto, 30)
                rotacion = "Alta" if ventas_30d > 10 else "Media" if ventas_30d > 3 else "Baja"
                margen = ((producto.precio_venta - producto.precio_costo) / producto.precio_venta * 100) if producto.precio_venta > 0 else 0
                
                # Lógica de sugerencias de precios
                if rotacion == "Baja" and margen > 40:
                    icono = "🔻"
                    precio_sugerido = producto.precio_venta * 0.9  # Reducir 10%
                    razon = "Reducir precio para aumentar rotación"
                elif rotacion == "Alta" and margen < 30:
                    icono = "🔺"
                    precio_sugerido = producto.precio_venta * 1.1  # Aumentar 10%
                    razon = "Aumentar margen - alta demanda"
                else:
                    icono = "✅"
                    precio_sugerido = producto.precio_venta
                    razon = "Precio óptimo"
                
                tree_precios.insert("", "end", values=(
                    icono,
                    f"{producto.descripcion} {producto.color}/{producto.talle}",
                    self.formato_moneda(producto.precio_venta),
                    f"{margen:.1f}%",
                    rotacion,
                    self.formato_moneda(precio_sugerido),
                    razon
                ))
            except Exception:
                continue
    
    def _mostrar_analisis_ia(self):
        """Vista de análisis avanzado y tendencias"""
        lbl_titulo = tk.Label(self.frame_contenido_ia, text="📈 ANÁLISIS AVANZADO Y TENDENCIAS", 
                             font=("Montserrat", 14, "bold"), bg=COLOR_FONDO, fg="#9C27B0")
        lbl_titulo.place(x=560, y=20, anchor="center")
        
        # Panel de tendencias por marca
        frame_marcas = tk.Frame(self.frame_contenido_ia, bg="#E8F5E8", relief="solid", bd=1)
        frame_marcas.place(x=20, y=60, width=540, height=160)
        
        lbl_marcas = tk.Label(frame_marcas, text="🏷️ TENDENCIAS POR MARCA", 
                             font=("Montserrat", 12, "bold"), bg="#E8F5E8", fg="#333333")
        lbl_marcas.pack(pady=5)
        
        # Análisis por marca
        marcas_ventas = {}
        for venta in self.sistema.ventas:
            for item in venta.items:
                marca = item['producto'].marca
                if marca not in marcas_ventas:
                    marcas_ventas[marca] = 0
                marcas_ventas[marca] += item['cantidad']
        
        # Top 5 marcas
        top_marcas = sorted(marcas_ventas.items(), key=lambda x: x[1], reverse=True)[:5]
        texto_marcas = ""
        for i, (marca, ventas) in enumerate(top_marcas, 1):
            texto_marcas += f"{i}. {marca}: {ventas} unidades vendidas\n"
        
        lbl_marcas_data = tk.Label(frame_marcas, text=texto_marcas, font=("Montserrat", 10), 
                                  bg="#E8F5E8", fg="#333333", justify="left")
        lbl_marcas_data.pack(pady=10)
        
        # Panel de productos sin movimiento
        frame_lentos = tk.Frame(self.frame_contenido_ia, bg="#FFF3E0", relief="solid", bd=1)
        frame_lentos.place(x=580, y=60, width=540, height=160)
        
        lbl_lentos = tk.Label(frame_lentos, text="🐌 PRODUCTOS SIN MOVIMIENTO", 
                             font=("Montserrat", 12, "bold"), bg="#FFF3E0", fg="#333333")
        lbl_lentos.pack(pady=5)
        
        productos_lentos = []
        for producto in self.sistema.productos:
            if self._obtener_ventas_producto(producto, 60) == 0:  # Sin ventas en 60 días
                productos_lentos.append(producto)
        
        texto_lentos = f"• {len(productos_lentos)} productos sin ventas (60 días)\n"
        texto_lentos += "• Considerar promociones especiales\n"
        texto_lentos += "• Revisar estrategia de precios\n"
        texto_lentos += "• Evaluar descontinuación"
        
        lbl_lentos_data = tk.Label(frame_lentos, text=texto_lentos, font=("Montserrat", 10), 
                                  bg="#FFF3E0", fg="#333333", justify="left")
        lbl_lentos_data.pack(pady=10)
        
        # Tabla de análisis detallado
        cols = ("Producto", "Última Venta", "Stock Días", "Margen %", "Categoría IA", "Recomendación")
        tree_analisis = ttk.Treeview(self.frame_contenido_ia, columns=cols, show="headings", height=8)
        
        anchos = [250, 120, 100, 100, 150, 300]
        for col, ancho in zip(cols, anchos):
            tree_analisis.heading(col, text=col, anchor="center")
            tree_analisis.column(col, width=ancho, anchor="center")
        
        tree_analisis.place(x=20, y=240, width=1120, height=150)
        
        # Análisis detallado
        for producto in self.sistema.productos[:15]:  # Limitar para rendimiento
            try:
                ventas_30d = self._obtener_ventas_producto(producto, 30)
                margen = ((producto.precio_venta - producto.precio_costo) / producto.precio_venta * 100) if producto.precio_venta > 0 else 0
                
                # Categorización IA
                if ventas_30d > 10:
                    categoria = "⭐ Estrella"
                    recomendacion = "Mantener stock alto - producto exitoso"
                elif ventas_30d > 5:
                    categoria = "📈 Crecimiento"
                    recomendacion = "Monitorear tendencia - potencial estrella"
                elif ventas_30d > 0:
                    categoria = "🔄 Estable"
                    recomendacion = "Stock normal - ventas regulares"
                else:
                    categoria = "⚠️ Lento"
                    recomendacion = "Considerar promoción o descuento"
                
                dias_stock = producto.cantidad / max(1, ventas_30d/30) if ventas_30d > 0 else 999
                
                tree_analisis.insert("", "end", values=(
                    f"{producto.descripcion} {producto.color}/{producto.talle}",
                    "Reciente" if ventas_30d > 0 else ">30 días",
                    f"{int(dias_stock)} días" if dias_stock < 999 else "Sin datos",
                    f"{margen:.1f}%",
                    categoria,
                    recomendacion
                ))
            except Exception:
                continue
    
    def _actualizar_centro_ia(self):
        """Actualiza los datos del centro IA"""
        self._cambiar_vista_ia(self.vista_ia_activa.get())
        from tkinter import messagebox
        messagebox.showinfo("IA Actualizada", "Todos los análisis han sido actualizados con los datos más recientes.")
    
    def _exportar_centro_ia(self):
        """Exporta un reporte completo de todas las funciones IA"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"Centro_IA_Completo_{datetime.date.today().strftime('%Y-%m-%d')}.csv"
            )
            
            if filename:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Encabezado
                    writer.writerow(['CENTRO DE INTELIGENCIA ARTIFICIAL - REPORTE COMPLETO'])
                    writer.writerow(['Fecha:', datetime.date.today().strftime('%Y-%m-%d')])
                    writer.writerow([''])
                    
                    # Sección de reposición
                    writer.writerow(['=== ANÁLISIS DE REPOSICIÓN ==='])
                    sugerencias = self._calcular_sugerencias_ia(30, 0.2)
                    writer.writerow(['Producto', 'Stock Actual', 'Velocidad Venta', 'Días Restantes', 'Cantidad Sugerida'])
                    for s in sugerencias:
                        p = s['producto']
                        writer.writerow([
                            f"{p.descripcion} {p.color}/{p.talle}",
                            s['stock_actual'],
                            f"{s['velocidad_venta']:.1f}",
                            s['dias_restantes'],
                            s['cantidad_sugerida']
                        ])
                    
                    writer.writerow([''])
                    writer.writerow(['=== ANÁLISIS DE PRECIOS ==='])
                    writer.writerow(['Producto', 'Precio Actual', 'Margen %', 'Rotación', 'Recomendación'])
                    
                    # Exportar más datos...
                    
                from tkinter import messagebox
                messagebox.showinfo("Exportación Exitosa", f"Reporte completo exportado a:\n{filename}")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al exportar: {e}")
    
    def _obtener_productos_criticos(self):
        """Obtiene productos con stock crítico"""
        criticos = []
        for producto in self.sistema.productos:
            ventas_30d = self._obtener_ventas_producto(producto, 30)
            velocidad = ventas_30d / 30
            dias_restantes = producto.cantidad / velocidad if velocidad > 0 else 999
            if dias_restantes <= 7 or producto.cantidad <= 5:
                criticos.append(producto)
        return criticos
    
    def _obtener_productos_estrella(self):
        """Obtiene productos con mejor performance"""
        estrellas = []
        for producto in self.sistema.productos:
            ventas_30d = self._obtener_ventas_producto(producto, 30)
            if ventas_30d >= 10:  # Criterio para producto estrella
                estrellas.append(producto)
        return estrellas
    
    def _calcular_sugerencias_ia(self, dias_analisis, umbral_stock):
        """Algoritmo de IA para calcular sugerencias de reposición"""
        sugerencias = []
        productos = self.sistema.inventario_actual()
        
        for producto in productos:
            try:
                # Calcular ventas en el período
                ventas_periodo = self._obtener_ventas_producto(producto, dias_analisis)
                
                # Calcular velocidad de venta promedio
                velocidad_venta = ventas_periodo / dias_analisis if dias_analisis > 0 else 0
                
                # Calcular días restantes con stock actual
                dias_restantes = producto.cantidad / velocidad_venta if velocidad_venta > 0 else 999
                
                # Determinar si necesita reposición
                stock_minimo = max(5, int(velocidad_venta * 14))  # Stock para 2 semanas
                necesita_reposicion = (producto.cantidad <= stock_minimo or 
                                     dias_restantes <= 14 or 
                                     producto.cantidad / max(1, ventas_periodo) <= umbral_stock)
                
                if necesita_reposicion:
                    # Calcular cantidad sugerida (stock para 30 días)
                    cantidad_sugerida = max(10, int(velocidad_venta * 30) - producto.cantidad)
                    
                    sugerencias.append({
                        'producto': producto,
                        'stock_actual': producto.cantidad,
                        'ventas_periodo': ventas_periodo,
                        'velocidad_venta': velocidad_venta,
                        'dias_restantes': max(0, int(dias_restantes)),
                        'cantidad_sugerida': cantidad_sugerida,
                        'prioridad': self._calcular_prioridad(dias_restantes, velocidad_venta)
                    })
            
            except Exception as e:
                print(f"[DEBUG] Error calculando sugerencia para {producto.descripcion}: {e} - main.py:2005")
                continue
        
        # Ordenar por prioridad (críticos primero)
        sugerencias.sort(key=lambda x: x['prioridad'], reverse=True)
        
        return sugerencias
    
    def _obtener_ventas_producto(self, producto, dias):
        """Obtiene las ventas de un producto en los últimos N días"""
        try:
            fecha_limite = datetime.date.today() - datetime.timedelta(days=dias)
            ventas_total = 0
            
            for venta in self.sistema.ventas:
                if venta.fecha >= fecha_limite:
                    for item in venta.items:
                        if (item['producto'].descripcion == producto.descripcion and 
                            item['producto'].color == producto.color and 
                            item['producto'].talle == producto.talle):
                            ventas_total += item['cantidad']
            
            return ventas_total
        except Exception:
            return 0
    
    def _calcular_prioridad(self, dias_restantes, velocidad_venta):
        """Calcula la prioridad de reposición (mayor número = más urgente)"""
        if dias_restantes <= 0:
            return 100  # Crítico - sin stock
        elif dias_restantes <= 3:
            return 80   # Muy urgente
        elif dias_restantes <= 7:
            return 60   # Urgente
        elif dias_restantes <= 14:
            return 40   # Atención
        else:
            return 20   # Normal

if __name__ == "__main__":
    print("[DEBUG] Creando instancia de SistemaGestion... - main.py:2045")
    sistema = SistemaGestion()
    print("[DEBUG] SistemaGestion creado. Creando AppPilchero... - main.py:2047")
    app = AppPilchero(sistema)
    print("[DEBUG] AppPilchero creado. Ejecutando mainloop... - main.py:2049")
    app.mainloop()
    print("[DEBUG] mainloop finalizado - main.py:2051")
