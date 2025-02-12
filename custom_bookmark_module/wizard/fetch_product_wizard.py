from odoo import models, fields, api, exceptions
import requests
import logging

_logger = logging.getLogger(__name__)

class ProductFetchWizard(models.TransientModel):
    _name = 'product.fetch.wizard'
    _description = 'Fetch Product Data from API'

    search_product_name = fields.Char(string="Search Product", required=True)

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
        """ Fetch product details from API and create product if found """
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
            print("response",product_data)

            if not product_data:
                raise exceptions.UserError("No product found in the API!")

            product_info = product_data[0]  # Assuming API returns a list

            # Check if product already exists
            existing_product = self.env['product.template'].search([
                ('default_code', '=', product_info.get('sku', ''))
            ], limit=1)

            if existing_product:
                raise exceptions.UserError("This product already exists in the database.")

            # Create new product
            new_product = self.env['product.template'].create({
                'name': product_info.get('name', self.search_product_name),
                'default_code': product_info.get('sku', ''),
                'list_price': product_info.get('price', 0.0),
                'standard_price': product_info.get('cost', 0.0),
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'res_id': new_product.id,
                'view_mode': 'form',
                'target': 'current'
            }

        except requests.exceptions.RequestException as e:
            _logger.error("API request failed: %s", e)
            raise exceptions.UserError(f"Error fetching data from API: {e}")
