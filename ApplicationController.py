import pandas as pd
import os
import logging
from cryptography.fernet import Fernet
import json

class ApplicationController:
    def __init__(self, encryption_key, storage_path="utils/data/"):
        """
        Controlador da aplicação para gerenciar integração de dados e fluxo geral.
        :param encryption_key: Chave de criptografia para os dados.
        :param storage_path: Caminho de armazenamento dos dados processados.
        """
        self.encryption_key = encryption_key
        self.storage_path = storage_path
        self.excel_importer = ExcelImporter(encryption_key, storage_path)
        os.makedirs(storage_path, exist_ok=True)

    def import_excel_data(self, file_path, data_type, selected_date):
        """
        Importa dados de um arquivo Excel e gerencia o fluxo do processo.
        :param file_path: Caminho do arquivo Excel.
        :param data_type: Tipo de dado (custos, receitas, programados).
        :param selected_date: Data selecionada (yyyy-MM).
        """
        try:
            data = self.excel_importer.import_financial_data(file_path, data_type, selected_date)
            if data is not None:
                logging.info(f"Dados de {data_type} importados com sucesso para {selected_date}.")
                return True
            else:
                logging.error("Erro ao importar dados.")
                return False
        except Exception as e:
            logging.error(f"Erro no processo de importação: {e}")
            return False

    def analyze_financial_data(self, start_date=None, end_date=None):
        """
        Analisa os dados financeiros dentro de um intervalo de tempo.
        :param start_date: Data inicial no formato yyyy-MM.
        :param end_date: Data final no formato yyyy-MM.
        """
        try:
            # Iterar sobre arquivos na pasta de armazenamento
            all_files = [f for f in os.listdir(self.storage_path) if f.endswith(".json")]
            relevant_files = []

            for file_name in all_files:
                file_date = file_name.split("_")[1].replace(".json", "")
                if (not start_date or file_date >= start_date) and (not end_date or file_date <= end_date):
                    relevant_files.append(file_name)

            combined_data = pd.DataFrame()

            for file_name in relevant_files:
                file_path = os.path.join(self.storage_path, file_name)
                data = self.load_encrypted_data(file_path)
                combined_data = pd.concat([combined_data, data], ignore_index=True)

            # Realizar análises específicas (crescimento de custos/receitas)
            growth_analysis = self.calculate_growth_analysis(combined_data)
            return growth_analysis
        except Exception as e:
            logging.error(f"Erro ao analisar dados financeiros: {e}")
            return None

    def load_encrypted_data(self, file_path):
        """
        Carrega e descriptografa dados de um arquivo.
        :param file_path: Caminho do arquivo criptografado.
        """
        try:
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)["data"]
                fernet = Fernet(self.encryption_key)
                decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
                return pd.read_json(decrypted_data)
        except Exception as e:
            logging.error(f"Erro ao carregar dados do arquivo {file_path}: {e}")
            return None

    def calculate_growth_analysis(self, data):
        """
        Calcula índices de crescimento baseados nos dados fornecidos.
        :param data: DataFrame combinado de custos e receitas.
        """
        try:
            if data.empty:
                logging.warning("Nenhum dado disponível para análise.")
                return None

            grouped = data.groupby(["Categoria", "Tipo"])["Valor"].sum().reset_index()
            growth_indices = grouped.copy()
            growth_indices["Crescimento"] = grouped["Valor"].pct_change().fillna(0) * 100
            return growth_indices
        except Exception as e:
            logging.error(f"Erro ao calcular análise de crescimento: {e}")
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

class ExcelImporter:
    def __init__(self, encryption_key, storage_path="utils/data/"):
        self.encryption_key = encryption_key
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def import_financial_data(self, file_path, data_type, selected_date):
        """
        Similar ao anterior, com validações e criptografia.
        """
        # Placeholder para manter consistência
        pass

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = Fernet.generate_key()
    controller = ApplicationController(encryption_key)
    success = controller.import_excel_data("caminho/para/arquivo.xlsx", "custos", "2023-05")
    if success:
        analysis = controller.analyze_financial_data()
        print(analysis)

