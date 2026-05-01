from playwright.sync_api import sync_playwright
import threading
import os
from dotenv import load_dotenv
import pandas as pd
import random
import time

load_dotenv("credentials.env")

class PosSession:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.browser = None
        self.page = None
        self.context = None
        self.partners = None
        self.products = None # Es buena práctica inicializarlo en None

    def _launch_browser(self):
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        return p
    
    def get_products(self):
        df = pd.read_csv("data/products.csv")
        self.products = df.to_dict(orient="records")
        print(self.products)
        print(f"Session {self.instance_id} loaded products: {len(self.products)} items")

    def get_partners(self):
        df = pd.read_csv("data/partners.csv")
        self.partners = df.to_dict(orient="records")
        print(self.partners)
        print(f"Session {self.instance_id} loaded partners: {len(self.partners)} items")

    def _login_and_navigate_to_pos(self):
        playwright = None
        try:
            print(f"Starting instance {self.instance_id} login process.")
            playwright = self._launch_browser()

            self.page.goto("http://localhost:8069/web/login?redirect=%2Fodoo%3F")
            self.page.wait_for_load_state("networkidle")
            
            username = os.getenv("username")
            password = os.getenv("password")
            
            self.page.fill('input[name="login"]', username)
            self.page.fill('input[name="password"]', password)
            
            with self.page.expect_navigation():
                self.page.click('button[type="submit"]')

            self.page.goto("http://localhost:8069/odoo/point-of-sale")
            return True
        except Exception as e:
            print(f"Error during login/navigation for instance {self.instance_id}: {e}")
            return False

    def _open_specific_pos_record(self):
        try:
            kanban_records = self.page.locator("article.o_kanban_record")
            
            # Wait for at least one record to be visible
            kanban_records.first.wait_for(state="visible", timeout=30000)

            index_to_click = self.instance_id - 1 
            specific_record = kanban_records.nth(index_to_click)
  
            btn_open_session = specific_record.locator("button.btn-primary")
            
            print(f"Session {self.instance_id} clicking POS button...")
            
            with self.page.expect_navigation():
                btn_open_session.click()

            print(f"Session {self.instance_id} opened specific POS record successfully.")
            self.page.wait_for_timeout(5000)
            return True
        except Exception as e:
            print(f"Error opening specific POS record for instance {self.instance_id}: {e}")
            return False
        
    def _get_sale_orders(self):
            total_lines_1 = [1, 2, 3, 4, 5]
            total_lines_2 = [5, 10, 15, 20, 25]
            total_lines_choice = random.choice([total_lines_1, total_lines_2])
            num_lines = random.choice(total_lines_choice)
            
            # Localizador del input de búsqueda guardado en una variable para reusarlo
            search_input = self.page.locator('input[placeholder="Search products..."]')
            
            # 1. Iterar sobre los productos
            for line in range(num_lines):
                product = random.choice(self.products)["name"]
                print(f"--- Procesando Producto: {product} ---")
                
                try:
                    search_input.fill(product)
                    print("Búsqueda ejecutada.")
                    self.page.wait_for_timeout(1000) 
                except Exception as e:
                    print(f"Error al escribir el producto {product}: {e}")
                    continue 
                
                try:

                    first_result_locator = self.page.locator('div.product-list:not(.category-list) article.product').first

                    first_result_locator.click()
                    print("Clic realizado exitosamente en el primer resultado de la lista de productos.")
                    
                    search_input.clear()

                    print("Input de búsqueda limpiado.")

                except Exception as e:
                    print(f"ERROR al intentar hacer clic: {e}. Revisar el selector.")
                    # Es buena práctica limpiar el input incluso si falló el clic para que no afecte el siguiente ciclo
                    search_input.clear() 
                    pass

    def _get_partner_sale_order(self):
        selector = 'button.set-partner:has-text("Customer")'

        try:
            customer_name = random.choice(self.partners)["name"]
            
            while customer_name in ["Administrador", "My Company"]:
                customer_name = random.choice(self.partners)["name"]
            
            print(f"--- Procesando Cliente: {customer_name} ---")

            boton_customer = self.page.locator(selector)
            boton_customer.click()

            self.page.wait_for_timeout(1000)

            inside_partner = self.page.locator('input[placeholder="Search Customers..."]')

            inside_partner.fill(customer_name)
            print("Búsqueda de cliente ejecutada.")
            self.page.wait_for_timeout(1000)

            self.page.locator('tbody tr.partner-line').first.click()

            print("Clic realizado exitosamente en el primer resultado de la lista de clientes.")
            self.page.wait_for_timeout(1000)

        except Exception as e:
            print(f"Error al buscar cliente {customer_name}: {e}")

    def _payment_process(self):
            selector_pay = '.button.pay:has-text("Payment")' # Ajusta la clase si es necesario
            
            try:
                pay_button = self.page.locator(selector_pay)
                # Espera dinámica para el botón principal de pago
                pay_button.wait_for(state="visible", timeout=10000)
                pay_button.click()
                print("Clic realizado exitosamente en el botón de pago.")

                payment_methods_list = ['Nequi', 'Cash', 'Card', 'Rappi']
                payment_method = random.choice(payment_methods_list)
                
                # ⚡ CORRECCIÓN: Buscamos dentro de la lista de pagos, sin importar si es div o button
                # Odoo suele usar la clase .paymentmethod o .paymentmethods
                payment_method_locator = self.page.locator('.paymentmethods .paymentmethod').filter(has_text=payment_method).first
                
                # Esperar a que los métodos de pago carguen en pantalla
                payment_method_locator.wait_for(state="visible", timeout=10000)
                payment_method_locator.click()
                
                print(f"Clic realizado exitosamente en el método de pago: {payment_method}.")
                
            except Exception as e:
                print(f"Error en el proceso de pago: {e}")

    def _validation_order(self):
            selector_validate = 'button.validation-button:has-text("Validate")'

            try:
                validation_button = self.page.locator(selector_validate)
                
                # ⚡ CORRECCIÓN: Espera dinámica. Se ejecutará justo cuando el botón exista y sea visible.
                # Timeout de 15 segundos máximo.
                validation_button.wait_for(state="visible", timeout=15000)
                validation_button.click()
                print("Clic realizado exitosamente en el botón de validar.")

            except Exception as e:
                print(f"Error al hacer clic en el botón de validar: {e}")

            try:
                new_order_selector = 'button.validation:has-text("New Order")'
                new_order_button = self.page.locator(new_order_selector)
                
                # ⚡ CORRECCIÓN: Espera dinámica para el botón de Nueva Orden
                new_order_button.wait_for(state="visible", timeout=15000)
                new_order_button.click()
                print("Clic realizado exitosamente en el botón de nueva orden.")

            except Exception as e:
                print(f"Error al hacer clic en el botón de nueva orden: {e}")

    def _open_register_button(self):
        # Using a selector that targets the button containing the specific text, 
        # which is more reliable than matching only classes.
        selector = 'button.button.btn.btn-lg.btn-primary:has-text("Open Register")'
        
        try:
            open_register_button = self.page.locator(selector)
            
            print(f"Session {self.instance_id} attempting to click 'Open Register'...")
            
            # Wait for the button to be visible before clicking
            open_register_button.wait_for(state="visible", timeout=15000)
            
            with self.page.expect_navigation():
                open_register_button.click()
            
            print(f"Session {self.instance_id} clicked Open Register button successfully.")
            
            # Keep waiting longer for the expected activity in the new view
            self.page.wait_for_timeout(25000)
            return True
        except Exception as e:
            print(f"Error in instance {self.instance_id}: {e}")

    def _end_session(self):
            # Tip: Asegúrate de que no te falte un punto aquí si 'o-dropdown-item' es una clase -> '.o-dropdown-item'
            menu_selector = 'button.dropdown-toggle'
            try:
                menu_button = self.page.locator(menu_selector)
                menu_button.click()
                self.page.wait_for_timeout(1000)

                # Corregido con el punto inicial asumiendo que es una clase
                close_session_selector = '.o-dropdown-item:has-text("Close Register")' 
                close_session_button = self.page.locator(close_session_selector)
                close_session_button.wait_for(state="visible", timeout=10000)
                close_session_button.click()

                amount_locator = self.page.locator('div:has(span:text-is("Cash")) > span:nth-child(2)')
                amount_locator.wait_for(state="visible", timeout=5000)
                
                raw_text = amount_locator.inner_text()
                clean_text = raw_text.replace('$', '').replace('\xa0', '').strip()
                print(f"Monto a cuadrar: {clean_text}")
                
                cash_input_selector = 'div.mb-3:has(label:text-is("Cash Count")) input'
                cash_input = self.page.locator(cash_input_selector)
                
                cash_input.wait_for(state="visible", timeout=5000)
                
                cash_input.click()
                cash_input.fill(clean_text)
                
                cash_input.press('Tab')
                self.page.wait_for_timeout(5000)
                print("Monto ingresado en el input de Cash Count.")
                
                final_close_button = self.page.locator('button:has-text("Close Register")')
                final_close_button.wait_for(state="visible", timeout=5000)
                final_close_button.click()

                backen_selector = 'button:has-text("Backend")'
                backen_button = self.page.locator(backen_selector)
                backen_button.wait_for(state="visible", timeout=10000)
                backen_button.click()
                
                print(f"Session {self.instance_id} closed register successfully.")

            except Exception as e:
                print(f"Error closing register for instance {self.instance_id}: {e}")


    def _perform_session_tasks(self):
        print(f"--- Starting comprehensive task flow for instance {self.instance_id} ---")
        
        if not self._login_and_navigate_to_pos():
            return

        if not self._open_specific_pos_record():
            return
            
        open_register_button = self.page.locator('button.button.btn.btn-lg.btn-primary:has-text("Open Register")')

        self._open_register_button()

        minutes = 1
        total_seg = minutes * 60

        final_time = time.time() + total_seg

        print(f"El bucle iniciará ahora y durará {minutes} minutos...")

        while time.time() < final_time:

            self._get_sale_orders()

            self._get_partner_sale_order()

            self._payment_process()

            self._validation_order()

            print("Ejecutando proceso...")

            time.sleep(5)
        
        self._end_session()
        self._close()
            
        print(f"--- Instance {self.instance_id} task flow completed. ---")


    def _close(self):
        if self.browser:
            self.browser.close()
        print(f"Closed instance {self.instance_id}")


def run_concurrent_sessions(num_instances=4):
    threads = []
    sessions = []
    
    for i in range(num_instances):
        session = PosSession(i + 1)
        sessions.append(session)
        session.get_products()
        session.get_partners()
        t = threading.Thread(target=session._perform_session_tasks)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
    
    print("All instances completed!")

if __name__ == "__main__":
    run_concurrent_sessions(4)