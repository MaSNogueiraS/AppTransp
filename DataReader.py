import os
import logging
import json
import pandas as pd
from cryptography.fernet import Fernet
from datetime import datetime

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Classe para leitura e descriptografia dos dados
class DataReader:
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key
        self.storage_path = "utils/data/"
        self.custos_path = os.path.join(self.storage_path, "custos/")
        self.receitas_path = os.path.join(self.storage_path, "receitas/")
        self.programados_path = os.path.join(self.storage_path, "programados/")

        # Criar subpastas, se não existirem
        os.makedirs(self.custos_path, exist_ok=True)
        os.makedirs(self.receitas_path, exist_ok=True)
        os.makedirs(self.programados_path, exist_ok=True)

    def fetch_data(self, start_date: str, end_date: str, data_type: str = "ambos") -> pd.DataFrame:
        try:
            # Converter as datas para o formato correto
            start_date = datetime.strptime(start_date, '%Y-%m')
            end_date = datetime.strptime(end_date, '%Y-%m')

            # Determinar os caminhos relevantes
            paths = []
            if data_type in ["custos", "ambos"]:
                paths.append(self.custos_path)
            if data_type in ["receitas", "ambos"]:
                paths.append(self.receitas_path)
            if data_type in ["programados", "ambos"]:
                paths.append(self.programados_path)

            all_data = []

            for path in paths:
                if not os.path.exists(path):
                    logging.warning(f"Caminho não encontrado: {path}")
                    continue

                # Iterar sobre os arquivos no diretório
                for file_name in os.listdir(path):
                    # Extrair o mês e ano do nome do arquivo
                    if file_name.endswith('.json'):
                        file_date = datetime.strptime(file_name.split('_')[0], '%Y_%m')

                        # Verificar se o arquivo está no intervalo desejado
                        if start_date <= file_date <= end_date:
                            file_path = os.path.join(path, file_name)
                            data = self._read_and_decrypt_file(file_path)
                            if data is not None:
                                all_data.append(data)

            if not all_data:
                logging.info("Nenhum dado encontrado no intervalo especificado.")
                return pd.DataFrame()

            # Combinar todos os dados em um único DataFrame
            combined_data = pd.concat(all_data, ignore_index=True)
            return combined_data

        except Exception as e:
            logging.error(f"Erro ao buscar dados: {e}")
            return pd.DataFrame()

    def _read_and_decrypt_file(self, file_path: str) -> pd.DataFrame:
        try:
            # Carregar o arquivo JSON criptografado
            with open(file_path, 'r') as file:
                encrypted_content = json.load(file)["data"]

            # Descriptografar o conteúdo
            fernet = Fernet(self.encryption_key)
            decrypted_content = fernet.decrypt(encrypted_content.encode()).decode()

            # Converter JSON para DataFrame
            data = pd.read_json(decrypted_content, orient='records')
            logging.info(f"Dados descriptografados com sucesso de {file_path}.")
            return data

        except Exception as e:
            logging.error(f"Erro ao descriptografar o arquivo {file_path}: {e}")
            return None

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = b'kMFeIcTPHnVRP1XsZ3qBLRMG6qL0JH8sWuE1yN9ybXU='
    data_reader = DataReader(encryption_key)

    # Exemplo: Buscar dados de janeiro e fevereiro de 2024 para ambos os tipos
    data = data_reader.fetch_data("2024-01", "2024-02", data_type="ambos")
    if not data.empty:
        print(data.head())
    else:
        print("Nenhum dado encontrado.")
