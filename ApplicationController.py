import logging
from ExcelImporter import ExcelImporter
from FinancialProcessor import FinancialProcessor
from SecurityMonitor import SecurityMonitor
from DatabaseConnector import DatabaseConnector

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ApplicationController:
    def __init__(self, encryption_key, excel_file_path):
        """
        Controlador da aplicação para gerenciar todos os módulos.
        :param encryption_key: Chave de criptografia para os dados.
        :param excel_file_path: Caminho do arquivo Excel para importação inicial.
        """
        self.encryption_key = encryption_key
        self.excel_file_path = excel_file_path

        # Inicializar módulos
        self.excel_importer = ExcelImporter(file_path=self.excel_file_path, encryption_key=self.encryption_key)
        self.processor = FinancialProcessor()
        self.db_connector = DatabaseConnector()
        self.security_monitor = SecurityMonitor(data_paths=[
            "utils/data/custos/",
            "utils/data/receitas/",
            "utils/data/programados/"
        ])

    def import_data(self, data_type, overwrite=False):
        """
        Importa dados do Excel e armazena no banco de dados.
        :param data_type: Tipo de dado a importar (custos, receitas, programados).
        :param overwrite: Determina se os dados existentes devem ser sobrescritos.
        """
        data = self.excel_importer.import_financial_data(data_type=data_type, overwrite=overwrite)
        if data is not None:
            self.db_connector.insert_data(data_type, data.to_dict(orient='records'))
            logging.info(f"Dados do tipo {data_type} importados e armazenados com sucesso.")

    def analyze_financials(self):
        """
        Realiza análises financeiras e retorna resultados.
        """
        all_costs = self.db_connector.fetch_data("custos")
        all_revenues = self.db_connector.fetch_data("receitas")
        costs_df = pd.DataFrame(all_costs)
        revenues_df = pd.DataFrame(all_revenues)

        # Índices de crescimento
        growth_costs = self.processor.calculate_growth_indices(costs_df, 'custos')
        growth_revenues = self.processor.calculate_growth_indices(revenues_df, 'receitas')

        # Análise orçamentária
        budget_analysis = self.processor.analyze_budget(costs_df)

        return {
            "Crescimento Custos": growth_costs,
            "Crescimento Receitas": growth_revenues,
            "Análise Orçamentária": budget_analysis
        }

    def forecast_cash_flow(self):
        """
        Realiza previsão de fluxo de caixa com base nos dados disponíveis.
        """
        all_data = self.db_connector.fetch_data("custos") + self.db_connector.fetch_data("receitas")
        combined_df = pd.DataFrame(all_data)
        return self.processor.forecast_cash_flow(combined_df)

    def start_security_monitor(self):
        """
        Inicia o monitoramento de segurança para proteger os dados.
        """
        self.security_monitor.monitor()

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = b'kMFeIcTPHnVRP1XsZ3qBLRMG6qL0JH8sWuE1yN9ybXU='
    excel_file_path = "caminho/para/arquivo.xlsx"

    app_controller = ApplicationController(encryption_key, excel_file_path)

    # Importar dados de custos
    app_controller.import_data(data_type="custos", overwrite=False)

    # Analisar dados financeiros
    financial_analysis = app_controller.analyze_financials()
    print(financial_analysis)

    # Prever fluxo de caixa
    cash_flow_forecast = app_controller.forecast_cash_flow()
    print(cash_flow_forecast)

    # Iniciar monitoramento de segurança
    app_controller.start_security_monitor()
