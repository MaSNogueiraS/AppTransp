import sqlite3
import logging
import os

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseConnector:
    def __init__(self, db_path="utils/data/app_data.db"):
        """
        Conexão com o banco de dados SQLite para gerenciar custos, receitas e programados.
        :param db_path: Caminho do arquivo do banco de dados.
        """
        self.db_path = db_path
        self.connection = None

        # Criar diretório se necessário
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))

        self._initialize_database()

    def _initialize_database(self):
        """
        Inicializa as tabelas necessárias no banco de dados.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()

            # Tabelas para custos, receitas e programados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fornecedor TEXT,
                    data_pagamento TEXT,
                    valor REAL,
                    categoria TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receitas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente TEXT,
                    data_pagamento TEXT,
                    valor REAL,
                    categoria TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS programados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT,
                    tipo TEXT,
                    data_prevista TEXT,
                    valor REAL
                )
            ''')

            self.connection.commit()
            logging.info("Tabelas inicializadas com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            if self.connection:
                self.connection.close()

    def insert_data(self, table, data):
        """
        Insere dados na tabela especificada.
        :param table: Nome da tabela (custos, receitas, programados).
        :param data: Lista de dicionários com os dados a serem inseridos.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()

            if table == "custos":
                cursor.executemany('''
                    INSERT INTO custos (fornecedor, data_pagamento, valor, categoria)
                    VALUES (:fornecedor, :data_pagamento, :valor, :categoria)
                ''', data)

            elif table == "receitas":
                cursor.executemany('''
                    INSERT INTO receitas (cliente, data_pagamento, valor, categoria)
                    VALUES (:cliente, :data_pagamento, :valor, :categoria)
                ''', data)

            elif table == "programados":
                cursor.executemany('''
                    INSERT INTO programados (descricao, tipo, data_prevista, valor)
                    VALUES (:descricao, :tipo, :data_prevista, :valor)
                ''', data)

            else:
                logging.error(f"Tabela desconhecida: {table}")
                return

            self.connection.commit()
            logging.info(f"Dados inseridos com sucesso na tabela {table}.")
        except Exception as e:
            logging.error(f"Erro ao inserir dados na tabela {table}: {e}")
        finally:
            if self.connection:
                self.connection.close()

    def fetch_data(self, table, filters=None):
        """
        Busca dados da tabela especificada com filtros opcionais.
        :param table: Nome da tabela (custos, receitas, programados).
        :param filters: Dicionário com colunas e valores para filtrar (opcional).
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()

            query = f"SELECT * FROM {table}"
            if filters:
                conditions = [f"{col} = ?" for col in filters.keys()]
                query += " WHERE " + " AND ".join(conditions)
                cursor.execute(query, list(filters.values()))
            else:
                cursor.execute(query)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logging.error(f"Erro ao buscar dados da tabela {table}: {e}")
            return []
        finally:
            if self.connection:
                self.connection.close()

    def clear_table(self, table):
        """
        Limpa todos os dados da tabela especificada.
        :param table: Nome da tabela (custos, receitas, programados).
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {table}")
            self.connection.commit()
            logging.info(f"Dados da tabela {table} limpos com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao limpar dados da tabela {table}: {e}")
        finally:
            if self.connection:
                self.connection.close()

# Exemplo de uso
if __name__ == "__main__":
    db_connector = DatabaseConnector()

    # Inserir dados de exemplo
    custos_data = [
        {"fornecedor": "Posto Shell", "data_pagamento": "2024-01-15", "valor": 500.0, "categoria": "Combustível"},
        {"fornecedor": "Oficina ABC", "data_pagamento": "2024-01-20", "valor": 1200.0, "categoria": "Manutenção"}
    ]
    db_connector.insert_data("custos", custos_data)

    # Buscar dados
    fetched_data = db_connector.fetch_data("custos")
    print(fetched_data)

    # Limpar tabela
    db_connector.clear_table("custos")
