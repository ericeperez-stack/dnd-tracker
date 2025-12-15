import flet as ft

def main(page: ft.Page):
    page.title = "D&D Tracker Ultimate"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 420
    page.window_height = 850
    page.padding = 15

    # --- VARIABLES GLOBALES ---
    combatientes = []
    turno_actual = -1 
    
    # Referencias a Inputs
    txt_nombre = ft.TextField(label="Nombre / Enemigo", expand=True, text_size=14)
    txt_iniciativa = ft.TextField(label="Init", width=70, keyboard_type=ft.KeyboardType.NUMBER, text_size=14)
    switch_enemigo = ft.Switch(label="Es Enemigo", active_color="red", value=True) 
    
    lista_visual = ft.Column(scroll="auto", expand=True)

    # --- FUNCIONES DE ALMACENAMIENTO (PERSISTENCIA) ---
    def obtener_jugadores_guardados():
        return page.client_storage.get("jugadores_saved") or []

    def guardar_jugador_db(nombre):
        lista = obtener_jugadores_guardados()
        if nombre not in lista:
            lista.append(nombre)
            page.client_storage.set("jugadores_saved", lista)

    def borrar_jugador_db(nombre):
        lista = obtener_jugadores_guardados()
        if nombre in lista:
            lista.remove(nombre)
            page.client_storage.set("jugadores_saved", lista)

    # --- DIALOGOS ---

    # 1. Diálogo para Cargar Jugadores Guardados
    def abrir_dialogo_cargar_party(e):
        jugadores = obtener_jugadores_guardados()
        if not jugadores:
            page.snack_bar = ft.SnackBar(ft.Text("No hay jugadores guardados. Ve a 'Gestionar'."))
            page.snack_bar.open = True
            page.update()
            return

        inputs_iniciativa = {} 

        columna_jugadores = ft.Column()
        for j in jugadores:
            field = ft.TextField(label="Init", width=60, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
            inputs_iniciativa[j] = field 
            
            fila = ft.Row([
                ft.Text(j, size=16, weight="bold", expand=True),
                field
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            columna_jugadores.controls.append(fila)

        def confirmar_carga(e):
            count = 0
            for nombre, input_field in inputs_iniciativa.items():
                if input_field.value: 
                    try:
                        val = int(input_field.value)
                        nuevo = {
                            'nombre': nombre, 
                            'init': val, 
                            'es_enemigo': False, 
                            'estado': "", 
                            'turnos': 0
                        }
                        combatientes.append(nuevo)
                        count += 1
                    except ValueError:
                        pass
            
            if count > 0:
                combatientes.sort(key=lambda x: x['init'], reverse=True)
                renderizar_lista()
                page.close(dlg_carga)
            else:
                input_field.error_text = "Pon al menos una iniciativa"
                page.update()

        dlg_carga = ft.AlertDialog(
            title=ft.Text("Cargar Party"),
            content=ft.Container(content=columna_jugadores, height=300, width=300), 
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_carga)),
                ft.ElevatedButton("¡A Luchar!", on_click=confirmar_carga, bgcolor="green", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg_carga)

    # 2. Diálogo para Gestionar (Crear/Borrar) Jugadores Permanentes
    def abrir_gestion_jugadores(e):
        txt_nuevo_pj = ft.TextField(label="Nombre Nuevo Jugador", expand=True)
        lista_db_ui = ft.Column()

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

        def btn_borrar_db_click(e):
            borrar_jugador_db(e.control.data)
            refrescar_lista_db()

        refrescar_lista_db() 

        dlg_gestion = ft.AlertDialog(
            title=ft.Text("Base de Datos Jugadores"),
            content=ft.Container(
                width=300, height=400,
                content=ft.Column([
                    ft.Row([txt_nuevo_pj, ft.IconButton(icon="save", on_click=btn_agregar_db_click)]),
                    ft.Divider(),
                    ft.Text("Jugadores Guardados:", size=12, italic=True),
                    ft.Column(controls=lista_db_ui.controls, scroll="auto", expand=True) 
                ])
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dlg_gestion))]
        )
        page.open(dlg_gestion)

    # 3. Diálogo para EDITAR ESTADO
    def abrir_editor_estado(e):
        combatiente = e.control.data 
        
        txt_edit_estado = ft.TextField(label="Estado", value=combatiente['estado'])
        txt_edit_turnos = ft.TextField(label="Turnos", value=str(combatiente['turnos']), keyboard_type=ft.KeyboardType.NUMBER, width=100)
        
        def guardar_cambios_estado(e):
            try:
                combatiente['estado'] = txt_edit_estado.value
                combatiente['turnos'] = int(txt_edit_turnos.value) if txt_edit_turnos.value else 0
                renderizar_lista()
                page.close(dlg_edit)
            except ValueError:
                txt_edit_turnos.error_text = "Numero"
                page.update()
        
        def quitar_estado_manual(e):
            combatiente['estado'] = ""
            combatiente['turnos'] = 0
            renderizar_lista()
            page.close(dlg_edit)

        dlg_edit = ft.AlertDialog(
            title=ft.Text(f"Editar: {combatiente['nombre']}"),
            content=ft.Column([
                ft.Text("Agrega o quita estados en tiempo real."),
                txt_edit_estado,
                txt_edit_turnos
            ], height=200, tight=True),
            actions=[
                ft.TextButton("Limpiar Estado", on_click=quitar_estado_manual, style=ft.ButtonStyle(color="red")),
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_edit)),
                ft.ElevatedButton("Guardar", on_click=guardar_cambios_estado)
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        page.open(dlg_edit)


    # --- RENDERIZADO PRINCIPAL ---
    def renderizar_lista():
        lista_visual.controls.clear()

        for i, c in enumerate(combatientes):
            es_enemigo = c['es_enemigo']
            es_turno = (i == turno_actual)
            
            # Estilos visuales con TEXTO para evitar errores
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
                        ft.Text(f"{c['estado']} ({c['turnos']} turnos)", size=12, color="yellow", expand=True),
                    ])
                )

            # --- Tarjeta ---
            card = ft.Container(
                bgcolor=bg_color, border=borde, border_radius=10, padding=10,
                animate_opacity=300,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(name="skull" if es_enemigo else "shield", color="white70"),
                        ft.Column([
                            ft.Text(c['nombre'], weight="bold", size=16),
                            ft.Text(f"Init: {c['init']}", size=12, italic=True),
                        ], expand=True),
                        # Botón Editar
                        ft.IconButton(icon="edit", icon_color="blue200", tooltip="Editar Estado", data=c, on_click=abrir_editor_estado),
                        # Botón Borrar
                        ft.IconButton(icon="close", icon_color="grey500", tooltip="Eliminar del combate", data=c, on_click=eliminar_combatiente)
                    ]),
                    fila_estado
                ])
            )
            lista_visual.controls.append(card)
        page.update()

    # --- LOGICA DE BOTONES ---

    def agregar_manual_click(e):
        if not txt_nombre.value or not txt_iniciativa.value: return
        try:
            val = int(txt_iniciativa.value)
            nuevo = {'nombre': txt_nombre.value, 'init': val, 'es_enemigo': switch_enemigo.value, 'estado': "", 'turnos': 0}
            combatientes.append(nuevo)
            combatientes.sort(key=lambda x: x['init'], reverse=True)
            txt_nombre.value = ""
            txt_iniciativa.value = ""
            txt_nombre.focus()
            renderizar_lista()
        except ValueError: pass

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
        ft.ElevatedButton("Gestionar Jugadores", icon="person_add", on_click=abrir_gestion_jugadores, height=30),
        ft.ElevatedButton("Cargar Party", icon="group_add", on_click=abrir_dialogo_cargar_party, bgcolor="green900", color="white", height=30),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    inputs_rapidos = ft.Row([
        txt_nombre, 
        txt_iniciativa, 
        ft.IconButton(icon="add_circle", icon_color="red", icon_size=30, on_click=agregar_manual_click, tooltip="Agregar manual")
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.add(
        ft.Text("⚔️ DM Tracker", size=20, weight="bold", text_align="center"),
        barra_superior,
        ft.Divider(),
        ft.Text("Agregar Enemigo / Manual:", size=12, italic=True),
        inputs_rapidos,
        switch_enemigo,
        ft.Divider(),
        lista_visual
    )
    
    page.floating_action_button = ft.FloatingActionButton(text="Siguiente", icon="play_arrow", on_click=siguiente_turno)
    
    # CORRECCIÓN AQUÍ: Usamos "grey900" (String) en vez de ft.colors.SURFACE_VARIANT
    page.appbar = ft.AppBar(
        leading=ft.Icon("dnd_games"),
        title=ft.Text("Iniciativa"),
        bgcolor="grey900", 
        actions=[ft.IconButton(icon="delete_forever", tooltip="Limpiar Combate", on_click=limpiar_todo)]
    )

ft.app(target=main, view=ft.WEB_BROWSER, port=8080)