import logging
import os
from DataReader import DataReader
from FinancialProcessor import FinancialProcessor
from SecurityMonitor import SecurityMonitor

class ApplicationController:
    def __init__(self, encryption_key, storage_path="utils/data/"):
        """
        Controlador principal para gerenciar módulos do sistema.
        :param encryption_key: Chave de criptografia para os dados.
        :param storage_path: Caminho de armazenamento dos dados processados.
        """
        self.encryption_key = encryption_key
        self.storage_path = storage_path

        # Inicializar módulos
        self.data_reader = DataReader(encryption_key, storage_path)
        self.processor = FinancialProcessor()
        self.security_monitor = SecurityMonitor(data_paths=[storage_path])

    def import_data(self, file_path, data_type, selected_date):
        """
        Importa dados de um arquivo Excel para o sistema.
        :param file_path: Caminho do arquivo Excel.
        :param data_type: Tipo de dado a ser importado (custos, receitas, programados).
        :param selected_date: Data selecionada no formato "yyyy-MM".
        """
        try:
            logging.info(f"Importando dados do arquivo: {file_path}")
            data = self.data_reader.import_financial_data(file_path, data_type, selected_date)
            if data is not None:
                logging.info(f"Dados de {data_type} importados com sucesso para {selected_date}.")
                return True
            else:
                logging.warning(f"Falha ao importar dados de {data_type}.")
                return False
        except Exception as e:
            logging.error(f"Erro ao importar dados: {e}")
            return False

    def analyze_financials(self, start_date=None, end_date=None):
        """
        Realiza análise financeira no intervalo especificado.
        :param start_date: Data inicial no formato "yyyy-MM".
        :param end_date: Data final no formato "yyyy-MM".
        :return: Resultados de análise financeira.
        """
        try:
            custos_data = self.data_reader.read_data_by_date("custos", start_date, end_date)
            receitas_data = self.data_reader.read_data_by_date("receitas", start_date, end_date)

            growth_costs = self.processor.calculate_growth_indices(custos_data, "custos")
            growth_revenues = self.processor.calculate_growth_indices(receitas_data, "receitas")

            return {
                "Crescimento Custos": growth_costs,
                "Crescimento Receitas": growth_revenues
            }
        except Exception as e:
            logging.error(f"Erro ao realizar análise financeira: {e}")
            return None

    def forecast_financials(self):
        """
        Realiza previsão financeira com base nos dados armazenados.
        :return: Previsões financeiras.
        """
        try:
            all_costs = self.data_reader.read_data_by_date("custos")
            all_revenues = self.data_reader.read_data_by_date("receitas")
            forecast = self.processor.forecast_cash_flow(all_costs, all_revenues)
            return forecast
        except Exception as e:
            logging.error(f"Erro ao realizar previsão financeira: {e}")
            return None

    def clear_all_data(self):
        """
        Remove todos os dados armazenados.
        """
        try:
            for file_name in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, file_name)
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
        try:
            self.security_monitor.monitor()
        except Exception as e:
            logging.error(f"Erro ao iniciar o monitoramento de segurança: {e}")

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = b"sua-chave-aqui"
    app_controller = ApplicationController(encryption_key)

    # Testar importação de dados
    success = app_controller.import_data("caminho/para/arquivo.xlsx", "custos", "2023-05")
    if success:
        print("Dados importados com sucesso.")
    else:
        print("Falha na importação de dados.")

    # Testar análise financeira
    analysis = app_controller.analyze_financials("2023-01", "2023-12")
    if analysis:
        print("Análise financeira realizada com sucesso:")
        print(analysis)

    # Testar previsão financeira
    forecast = app_controller.forecast_financials()
    if forecast:
        print("Previsão financeira realizada com sucesso:")
        print(forecast)

    # Testar limpeza de dados
    if app_controller.clear_all_data():
        print("Todos os dados foram limpos com sucesso.")
    else:
        print("Falha ao limpar os dados.")
