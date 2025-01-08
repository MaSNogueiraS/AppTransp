import logging
from excel_importer import ExcelImporter
from financial_processor import FinancialProcessor
from security_monitor import SecurityMonitor
import os

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ApplicationController:
    def __init__(self, encryption_key, storage_path="utils/data/"):
        """
        Controlador principal para gerenciar todos os módulos do sistema.
        :param encryption_key: Chave de criptografia para dados.
        :param storage_path: Caminho para armazenamento de dados.
        """
        self.encryption_key = encryption_key
        self.storage_path = storage_path

        # Inicializar módulos
        self.excel_importer = ExcelImporter(encryption_key, storage_path)
        self.processor = FinancialProcessor()
        self.security_monitor = SecurityMonitor(data_paths=[
            os.path.join(storage_path, "custos"),
            os.path.join(storage_path, "receitas"),
            os.path.join(storage_path, "programados")
        ])

    def import_data(self, file_path, data_type):
        """
        Importa dados de um arquivo Excel para o sistema.
        :param file_path: Caminho do arquivo Excel.
        :param data_type: Tipo de dado a ser importado (custos, receitas, programados).
        """
        try:
            logging.info(f"Importando dados do arquivo: {file_path}")
            data = self.excel_importer.import_financial_data(file_path, data_type)
            if data is not None:
                logging.info(f"Dados de {data_type} importados com sucesso.")
                return True
            else:
                logging.warning(f"Falha ao importar dados de {data_type}.")
                return False
        except Exception as e:
            logging.error(f"Erro ao importar dados: {e}")
            return False

    def analyze_financials(self):
        """
        Realiza análise financeira com os dados armazenados.
        """
        try:
            custos_path = os.path.join(self.storage_path, "custos_data.json")
            receitas_path = os.path.join(self.storage_path, "receitas_data.json")

            custos_data = self.excel_importer.load_encrypted_data(custos_path)
            receitas_data = self.excel_importer.load_encrypted_data(receitas_path)

            growth_costs = self.processor.calculate_growth_indices(custos_data, 'custos')
            growth_revenues = self.processor.calculate_growth_indices(receitas_data, 'receitas')

            return {
                "Crescimento Custos": growth_costs,
                "Crescimento Receitas": growth_revenues
            }
        except Exception as e:
            logging.error(f"Erro ao realizar análise financeira: {e}")
            return None

    def clear_all_data(self):
        """
        Limpa todos os dados armazenados no sistema.
        """
        try:
            for file in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logging.info("Todos os dados foram limpos com sucesso.")
            return True
        except Exception as e:
            logging.error(f"Erro ao limpar dados: {e}")
            return False

    def start_security_monitor(self):
        """
        Inicia o monitoramento de segurança para proteger os dados.
        """
        self.security_monitor.monitor()

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = b'kMFeIcTPHnVRP1XsZ3qBLRMG6qL0JH8sWuE1yN9ybXU='
    app_controller = ApplicationController(encryption_key)

    # Testar importação de dados
    success = app_controller.import_data("caminho/para/arquivo.xlsx", "custos")
    if success:
        print("Dados importados com sucesso.")
    else:
        print("Falha na importação de dados.")

    # Testar análise financeira
    analysis = app_controller.analyze_financials()
    if analysis:
        print("Análise financeira realizada com sucesso:")
        print(analysis)

    # Testar limpeza de dados
    if app_controller.clear_all_data():
        print("Todos os dados foram limpos com sucesso.")
    else:
        print("Falha ao limpar os dados.")
