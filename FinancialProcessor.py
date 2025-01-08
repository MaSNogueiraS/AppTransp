import logging
import pandas as pd

from sklearn.linear_model import LinearRegression
import numpy as np

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FinancialProcessor:
    def __init__(self):
        self.budget_targets = {}  # Armazena metas orçamentárias por categoria

    def calculate_growth_indices(self, df: pd.DataFrame, data_type: str):
        """
        Calcula índices de crescimento para custos ou receitas.
        :param df: DataFrame contendo os dados financeiros.
        :param data_type: Tipo de dado para o índice ('custos' ou 'receitas').
        """
        try:
            df['AnoMes'] = pd.to_datetime(df['Data Pagamento']).dt.to_period('M')
            grouped = df.groupby('AnoMes')['Valor'].sum()

            growth_indices = grouped.pct_change() * 100  # Calcula a variação percentual mês a mês
            growth_indices = growth_indices.fillna(0).round(2)  # Preenche valores NaN e arredonda

            logging.info(f"Índices de crescimento calculados para {data_type}.")
            return growth_indices
        except Exception as e:
            logging.error(f"Erro ao calcular índices de crescimento: {e}")
            return pd.Series(dtype=float)

    def analyze_budget(self, df: pd.DataFrame):
        """
        Analisa o desempenho orçamentário para centros de custo.
        :param df: DataFrame contendo os dados financeiros.
        """
        try:
            grouped = df.groupby('Categoria')['Valor'].sum()
            results = []

            for category, spent in grouped.items():
                budget = self.budget_targets.get(category, None)
                if budget:
                    deviation = ((budget - spent) / budget) * 100
                    status = "Abaixo" if deviation > 0 else "Acima"
                    results.append({
                        'Categoria': category,
                        'Orçamento Previsto': budget,
                        'Gasto Atual': spent,
                        'Desvio (%)': deviation,
                        'Status': status
                    })

            logging.info("Análise orçamentária concluída.")
            return pd.DataFrame(results)
        except Exception as e:
            logging.error(f"Erro ao analisar orçamento: {e}")
            return pd.DataFrame()

    def forecast_cash_flow(self, df: pd.DataFrame):
        """
        Faz previsão de fluxo de caixa com base em dados históricos.
        :param df: DataFrame contendo os dados financeiros.
        """
        try:
            df['AnoMes'] = pd.to_datetime(df['Data Pagamento']).dt.to_period('M').dt.to_timestamp()
            grouped = df.groupby(['AnoMes', 'Tipo'])['Valor'].sum().unstack(fill_value=0)

            forecasts = {}
            for column in grouped.columns:
                x = np.arange(len(grouped)).reshape(-1, 1)
                y = grouped[column].values

                model = LinearRegression()
                model.fit(x, y)

                future_x = np.array([[len(grouped) + i] for i in range(1, 4)])  # Prever próximos 3 meses
                future_y = model.predict(future_x)

                forecasts[column] = future_y.round(2)

            logging.info("Previsão de fluxo de caixa concluída.")
            return forecasts
        except Exception as e:
            logging.error(f"Erro ao prever fluxo de caixa: {e}")
            return {}

# Exemplo de uso
if __name__ == "__main__":
    processor = FinancialProcessor()

    # Dados fictícios para teste
    data = {
        'Data Pagamento': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-01-01'],
        'Valor': [2000, 3000, 2500, 1500],
        'Categoria': ['Combustível', 'Manutenção', 'Investimento', 'Combustível'],
        'Tipo': ['Custo', 'Custo', 'Custo', 'Receita']
    }
    df = pd.DataFrame(data)

    # Testar cálculo de índices de crescimento
    growth_indices = processor.calculate_growth_indices(df[df['Tipo'] == 'Custo'], 'custos')
    print("Índices de Crescimento:")
    print(growth_indices)

    # Testar análise de orçamento
    processor.budget_targets = {'Combustível': 5000, 'Manutenção': 3000}
    budget_analysis = processor.analyze_budget(df)
    print("Análise de Orçamento:")
    print(budget_analysis)

    # Testar previsão de fluxo de caixa
    cash_flow_forecast = processor.forecast_cash_flow(df)
    print("Previsão de Fluxo de Caixa:")
    print(cash_flow_forecast)
