from odoo import models, fields

import json
import logging
import requests
import base64
import hashlib
from requests_oauthlib import OAuth1
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

CONSUMER_KEY = ''
PRIVATE_KEY = """
"""
API_URL = ''


class QuoteRequest(models.Model):

    ##Datos del Request
    _name = 'mi.api.quoterequest'
    _description = 'Solicitud de Cotización API'

    transaction_reference = fields.Char(string="Referencia de Transacción")
    sender_account_uri = fields.Char(string="Cuenta del Remitente")
    recipient_account_uri = fields.Char(string="Cuenta del Receptor")
    payment_amount = fields.Float(string="Monto")
    payment_currency = fields.Char(string="Moneda")
    payment_origination_country = fields.Char(string="País de Origen")
    payment_type = fields.Selection([
        ('P2P', 'P2P'),
        ('B2B', 'B2B')
    ], string="Tipo de Pago")
    receiver_currency = fields.Char(string="Moneda del Receptor")
    fees_included = fields.Boolean(string="Incluir Comisiones")

    ##Datos del response
    api_response = fields.Text(string="Respuesta de API")
    api_status_code = fields.Char(string="Código de Respuesta")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('success', 'Enviado Exitosamente'),
        ('error', 'Error al Enviar')
    ], default='draft', string="Estado")
    quote_id = fields.Char(string="ID de Cotización")
    expiration_date = fields.Datetime(string="Fecha de Expiración")

    def get_quote(self):
        for record in self:
            json_payload = {
                "quoterequest": {
                    "transaction_reference": record.transaction_reference,
                    "sender_account_uri": record.sender_account_uri,
                    "recipient_account_uri": record.recipient_account_uri,
                    "payment_amount": {
                        "amount": str(record.payment_amount),
                        "currency": record.payment_currency
                    },
                    "payment_origination_country": record.payment_origination_country,
                    "payment_type": record.payment_type,
                    "quote_type": {
                        "forward": {
                            "receiver_currency": record.receiver_currency,
                            "fees_included": str(record.fees_included).lower()
                        }
                    }
                }
            }

            try:

                body_json = json.dumps(json_payload)
                session = requests.Session()

                oauth = OAuth1(
                client_key=CONSUMER_KEY,
                rsa_key=PRIVATE_KEY,
                signature_method='RSA-SHA256',
                signature_type='auth_header'
                )

                req = requests.Request(
            'POST',
            API_URL,
            data=body,
            headers={'Content-Type': 'application/json'}
        )
                # Preparar request
                prepped = session.prepare_request(req)

        # Calcular hash SHA256 del cuerpo
                sha256 = hashlib.sha256()
                sha256.update(body.encode('utf-8'))
                body_hash = base64.b64encode(sha256.digest()).decode('utf-8')

        # Firmar la request
                prepped = oauth(prepped)

        # Modificar header Authorization para añadir oauth_body_hash
                prepped.headers['Authorization'] = prepped.headers['Authorization'].decode('utf-8') + f', oauth_body_hash="{body_hash}"'

        # Enviar request
                response = session.send(prepped)

                record.api_status_code = str(response.status_code)
                record.api_response = response.text

                
                if response.status_code == 200:
                    result = response.json()
                    proposal = result['quote']['proposals']['proposal'][0]

                    transaction_reference = result.get('quote', {}).get('transaction_reference')
                    payment_type = result.get('quote', {}).get('payment_type')

                    record.quote_id = proposal.get('id')
                    record.expiration_date = proposal.get('expiration_date')
                    record.state = 'success'

                    _logger.info("ID Cotización: %s", record.quote_id)
                    _logger.info("Fecha de Expiracion: %s", record.expiration_date)
                    _logger.info("Transaccion reference: %s", record.transaction_reference)
                    _logger.info("Tipo de Pago: %s", record.payment_type)
                    _logger.info("Estado: %s", record.state)

                else:
                    record.state = 'error'
                    _logger.warning(" Cotización fallida: %s", response.text)
            except Exception as e:
                record.state = 'error'
                record.api_response = str(e)
                record.api_status_code = 'Exception'
                _logger.exception("Excepción en get_quote(): %s", e)
