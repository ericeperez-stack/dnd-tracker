import flet as ft

def main(page: ft.Page):
    page.title = "D&D Tracker Ultimate v2"
    page.theme_mode = ft.ThemeMode.DARK
    # Ajustamos un poco el ancho para que quepan los nuevos inputs en movil
    page.window_width = 450 
    page.window_height = 850
    page.padding = 15

    # --- VARIABLES GLOBALES ---
    combatientes = []
    turno_actual = -1 
    
    # Referencias a Inputs Principales (Agregados AC)
    txt_nombre = ft.TextField(label="Nombre / Enemigo", expand=True, text_size=14, height=50)
    txt_iniciativa = ft.TextField(label="Init", width=65, keyboard_type=ft.KeyboardType.NUMBER, text_size=14, height=50)
    txt_ac = ft.TextField(label="AC", width=60, keyboard_type=ft.KeyboardType.NUMBER, text_size=14, height=50)
    # Switch más compacto
    switch_enemigo = ft.Switch(label="Enemigo", active_color="red", value=True) 
    
    lista_visual = ft.Column(scroll="auto", expand=True)

    # --- FUNCIONES DE ALMACENAMIENTO (PERSISTENCIA) ---
    def obtener_jugadores_guardados():
        return page.client_storage.get("jugadores_saved") or []

    def guardar_jugador_db(nombre):
        lista = obtener_jugadores_guardados()
        if nombre and nombre not in lista:
            lista.append(nombre)
            page.client_storage.set("jugadores_saved", lista)

    def borrar_jugador_db(nombre):
        lista = obtener_jugadores_guardados()
        if nombre in lista:
            lista.remove(nombre)
            page.client_storage.set("jugadores_saved", lista)

    # --- DIALOGOS ---

    # 1. Diálogo para Cargar Jugadores Guardados (CORREGIDO UI + AC)
    def abrir_dialogo_cargar_party(e):
        jugadores = obtener_jugadores_guardados()
        if not jugadores:
            page.snack_bar = ft.SnackBar(ft.Text("No hay jugadores guardados. Ve a 'Gestionar'."))
            page.snack_bar.open = True
            page.update()
            return

        # Diccionario para guardar tuplas de inputs: nombre -> (input_init, input_ac)
        inputs_party_data = {} 

        columna_jugadores = ft.Column(scroll="auto", spacing=15)
        for j in jugadores:
            # Creamos inputs para Init y AC para cada jugador
            field_init = ft.TextField(label="Init", width=60, text_size=12, keyboard_type=ft.KeyboardType.NUMBER, height=45)
            field_ac = ft.TextField(label="AC", width=60, text_size=12, keyboard_type=ft.KeyboardType.NUMBER, height=45, value="10") # Default AC 10
            
            inputs_party_data[j] = (field_init, field_ac) 
            
            fila = ft.Row([
                ft.Icon("person", color="green200"),
                ft.Text(j, size=16, weight="bold", expand=True),
                field_init,
                field_ac
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            columna_jugadores.controls.append(fila)

        def confirmar_carga(e):
            count = 0
            # Iteramos sobre los inputs guardados
            for nombre, (input_init, input_ac) in inputs_party_data.items():
                if input_init.value and input_ac.value: 
                    try:
                        val_init = int(input_init.value)
                        val_ac = int(input_ac.value)
                        nuevo = {
                            'nombre': nombre, 
                            'init': val_init,
                            'ac': val_ac, # Guardamos AC
                            'es_enemigo': False, 
                            'estado': "", 
                            'turnos': 0
                        }
                        combatientes.append(nuevo)
                        count += 1
                    except ValueError:
                        pass # Ignorar si no son numeros
            
            if count > 0:
                combatientes.sort(key=lambda x: x['init'], reverse=True)
                renderizar_lista()
                page.close(dlg_carga)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Introduce al menos una Iniciativa y AC válidas."))
                page.snack_bar.open = True
                page.update()

        # SOLUCIÓN UI: Usamos un Container con altura máxima para el contenido,
        # forzando el scroll interno y dejando los botones de acción libres abajo.
        dlg_carga = ft.AlertDialog(
            title=ft.Text("Cargar Party (Init & AC)"),
            content=ft.Container(
                content=columna_jugadores, 
                height=400, # Altura fija suficiente para ver varios, el resto scrollea
                width=380,
                padding=10,
                border=ft.border.all(1, "grey300"),
                border_radius=10
            ), 
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_carga)),
                ft.ElevatedButton("¡A Luchar!", on_click=confirmar_carga, bgcolor="green", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True
        )
        page.open(dlg_carga)

    # 2. Diálogo para Gestionar Jugadores (Sin cambios mayores)
    def abrir_gestion_jugadores(e):
        txt_nuevo_pj = ft.TextField(label="Nombre Nuevo Jugador", expand=True)
        lista_db_ui = ft.Column(scroll="auto")

        def refrescar_lista_db():
            lista_db_ui.controls.clear()
            saved = obtener_jugadores_guardados()
            for nombre in saved:
                lista_db_ui.controls.append(
                    ft.Row([
                        ft.Icon("person", color="blue"),
                        ft.Text(nombre, expand=True),
                        ft.IconButton(icon="delete", icon_color="red", data=nombre, on_click=btn_borrar_db_click)
                    ])
                )
            page.update()

        def btn_agregar_db_click(e):
            if txt_nuevo_pj.value:
                guardar_jugador_db(txt_nuevo_pj.value)
                txt_nuevo_pj.value = ""
                refrescar_lista_db()
                txt_nuevo_pj.focus()

        def btn_borrar_db_click(e):
            borrar_jugador_db(e.control.data)
            refrescar_lista_db()

        refrescar_lista_db() 

        dlg_gestion = ft.AlertDialog(
            title=ft.Text("Base de Datos Jugadores"),
            content=ft.Container(
                width=350, height=400,
                content=ft.Column([
                    ft.Row([txt_nuevo_pj, ft.IconButton(icon="save", on_click=btn_agregar_db_click, tooltip="Guardar")]),
                    ft.Divider(),
                    ft.Text("Jugadores Guardados (Nombres fijos):", size=12, italic=True),
                    ft.Container(content=lista_db_ui, expand=True, border=ft.border.all(1, "grey800"), border_radius=5, padding=5)
                ])
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dlg_gestion))]
        )
        page.open(dlg_gestion)

    # 3. Diálogo para EDITAR ESTADO y AC (EN CUALQUIER MOMENTO)
    def abrir_editor_estado(e):
        combatiente = e.control.data 
        
        # Inputs para editar
        txt_edit_ac = ft.TextField(label="AC Actual", value=str(combatiente.get('ac', 10)), keyboard_type=ft.KeyboardType.NUMBER, width=80)
        txt_edit_estado = ft.TextField(label="Nombre Estado", value=combatiente['estado'], expand=True)
        txt_edit_turnos = ft.TextField(label="Turnos", value=str(combatiente['turnos']), keyboard_type=ft.KeyboardType.NUMBER, width=80)
        
        def guardar_cambios_estado(e):
            try:
                # Guardamos AC, Estado y Turnos
                combatiente['ac'] = int(txt_edit_ac.value)
                combatiente['estado'] = txt_edit_estado.value
                combatiente['turnos'] = int(txt_edit_turnos.value) if txt_edit_turnos.value else 0
                renderizar_lista()
                page.close(dlg_edit)
            except ValueError:
                txt_edit_ac.error_text = "Error numérico"
                page.update()
        
        def quitar_estado_manual(e):
            combatiente['estado'] = ""
            combatiente['turnos'] = 0
            # No tocamos la AC al limpiar estado
            renderizar_lista()
            page.close(dlg_edit)

        dlg_edit = ft.AlertDialog(
            title=ft.Text(f"Editar: {combatiente['nombre']}"),
            content=ft.Container(
                height=250, width=350,
                content=ft.Column([
                    ft.Text("Modificar Estadísticas de Combate", weight="bold"),
                    ft.Row([txt_edit_ac], alignment=ft.MainAxisAlignment.START), # Fila para AC
                    ft.Divider(),
                    ft.Text("Estados alterados:"),
                    ft.Row([txt_edit_estado, txt_edit_turnos]) # Fila para Estados
                ])
            ),
            actions=[
                ft.TextButton("Limpiar Estado Solo", on_click=quitar_estado_manual, style=ft.ButtonStyle(color="red200")),
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_edit)),
                ft.ElevatedButton("GUARDAR CAMBIOS", on_click=guardar_cambios_estado, bgcolor="blue900", color="white")
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            modal=True
        )
        page.open(dlg_edit)


    # --- RENDERIZADO PRINCIPAL (Actualizado con AC) ---
    def renderizar_lista():
        lista_visual.controls.clear()

        for i, c in enumerate(combatientes):
            es_enemigo = c['es_enemigo']
            es_turno = (i == turno_actual)
            ac_actual = c.get('ac', '?') # Obtenemos AC de forma segura
            
            # Estilos visuales
            bg_color = "red900" if es_enemigo else "bluegrey900"
            if es_turno:
                borde = ft.border.all(2, "yellow")
                bg_color = "black" 
            else:
                borde = None
            
            # --- Fila de Estado ---
            fila_estado = ft.Container()
            if c['estado']:
                fila_estado = ft.Container(
                    bgcolor="grey900", border_radius=5, padding=5, margin=ft.margin.only(top=5),
                    content=ft.Row([
                        ft.Icon(name="water_drop", color="purple", size=16),
                        ft.Text(f"{c['estado']} ({c['turnos']} turnos restantes)", size=12, color="yellow", expand=True),
                    ])
                )

            # --- Tarjeta del Personaje ---
            card = ft.Container(
                bgcolor=bg_color, border=borde, border_radius=10, padding=10,
                animate_opacity=300,
                content=ft.Column([
                    ft.Row([
                        # Icono Principal
                        ft.Icon(name="skull" if es_enemigo else "shield", color="white70", size=30),
                        
                        # Columna central con datos
                        ft.Column([
                            ft.Text(c['nombre'], weight="bold", size=17),
                            ft.Row([
                                ft.Text(f"Init: {c['init']}", size=13, italic=True, color="grey300"),
                                ft.Text("|", color="grey500"),
                                # MOSTRAR AC AQUÍ CON UN ICONO DE ESCUDO PEQUEÑO
                                ft.Icon("shield_outlined", size=14, color="grey300"),
                                ft.Text(f"AC: {ac_actual}", weight="bold", size=14, color="blue200"),
                            ], spacing=5)
                        ], expand=True, spacing=2),

                        # Botones de acción rápida
                        ft.Row([
                             # Botón Editar (Lápiz)
                            ft.IconButton(icon="edit", icon_color="blue200", tooltip="Editar AC/Estado", data=c, on_click=abrir_editor_estado),
                            # Botón Borrar (X)
                            ft.IconButton(icon="close", icon_color="grey500", tooltip="Eliminar del combate", data=c, on_click=eliminar_combatiente)
                        ], spacing=0)
                       
                    ]),
                    fila_estado
                ])
            )
            lista_visual.controls.append(card)
        page.update()

    # --- LOGICA DE BOTONES PRINCIPALES ---

    def agregar_manual_click(e):
        # Validamos que haya nombre, iniciativa Y AC
        if not txt_nombre.value or not txt_iniciativa.value or not txt_ac.value: 
            txt_nombre.error_text = "Faltan datos" if not txt_nombre.value else None
            page.update()
            return
        try:
            val_init = int(txt_iniciativa.value)
            val_ac = int(txt_ac.value) # Leemos la AC
            
            nuevo = {
                'nombre': txt_nombre.value, 
                'init': val_init,
                'ac': val_ac, # Guardamos AC
                'es_enemigo': switch_enemigo.value, 
                'estado': "", 
                'turnos': 0
            }
            combatientes.append(nuevo)
            combatientes.sort(key=lambda x: x['init'], reverse=True)
            
            # Limpieza
            txt_nombre.value = ""
            txt_iniciativa.value = ""
            txt_ac.value = "" # Limpiamos AC
            txt_nombre.error_text = None
            txt_nombre.focus()
            renderizar_lista()
        except ValueError: 
            txt_iniciativa.error_text = "Error"
            page.update()

    def eliminar_combatiente(e):
        item = e.control.data
        if item in combatientes:
            combatientes.remove(item)
            renderizar_lista()

    def siguiente_turno(e):
        nonlocal turno_actual
        if not combatientes: return
        
        # Reducir turno del que termina
        if turno_actual != -1 and turno_actual < len(combatientes):
            pj = combatientes[turno_actual]
            if pj['estado'] and pj['turnos'] > 0:
                pj['turnos'] -= 1
                if pj['turnos'] <= 0: pj['estado'] = "" 

        turno_actual += 1
        if turno_actual >= len(combatientes): turno_actual = 0
        renderizar_lista()

    def limpiar_todo(e):
        nonlocal turno_actual
        combatientes.clear()
        turno_actual = -1
        renderizar_lista()

    # --- LAYOUT FINAL ---
    
    barra_superior = ft.Row([
        ft.ElevatedButton("Gestionar Jugadores", icon="person_add", on_click=abrir_gestion_jugadores, height=35),
        ft.ElevatedButton("Cargar Party", icon="group_add", on_click=abrir_dialogo_cargar_party, bgcolor="green800", color="white", height=35),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Fila de inputs manuales (Ahora son 3 + el boton)
    inputs_rapidos = ft.Row([
        txt_nombre, 
        txt_iniciativa,
        txt_ac, # Agregado el campo AC
        ft.IconButton(icon="add_circle", icon_color="red400", icon_size=35, on_click=agregar_manual_click, tooltip="Agregar manual")
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    header = ft.Column([
        ft.Text("⚔️ DM Tracker", size=22, weight="bold", text_align="center", color="red200"),
        barra_superior,
        ft.Divider(color="grey800"),
        ft.Row([ft.Text("Agregar Manual / Enemigo:", size=12, italic=True), switch_enemigo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        inputs_rapidos,
        ft.Divider(thickness=2, color="red900"),
    ], spacing=10)

    page.add(
        header,
        lista_visual
    )
    
    page.floating_action_button = ft.FloatingActionButton(text="Siguiente Turno", icon="play_arrow", on_click=siguiente_turno, bgcolor="yellow800")
    
    page.appbar = ft.AppBar(
        leading=ft.Icon("casino"),
        title=ft.Text("Iniciativa D&D"),
        bgcolor="grey900", 
        actions=[ft.IconButton(icon="delete_forever", tooltip="Limpiar Combate", on_click=limpiar_todo, icon_color="red")]
    )

# MODO FINAL PARA CELULAR
ft.app(target=main)
