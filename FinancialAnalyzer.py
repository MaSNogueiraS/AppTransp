import pandas as pd
import logging
import json
from sklearn.linear_model import LinearRegression
import numpy as np

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FinancialAnalyzer:
    def __init__(self):
        self.investment_keywords = ["banco", "leasing", "financiamento"]
        self.user_defined_keywords = {}
        self.budget_targets = {}  # Armazena metas por centro de custo

    def classify_costs(self, df: pd.DataFrame):
        """
        Classifica custos como investimentos ou operacionais com base em palavras-chave.
        Solicita ao usuário classificar itens desconhecidos.
        """
        df['Categoria'] = df['Fornecedor'].apply(self._categorize_cost)
        return df

    def _categorize_cost(self, fornecedor):
        # Verificar palavras-chave conhecidas
        for keyword in self.investment_keywords:
            if keyword.lower() in fornecedor.lower():
                return 'Investimento'

        # Verificar palavras-chave definidas pelo usuário
        for keyword, category in self.user_defined_keywords.items():
            if keyword.lower() in fornecedor.lower():
                return category

        # Solicitar classificação para itens desconhecidos
        logging.warning(f"Fornecedor desconhecido: {fornecedor}. Solicitação ao usuário necessária.")
        category = input(f"Classifique o fornecedor '{fornecedor}' (Investimento/Operacional): ").strip()
        self.user_defined_keywords[fornecedor.lower()] = category
        return category

    def analyze_profitability(self, df: pd.DataFrame):
        """
        Analisa a lucratividade da empresa com base em receitas e custos.
        """
        total_revenue = df[df['Tipo'] == 'Receita']['Valor'].sum()
        total_cost = df[df['Tipo'] == 'Custo']['Valor'].sum()
        profit = total_revenue - total_cost
        margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0

        return {
            'Receita Total': total_revenue,
            'Custo Total': total_cost,
            'Lucro': profit,
            'Margem de Lucro (%)': margin
        }

    def identify_leaders(self, df: pd.DataFrame):
        """
        Identifica líderes de custos e receitas.
        """
        top_costs = df[df['Tipo'] == 'Custo'].groupby('Fornecedor')['Valor'].sum().nlargest(5)
        top_revenues = df[df['Tipo'] == 'Receita'].groupby('Cliente')['Valor'].sum().nlargest(5)

        return {
            'Líderes de Custo': top_costs,
            'Líderes de Receita': top_revenues
        }

    def detect_trends(self, df: pd.DataFrame):
        """
        Detecta tendências em receitas e custos ao longo do tempo.
        """
        df['MesAno'] = pd.to_datetime(df['Data Pagamento']).dt.to_period('M')
        trend = df.groupby(['MesAno', 'Tipo'])['Valor'].sum().unstack().fillna(0)
        return trend

    def forecast(self, df: pd.DataFrame):
        """
        Faz previsão de receitas e custos futuros com base em séries temporais.
        """
        df['MesAno'] = pd.to_datetime(df['Data Pagamento']).dt.to_period('M').dt.to_timestamp()
        trend = df.groupby(['MesAno', 'Tipo'])['Valor'].sum().unstack().fillna(0)

        forecasts = {}
        for column in trend.columns:
            x = np.arange(len(trend)).reshape(-1, 1)
            y = trend[column].values

            model = LinearRegression()
            model.fit(x, y)

            future_x = np.array([[len(trend) + i] for i in range(1, 4)])  # Prever próximos 3 períodos
            future_y = model.predict(future_x)

            forecasts[column] = future_y

        return forecasts

    def analyze_budget(self, df: pd.DataFrame):
        """
        Analisa o orçamento previsto para centros de custo e receita.
        """
        results = []
        grouped = df.groupby('Categoria')['Valor'].sum()

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
        return pd.DataFrame(results)

# Exemplo de uso
if __name__ == "__main__":
    analyzer = FinancialAnalyzer()

    # Dados fictícios para teste
    data = {
        'Fornecedor': ['Banco Volvo', 'Posto A', 'Fornecedor B'],
        'Cliente': ['Cliente X', 'Cliente Y', 'Cliente Z'],
        'Tipo': ['Custo', 'Custo', 'Receita'],
        'Valor': [2000, 1500, 5000],
        'Data Pagamento': ['2024-01-01', '2024-01-02', '2024-01-03']
    }
    df = pd.DataFrame(data)

    # Classificar custos
    df = analyzer.classify_costs(df)
    print(df)

    # Analisar lucratividade
    profit_analysis = analyzer.analyze_profitability(df)
    print(json.dumps(profit_analysis, indent=2))

    # Identificar líderes
    leaders = analyzer.identify_leaders(df)
    print(leaders)

    # Detectar tendências
    trends = analyzer.detect_trends(df)
    print(trends)

    # Fazer previsões
    forecasts = analyzer.forecast(df)
    print(forecasts)

    # Analisar orçamento
    analyzer.budget_targets = {'Investimento': 3000, 'Operacional': 2000}
    budget_analysis = analyzer.analyze_budget(df)
    print(budget_analysis)
