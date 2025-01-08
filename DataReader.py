import os
import logging
import pandas as pd
from cryptography.fernet import Fernet
import json

class DataReader:
    def __init__(self, encryption_key, storage_path="utils/data/"):
        """
        Módulo para leitura e manipulação de dados armazenados.
        :param encryption_key: Chave de criptografia para os dados.
        :param storage_path: Caminho de armazenamento dos dados processados.
        """
        self.encryption_key = encryption_key
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def load_encrypted_data(self, file_path):
        """
        Carrega e descriptografa dados de um arquivo existente.
        :param file_path: Caminho do arquivo.
        """
        try:
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)["data"]
                fernet = Fernet(self.encryption_key)
                decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
                return pd.read_json(decrypted_data)
        except Exception as e:
            logging.error(f"Erro ao carregar dados do arquivo {file_path}: {e}")
            return pd.DataFrame()

    def read_data_by_date(self, data_type, start_date=None, end_date=None):
        """
        Lê dados de arquivos com base no tipo e intervalo de datas.
        :param data_type: Tipo de dado (custos, receitas, programados).
        :param start_date: Data inicial no formato "yyyy-MM".
        :param end_date: Data final no formato "yyyy-MM".
        :return: DataFrame combinado contendo os dados dentro do intervalo.
        """
        try:
            relevant_files = []
            all_files = os.listdir(self.storage_path)

            for file_name in all_files:
                if file_name.startswith(data_type):
                    file_date = file_name.split("_")[1].replace(".json", "")
                    if (not start_date or file_date >= start_date) and (not end_date or file_date <= end_date):
                        relevant_files.append(file_name)

            combined_data = pd.DataFrame()

            for file_name in relevant_files:
                file_path = os.path.join(self.storage_path, file_name)
                data = self.load_encrypted_data(file_path)
                combined_data = pd.concat([combined_data, data], ignore_index=True)

            return combined_data
        except Exception as e:
            logging.error(f"Erro ao ler dados por data: {e}")
            return pd.DataFrame()

    def analyze_data(self, combined_data):
        """
        Realiza análise básica nos dados combinados.
        :param combined_data: DataFrame contendo os dados combinados.
        :return: DataFrame com resultados agregados por categoria.
        """
        try:
            grouped = combined_data.groupby(["Categoria"])["Valor"].sum().reset_index()
            grouped = grouped.sort_values(by="Valor", ascending=False)
            return grouped
        except Exception as e:
            logging.error(f"Erro ao analisar dados: {e}")
            return pd.DataFrame()

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = Fernet.generate_key()
    reader = DataReader(encryption_key)

    # Exemplo de leitura de dados
    data = reader.read_data_by_date("custos", "2023-01", "2023-06")
    if not data.empty:
        analysis = reader.analyze_data(data)
        print(analysis)
    else:
        print("Nenhum dado disponível no intervalo selecionado.")
