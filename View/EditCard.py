import flet as ft
from data.database.connection import get_session
from data.models.ficha import Ficha
from datetime import datetime

def edit_card_view(page: ft.Page):
    # Obtener la ficha seleccionada del almacenamiento
    selected_ficha = page.client_storage.get("selected_ficha")
    if not selected_ficha:
        return ft.Text("Error: No hay ficha seleccionada")

    def save_clicked(e):
        if not card_name.value:
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Por favor ingrese un nombre para la tarjeta"),
                    bgcolor=ft.colors.RED_400,
                    action="Ok"
                )
            )
            return
        
        session = get_session()
        try:
            # Buscar y actualizar la ficha
            ficha = session.query(Ficha).filter(Ficha.id == selected_ficha["id"]).first()
            if ficha:
                ficha.title = card_name.value.strip()
                ficha.updated_at = datetime.now()
                session.commit()
                
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Ficha actualizada exitosamente"),
                        bgcolor=ft.colors.GREEN_400,
                        action="Ok"
                    )
                )
                page.go("/Card")
            
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar ficha: {str(e)}")
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Error al actualizar la ficha"),
                    bgcolor=ft.colors.RED_400,
                    action="Ok"
                )
            )
        finally:
            session.close()

    def cancel_clicked(e):
        page.go("/Card")

    # Campo para el nombre de la tarjeta
    card_name = ft.TextField(
        label="Nombre de la Tarjeta",
        border_color=ft.colors.BLUE,
        width=300,
        text_align=ft.TextAlign.LEFT,
        on_submit=save_clicked,
        autofocus=True,
        value=selected_ficha["title"] if selected_ficha else ""
    )

    # Botones
    btn_save = ft.ElevatedButton(
        text="Actualizar",
        width=140,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.BLUE,
        on_click=save_clicked
    )

    btn_cancel = ft.ElevatedButton(
        text="Cancelar",
        width=140,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.RED,
        on_click=cancel_clicked
    )

    # Contenedor principal
    return ft.Container(
        width=400,
        height=300,
        border=ft.border.all(2, ft.colors.BLUE_200),
        border_radius=15,
        padding=30,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Text("Editar Tarjeta", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                card_name,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[btn_cancel, btn_save],
                ),
            ],
        ),
        alignment=ft.alignment.center,
    )

__all__ = ['edit_card_view'] 