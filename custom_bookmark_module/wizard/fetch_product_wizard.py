from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

import base64
import requests
import logging

_logger = logging.getLogger(__name__)

class ProductFetchWizard(models.TransientModel):
    _name = 'product.fetch.wizard'
    _description = 'Fetch Product Data from API'

    search_product_name = fields.Char(string="Search Product", required=True)
    title = fields.Char(string="Book Title")
    raison_sociale = fields.Char(string="Distributor")
    publisher = fields.Char(string="Publisher")
    auth_last_name = fields.Char(string="Author's Last Name")
    auth_name = fields.Char(string="Author's First Name")
    eans = fields.Char(string="EANs")
    price = fields.Float(string="Price")
    flag_scolaire = fields.Boolean(string="Flag Scolaire")
    cover_image = fields.Image(string="Cover Image")


    def get_access_token(self):
        """ Authenticate and get access token """
        url = "https://login.electre-ng-horsprod.com/auth/realms/electre/protocol/openid-connect/token"
        payload = {
            'grant_type': 'password',
            'client_id': 'api-client',
            'username': 'api-stephan-gestion',
            'password': 'TeRL7a3RrcLQKZedJmQXLOFXA0w55cQm',
            'scope': 'roles'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            _logger.info("Access token received successfully")
            return token_data.get("access_token")
        except requests.exceptions.RequestException as e:
            _logger.error("Error getting access token: %s", e)
            return None


    def fetch_product_data(self):
        """ Fetch product details from API and show preview """
        self.ensure_one()

        token = self.get_access_token()
        if not token:
            raise exceptions.UserError("Failed to authenticate with API.")

        api_url = f"https://api.demo.electre-ng-horsprod.com/notices/ean/{self.search_product_name}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            product_data = response.json()
            # print("result , ",product_data)
            if not product_data or 'notices' not in product_data:
                raise exceptions.UserError("No product found in the API!")

            product_info = product_data['notices'][0]
            # Update the wizard fields with fetched product info
            self.title = product_info.get('titre', 'Unknown Title')
            self.raison_sociale = product_info.get('distributeur', {}).get('raisonSociale', 'Unknown Distributor')
            self.publisher = product_info.get('editeurs', [{}])[0].get('formeBibEditeur', 'Unknown Publisher')
            if product_info.get('auteursPrincipaux'):
                self.auth_last_name = product_info['auteursPrincipaux'][0].get('nom', 'Unknown Last Name')
                self.auth_name = product_info['auteursPrincipaux'][0].get('prenom', 'Unknown First Name')
            self.eans = ', '.join(product_info.get('eans', []))
            self.price = product_info.get('prix', {}).get('ttc', 0.0)
            self.flag_scolaire = product_info.get('flagScolaire', False)
            # self.imagette_couverture = product_info.get('imagetteCouverture', '')
            # Handle image
            image_url = product_info.get('imagetteCouverture', '')
            if image_url:
                image_data = requests.get(image_url).content
                self.cover_image = base64.b64encode(image_data)

        except requests.exceptions.RequestException as e:
                _logger.error("API request failed: %s", e)
                raise exceptions.UserError(f"Error fetching data from API: {e}")

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.fetch.wizard',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'res_id': self.id,
        }

    def create_product(self):
        # Create a new product based on the fields in the wizard
        product_vals = {
            'name': self.title,
            'default_code': self.eans,
            'list_price': self.price,
            # 'type': 'product',  # Adjust according to your needs
            # 'flag_scolaire': self.flagScolaire,  # Assuming you have a custom field
            'image_1920': self.cover_image,
        }
        if self.title:
            existing_product = self.env['product.product'].search([('default_code', '=', self.eans)], limit=1)
            if existing_product:
                raise UserError(f"A product with EAN {self.eans} already exists: {existing_product.display_name}")

            product = self.env['product.product'].create(product_vals)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'view_mode': 'form',
                'res_id': product.id,
                'target': 'current',  # Opens in the same window
            }
        else:
            raise UserError("No product data was found from the API. Please check the API response.")












