import flet as ft
from data.database.connection import get_session
from data.models.ficha import Ficha
from config.config import Config

def recycle_view(page: ft.Page):
    # Inicializar Config
    config = Config()
    selected_ficha = None

    def load_inactive_fichas():
        """Carga las fichas inactivas del usuario"""
        session = get_session()
        try:
            user_id = page.client_storage.get("user_id")
            fichas = session.query(Ficha).filter(
                Ficha.usuario_id == user_id,
                Ficha.is_active == False
            ).all()
            
            # Crear los controles antes de asignarlos
            controls = [
                ft.ListTile(
                    leading=ft.Icon(ft.icons.DELETE_OUTLINE),
                    title=ft.Text(ficha.title),
                    on_click=lambda e, f=ficha: select_ficha(f)
                ) for ficha in fichas
            ]
            
            # Asignar los controles al ListView
            if fichas_list.controls is not None:  # Verificar que el ListView esté inicializado
                fichas_list.controls = controls
                fichas_list.update()
                page.update()
        except Exception as e:
            print(f"Error cargando fichas inactivas: {str(e)}")
        finally:
            session.close()

    def select_ficha(ficha):
        """Maneja la selección de una ficha"""
        nonlocal selected_ficha
        selected_ficha = ficha
        # Habilitar botones
        btn_restore.disabled = False
        btn_delete.disabled = False
        page.update()

    def restore_clicked(e):
        """Restaura la ficha seleccionada"""
        if not selected_ficha:
            return
        
        session = get_session()
        try:
            ficha = session.query(Ficha).filter(Ficha.id == selected_ficha.id).first()
            if ficha:
                ficha.is_active = True
                session.commit()
                load_inactive_fichas()
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(config.get_text("recycle.messages.restore_success")),
                        bgcolor=ft.colors.GREEN_400,
                        action="Ok"
                    )
                )
        except Exception as e:
            session.rollback()
            print(f"Error restaurando ficha: {str(e)}")
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(config.get_text("recycle.messages.restore_error")),
                    bgcolor=ft.colors.RED_400,
                    action="Ok"
                )
            )
        finally:
            session.close()

    def delete_clicked(e):
        """Elimina permanentemente la ficha"""
        if not selected_ficha:
            return

        def confirm_delete(e):
            if e.control.text == config.get_text("card.buttons.yes"):
                session = get_session()
                try:
                    ficha = session.query(Ficha).filter(Ficha.id == selected_ficha.id).first()
                    if ficha:
                        session.delete(ficha)
                        session.commit()
                        load_inactive_fichas()
                        page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(config.get_text("recycle.messages.delete_success")),
                                bgcolor=ft.colors.GREEN_400,
                                action="Ok"
                            )
                        )
                except Exception as e:
                    session.rollback()
                    print(f"Error eliminando ficha: {str(e)}")
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(config.get_text("recycle.messages.delete_error")),
                            bgcolor=ft.colors.RED_400,
                            action="Ok"
                        )
                    )
                finally:
                    session.close()
            
            dlg_modal.open = False
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(config.get_text("recycle.delete_confirmation.title")),
            content=ft.Text(config.get_text("recycle.delete_confirmation.message")),
            actions=[
                ft.TextButton(config.get_text("card.buttons.no"), on_click=confirm_delete),
                ft.TextButton(config.get_text("card.buttons.yes"), on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def cancel_clicked(e):
        page.go("/Card")

    # Lista de fichas
    fichas_list = ft.ListView(
        expand=1,
        spacing=10,
        padding=20,
        height=300
    )

    # Botones
    btn_cancel = ft.ElevatedButton(
        text=config.get_text("recycle.buttons.cancel"),
        width=120,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.BLUE,
        on_click=lambda e: page.go("/Card")
    )

    btn_restore = ft.ElevatedButton(
        text=config.get_text("recycle.buttons.restore"),
        width=120,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.GREEN,
        on_click=restore_clicked,
        disabled=True
    )

    btn_delete = ft.ElevatedButton(
        text=config.get_text("recycle.buttons.delete"),
        width=100,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.RED,
        on_click=delete_clicked,
        disabled=True
    )

    # Contenedor principal
    main_view = ft.Container(
        width=400,
        height=500,
        bgcolor=ft.colors.WHITE10,
        border=ft.border.all(2, ft.colors.BLUE_200),
        border_radius=15,
        padding=30,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.icons.RECYCLING, size=50, color=ft.colors.BLUE),
                ft.Text(
                    config.get_text("recycle.title"),
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                
                # Lista de fichas inactivas
                ft.Container(
                    content=fichas_list,
                    border=ft.border.all(2, ft.colors.BLUE_200),
                    border_radius=10,
                    padding=10,
                    expand=True
                ),
                
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                
                # Contenedor para los botones
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[btn_cancel, btn_restore, btn_delete],
                    ),
                ),
            ],
        ),
        alignment=ft.alignment.center,
    )

    # En lugar de cargar directamente, usar did_mount
    def on_view_mount():
        load_inactive_fichas()
    
    main_view.did_mount = on_view_mount
    
    return main_view

# Exportamos la función
__all__ = ['recycle_view']