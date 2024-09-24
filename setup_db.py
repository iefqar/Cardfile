from data.database.setup import init_db
from data.repositories.usuario_repository import UsuarioRepository
from data.models.usuario import Usuario
from data.database.connection import engine
from config import Config

def initialize_db():
    # Inicializar la base de datos
    init_db()

    # Crear un repositorio de usuarios
    usuario_repo = UsuarioRepository()

    try:
        config = Config()

        # Agregar un nuevo usuario
        nuevo_usuario = Usuario(nombre=config.get("database.Init_Data.Username"), email=config.get("database.Init_Data.Email"), contraseña=config.get("database.Init_Data.Password"))
        usuario_repo.add_usuario(nuevo_usuario)
        print("Nuevo usuario agregado exitosamente.")

        # Obtener todos los usuarios
        usuarios = usuario_repo.get_all_usuarios()
        for usuario in usuarios:
            print(f"ID: {usuario.id}, Nombre: {usuario.nombre}, Email: {usuario.email}, Activo: {usuario.is_active}")
    
    except Exception as e:
        usuario_repo.session.rollback()
        print(f"Error al agregar el usuario o recuperar la lista de usuarios: {e}")

    finally:
        # Cerrar la sesión del repositorio
        usuario_repo.close()

if __name__ == "__main__":
    initialize_db()