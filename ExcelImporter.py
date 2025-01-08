import pandas as pd
import os
import logging
from cryptography.fernet import Fernet
import json
from datetime import datetime
from collections import Counter

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Classe para importar e criptografar dados financeiros de arquivos Excel
class ExcelImporter:
    def __init__(self, file_path: str, encryption_key: str):
        self.file_path = file_path
        self.encryption_key = encryption_key
        self.storage_path = "utils/data/"

        # Criar subpastas para diferentes tipos de dados
        self.custos_path = os.path.join(self.storage_path, "custos/")
        self.receitas_path = os.path.join(self.storage_path, "receitas/")
        self.programados_path = os.path.join(self.storage_path, "programados/")
        os.makedirs(self.custos_path, exist_ok=True)
        os.makedirs(self.receitas_path, exist_ok=True)
        os.makedirs(self.programados_path, exist_ok=True)

    def import_financial_data(self, data_type: str, overwrite: bool = False):
        if not os.path.exists(self.file_path):
            logging.error(f"Arquivo Excel não encontrado: {self.file_path}")
            return None

        try:
            # Identificar o tipo de arquivo baseado na entrada do usuário
            excel_data = pd.ExcelFile(self.file_path)
            sheet_name = excel_data.sheet_names[0]  # Supondo que a primeira aba contém os dados
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)

            # Verificar o tipo e ajustar colunas
            if data_type == "custos" and {'Fornecedor - Nome', 'Pagamento', 'Valor'}.issubset(df.columns):
                logging.info("Planilha de custos detectada.")
                df = df[['Fornecedor - Nome', 'Pagamento', 'Valor']]
                df = df.rename(columns={
                    'Fornecedor - Nome': 'Fornecedor',
                    'Pagamento': 'Data Pagamento',
                    'Valor': 'Valor Pago'
                })
                self.validate_and_store_data(df, "custos", overwrite)

            elif data_type == "receitas" and {'Cliente - Nome', 'Pagamento', 'Valor'}.issubset(df.columns):
                logging.info("Planilha de receitas detectada.")
                df = df[['Cliente - Nome', 'Pagamento', 'Valor']]
                df = df.rename(columns={
                    'Cliente - Nome': 'Cliente',
                    'Pagamento': 'Data Pagamento',
                    'Valor': 'Valor Recebido'
                })
                self.validate_and_store_data(df, "receitas", overwrite)

            elif data_type == "programados" and {'Descrição', 'Tipo', 'Pagamento', 'Valor'}.issubset(df.columns):
                logging.info("Planilha de programados detectada.")
                df = df[['Descrição', 'Tipo', 'Pagamento', 'Valor']]
                df = df.rename(columns={
                    'Descrição': 'Descrição',
                    'Tipo': 'Tipo Programado',
                    'Pagamento': 'Data Pagamento',
                    'Valor': 'Valor Programado'
                })
                self.validate_and_store_data(df, "programados", overwrite)

            else:
                logging.error("Formato desconhecido no arquivo Excel para o tipo especificado.")
                return None

            logging.info("Dados importados com sucesso do arquivo Excel.")
            return df
        except Exception as e:
            logging.error(f"Erro ao importar dados do arquivo Excel: {e}")
            return None

    def validate_and_store_data(self, df: pd.DataFrame, data_type: str, overwrite: bool):
        try:
            # Extrair o mês e ano das datas
            df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], format='%d/%m/%Y')
            df['MesAno'] = df['Data Pagamento'].dt.strftime('%Y_%m')

            # Validar se todas as datas pertencem ao mesmo mês e ano
            mes_ano_contagem = Counter(df['MesAno'])
            if len(mes_ano_contagem) > 1:
                logging.error("As datas no arquivo pertencem a múltiplos meses e anos.")
                for mes_ano, count in mes_ano_contagem.items():
                    logging.warning(f"{mes_ano}: {count} registros")
                return

            # Determinar o mês e ano para o nome do arquivo
            mes_ano = df['MesAno'].iloc[0]
            df.drop(columns=['MesAno'], inplace=True)

            # Caminho de armazenamento
            storage_path = {
                "custos": self.custos_path,
                "receitas": self.receitas_path,
                "programados": self.programados_path
            }.get(data_type, self.storage_path)

            file_name = f"{mes_ano}_{data_type}.json"
            file_full_path = os.path.join(storage_path, file_name)

            # Verificar se o arquivo já existe
            if os.path.exists(file_full_path) and not overwrite:
                logging.info(f"Arquivo {file_full_path} já existe. Adicionando dados ao arquivo.")
                existing_data = self._read_and_decrypt_file(file_full_path)
                if existing_data is not None:
                    df = pd.concat([existing_data, df], ignore_index=True)

            # Criptografar e armazenar os dados
            self.encrypt_and_store_data(df, file_full_path)
        except Exception as e:
            logging.error(f"Erro ao validar e armazenar os dados: {e}")

    def encrypt_and_store_data(self, df: pd.DataFrame, file_full_path: str):
        try:
            # Criptografar dados
            json_data = df.to_json(orient='records')
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(json_data.encode()).decode()

            # Salvar dados criptografados em um arquivo
            with open(file_full_path, 'w') as file:
                json.dump({"data": encrypted_data}, file)

            logging.info(f"Dados criptografados e salvos em {file_full_path}.")
        except Exception as e:
            logging.error(f"Erro ao criptografar e armazenar os dados: {e}")

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
    excel_importer = ExcelImporter('caminho/para/arquivo.xlsx', encryption_key)
    data = excel_importer.import_financial_data(data_type="custos", overwrite=False)
    if data is not None:
        print(data.head())