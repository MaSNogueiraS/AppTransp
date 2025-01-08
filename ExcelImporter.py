import pandas as pd
import os
import logging
from cryptography.fernet import Fernet
import json
from collections import defaultdict

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExcelImporter:
    def __init__(self, encryption_key, storage_path="utils/data/"):
        """
        Importa dados de arquivos Excel e gerencia armazenamento criptografado.
        :param encryption_key: Chave de criptografia para os dados.
        :param storage_path: Caminho de armazenamento dos dados processados.
        """
        self.encryption_key = encryption_key
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

        self.categories = defaultdict(lambda: "Não categorizado")
        self.load_categories()

    def load_categories(self):
        """
        Carrega categorias salvas para fornecedores, clientes e investimentos.
        """
        try:
            categories_file = os.path.join(self.storage_path, "categories.json")
            if os.path.exists(categories_file):
                with open(categories_file, 'r') as f:
                    self.categories.update(json.load(f))
            logging.info("Categorias carregadas com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao carregar categorias: {e}")

    def save_categories(self):
        """
        Salva categorias atuais para fornecedores, clientes e investimentos.
        """
        try:
            categories_file = os.path.join(self.storage_path, "categories.json")
            with open(categories_file, 'w') as f:
                json.dump(self.categories, f)
            logging.info("Categorias salvas com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao salvar categorias: {e}")

    def import_financial_data(self, file_path, data_type, selected_date):
        """
        Importa dados financeiros de um arquivo Excel.
        :param file_path: Caminho do arquivo Excel.
        :param data_type: Tipo de dado a importar (custos, receitas, programados).
        :param selected_date: Data selecionada (yyyy-MM).
        """
        if not os.path.exists(file_path):
            logging.error(f"Arquivo não encontrado: {file_path}")
            return None

        try:
            df = pd.read_excel(file_path)
            if data_type == "custos":
                df = self.process_costs(df)
            elif data_type == "receitas":
                df = self.process_revenues(df)
            elif data_type == "programados":
                df = self.process_scheduled(df)
            else:
                logging.error("Tipo de dado desconhecido.")
                return None

            # Verificar se já existe arquivo para o tipo e data
            file_name = f"{data_type}_{selected_date}.json"
            file_path = os.path.join(self.storage_path, file_name)

            if os.path.exists(file_path):
                user_choice = input("Dados para esta data já existem. Deseja (A)dicionar, (S)obrescrever ou (C)riar novo? ").strip().upper()
                if user_choice == "A":
                    self.append_to_existing_data(file_path, df)
                elif user_choice == "S":
                    self.save_encrypted_data(df, file_path)
                elif user_choice == "C":
                    new_file_name = f"{data_type}_{selected_date}_novo.json"
                    new_file_path = os.path.join(self.storage_path, new_file_name)
                    self.save_encrypted_data(df, new_file_path)
                else:
                    logging.warning("Escolha inválida. Operação cancelada.")
                    return None
            else:
                # Salvar os dados processados criptografados
                self.save_encrypted_data(df, file_path)
            return df
        except Exception as e:
            logging.error(f"Erro ao importar dados: {e}")
            return None

    def process_costs(self, df):
        """
        Processa dados de custos.
        """
        required_columns = ['Fornecedor - Nome', 'Pagamento', 'Valor']
        if not all(col in df.columns for col in required_columns):
            logging.error("Colunas necessárias para custos não encontradas.")
            return None

        df = df[required_columns]
        df.columns = ['Fornecedor', 'Data Pagamento', 'Valor']
        df['Categoria'] = df['Fornecedor'].apply(self.categorize_supplier)
        df['Tipo'] = df['Categoria'].apply(lambda x: 'Investimento' if 'investimento' in x.lower() else 'Custo')
        return df

    def process_revenues(self, df):
        """
        Processa dados de receitas.
        """
        required_columns = ['Cliente - Nome', 'Pagamento', 'Valor']
        if not all(col in df.columns for col in required_columns):
            logging.error("Colunas necessárias para receitas não encontradas.")
            return None

        df = df[required_columns]
        df.columns = ['Cliente', 'Data Pagamento', 'Valor']
        df['Categoria'] = df['Cliente'].apply(self.categorize_client)
        return df

    def process_scheduled(self, df):
        """
        Processa dados programados.
        """
        required_columns = ['Descrição', 'Tipo', 'Pagamento', 'Valor']
        if not all(col in df.columns for col in required_columns):
            logging.error("Colunas necessárias para programados não encontradas.")
            return None

        df = df[required_columns]
        df.columns = ['Descrição', 'Tipo Programado', 'Data Pagamento', 'Valor']
        return df

    def categorize_supplier(self, supplier):
        """
        Categoriza um fornecedor.
        """
        if supplier not in self.categories:
            self.categories[supplier] = input(f"Por favor, categorize o fornecedor '{supplier}': ")
        return self.categories[supplier]

    def categorize_client(self, client):
        """
        Categoriza um cliente.
        """
        if client not in self.categories:
            self.categories[client] = input(f"Por favor, categorize o cliente '{client}': ")
        return self.categories[client]

    def append_to_existing_data(self, file_path, new_data):
        """
        Adiciona dados novos a um arquivo existente.
        """
        try:
            fernet = Fernet(self.encryption_key)
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)["data"]
                existing_data = pd.read_json(fernet.decrypt(encrypted_data.encode()).decode())

            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
            self.save_encrypted_data(combined_data, file_path)
        except Exception as e:
            logging.error(f"Erro ao adicionar dados: {e}")

    def save_encrypted_data(self, df, file_path):
        """
        Criptografa e salva os dados processados.
        """
        try:
            fernet = Fernet(self.encryption_key)
            json_data = df.to_json(orient='records')
            encrypted_data = fernet.encrypt(json_data.encode()).decode()

            with open(file_path, 'w') as f:
                json.dump({"data": encrypted_data}, f)

            logging.info(f"Dados salvos com sucesso em {file_path}.")
        except Exception as e:
            logging.error(f"Erro ao salvar dados criptografados: {e}")

# Exemplo de uso
if __name__ == "__main__":
    encryption_key = Fernet.generate_key()
    importer = ExcelImporter(encryption_key)
    importer.import_financial_data("caminho/para/arquivo.xlsx", "custos", "2023-05")
