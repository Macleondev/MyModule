from odoo import models, fields, api
import requests # Importamos la librería 'requests' para hacer peticiones HTTP
import logging # Para registrar mensajes en el log de Odoo

_logger = logging.getLogger(__name__) # Inicializamos el logger

class MiApiConsumidor(models.Model):
    _name = 'mi.api.consumidor' # Nombre técnico de tu modelo
    _description = 'Registros de la API de prueba (JSONPlaceholder)'

    # Campos para almacenar los datos que obtendremos de la API
    api_id = fields.Integer(string="ID de la API", readonly=True, help="ID original del post en la API externa")
    user_id = fields.Integer(string="ID de Usuario (API)", readonly=True)
    title = fields.Char(string="Título del Post", required=True)
    body = fields.Text(string="Contenido del Post")
    fecha_consumo = fields.Datetime(string="Fecha de Consumo", default=fields.Datetime.now(), readonly=True)

    # --- Método para consumir la API ---
    @api.model
    def consumir_api_posts(self):
        """
        Consume la API de JSONPlaceholder para obtener posts y los guarda en Odoo.
        """
        url = "https://jsonplaceholder.typicode.com/posts" # URL de la API
        _logger.info(f"Intentando consumir API desde: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status() # Lanza una excepción si la respuesta no fue 2xx
            data = response.json() # Convierte la respuesta JSON en un objeto Python (lista de diccionarios)

            if data:
                _logger.info(f"API consumida exitosamente. Se encontraron {len(data)} posts.")
                # Recorre los datos y crea registros en Odoo
                for post in data:
                    # Buscamos si ya existe un registro con el mismo api_id para evitar duplicados
                    existing_post = self.search([('api_id', '=', post.get('id'))], limit=1)

                    if not existing_post:
                        self.create({
                            'api_id': post.get('id'),
                            'user_id': post.get('userId'),
                            'title': post.get('title'),
                            'body': post.get('body'),
                        })
                        _logger.info(f"Creado nuevo registro para post ID: {post.get('id')}")
                    else:
                        _logger.info(f"Post ID: {post.get('id')} ya existe. Se omite.")
                self.env.cr.commit() # Asegura que los cambios se guarden en la DB
                _logger.info("Proceso de consumo de API completado.")
            else:
                _logger.warning("La API devolvió una respuesta vacía.")

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error al consumir la API: {e}")
            # Puedes notificar al usuario en la UI si esto se llama desde un botón
            raise models.ValidationError(f"No se pudo conectar a la API: {e}")
        except ValueError as e: # Error al parsear JSON
            _logger.error(f"Error al parsear la respuesta JSON de la API: {e}")
            raise models.ValidationError(f"Error en el formato de datos de la API: {e}")
        except Exception as e:
            _logger.error(f"Ocurrió un error inesperado durante el consumo de la API: {e}")
            raise models.ValidationError(f"Error inesperado: {e}")

    # --- Acción para que un usuario pueda ejecutar el consumo desde la interfaz de Odoo ---
    def action_consumir_api_desde_ui(self):
        """
        Método que se puede llamar desde un botón en la UI para consumir la API.
        """
        self.consumir_api_posts()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Consumo de API',
                'message': 'Los datos de la API se han intentado consumir y guardar.',
                'sticky': False, # Notificación temporal
            }
        }