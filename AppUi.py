import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter
from application_controller import ApplicationController
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()

        self.app_controller = app_controller

        self.setWindowTitle("Fabri Log Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        # Home Screen
        self.home_screen = self.create_home_screen()
        self.central_widget.addWidget(self.home_screen)

        # Financial Screen
        self.financial_screen = self.create_financial_screen()
        self.central_widget.addWidget(self.financial_screen)

        # Configuration Screen
        self.configuration_screen = self.create_configuration_screen()
        self.central_widget.addWidget(self.configuration_screen)

        self.central_widget.setCurrentWidget(self.home_screen)

    def create_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Fabri Log Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.cash_label = QLabel("Saldo Atual: Dados insuficientes")
        self.cash_label.setAlignment(Qt.AlignCenter)
        self.cash_label.setStyleSheet("font-size: 18px;")

        self.forecast_label = QLabel("Previsão: Dados insuficientes")
        self.forecast_label.setAlignment(Qt.AlignCenter)
        self.forecast_label.setStyleSheet("font-size: 16px; color: gray;")

        self.chart_view = self.create_financial_chart()

        financial_button = QPushButton("Ir para Financeiro")
        financial_button.clicked.connect(self.show_financial_screen)

        config_button = QPushButton("Ir para Configurações")
        config_button.clicked.connect(self.show_configuration_screen)

        layout.addWidget(title)
        layout.addWidget(self.cash_label)
        layout.addWidget(self.forecast_label)
        layout.addWidget(self.chart_view)
        layout.addWidget(financial_button)
        layout.addWidget(config_button)

        widget.setLayout(layout)
        return widget

    def create_financial_chart(self):
        chart = QChart()
        chart.setTitle("Resumo Financeiro dos Últimos 6 Meses")

        series_costs = QLineSeries()
        series_revenues = QLineSeries()
        series_results = QLineSeries()
        series_trend = QLineSeries()

        series_costs.setName("Gastos")
        series_revenues.setName("Receitas")
        series_results.setName("Resultado")
        series_trend.setName("Tendência")

        # Obter dados do controlador
        data = self.app_controller.analyze_financials()
        if data:
            last_6_months = list(data.get("Crescimento Custos", {}).keys())[-6:]
            for i, month in enumerate(last_6_months):
                series_costs.append(i, data["Crescimento Custos"].get(month, 0))
                series_revenues.append(i, data["Crescimento Receitas"].get(month, 0))
                series_results.append(i, data["Crescimento Receitas"].get(month, 0) - data["Crescimento Custos"].get(month, 0))

            # Calcular tendência
            trend_data = self.app_controller.forecast_cash_flow()
            for i, (month, value) in enumerate(trend_data.items()):
                series_trend.append(i + len(last_6_months), value)

        chart.addSeries(series_costs)
        chart.addSeries(series_revenues)
        chart.addSeries(series_results)
        chart.addSeries(series_trend)

        axis_x = QValueAxis()
        axis_x.setTitleText("Meses")
        axis_x.setLabelFormat("%d")
        chart.addAxis(axis_x, Qt.AlignBottom)

        axis_y = QValueAxis()
        axis_y.setTitleText("Valores")
        chart.addAxis(axis_y, Qt.AlignLeft)

        series_costs.attachAxis(axis_x)
        series_costs.attachAxis(axis_y)
        series_revenues.attachAxis(axis_x)
        series_revenues.attachAxis(axis_y)
        series_results.attachAxis(axis_x)
        series_results.attachAxis(axis_y)
        series_trend.attachAxis(axis_x)
        series_trend.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        return chart_view

    def create_financial_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Análise Financeira")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        add_data_button = QPushButton("Adicionar Dados")
        add_data_button.clicked.connect(self.add_data)

        self.financial_display = QLabel("Sem dados financeiros para exibir")
        self.financial_display.setAlignment(Qt.AlignCenter)
        self.financial_display.setStyleSheet("font-size: 16px; color: gray;")

        back_button = QPushButton("Voltar")
        back_button.clicked.connect(self.show_home_screen)

        layout.addWidget(title)
        layout.addWidget(add_data_button)
        layout.addWidget(self.financial_display)
        layout.addWidget(back_button)

        widget.setLayout(layout)
        return widget

    def create_configuration_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Configurações")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        clear_data_button = QPushButton("Limpar Dados")
        clear_data_button.clicked.connect(self.clear_data)

        back_button = QPushButton("Voltar")
        back_button.clicked.connect(self.show_home_screen)

        layout.addWidget(title)
        layout.addWidget(clear_data_button)
        layout.addWidget(back_button)

        widget.setLayout(layout)
        return widget

    def add_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo Excel", "", "Arquivos Excel (*.xlsx);;Todos os Arquivos (*)", options=options)

        if file_path:
            data_type, ok = self.get_data_type()
            if ok:
                self.process_excel_file(file_path, data_type)

    def get_data_type(self):
        data_types = {"Custos": "custos", "Receitas": "receitas", "Programados": "programados"}
        items = list(data_types.keys())
        selected, ok = QMessageBox.question(
            self, "Selecionar Tipo de Dados", "Escolha o tipo de dados para importar:",
            QMessageBox.Yes | QMessageBox.No
        ), True

        return (data_types.get(selected), ok) if ok else (None, False)

    def process_excel_file(self, file_path, data_type):
        try:
            data = self.app_controller.import_data(file_path, data_type)
            if data:
                QMessageBox.information(self, "Sucesso", f"Dados de {data_type} adicionados com sucesso.")
                self.update_financial_display()
            else:
                QMessageBox.warning(self, "Erro", "Falha ao adicionar dados.")
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", str(e))

    def update_financial_display(self):
        analysis = self.app_controller.analyze_financials()
        if analysis:
            self.financial_display.setText(f"Crescimento Custos: {analysis['Crescimento Custos']}\nCrescimento Receitas: {analysis['Crescimento Receitas']}")
        else:
            self.financial_display.setText("Sem dados financeiros para exibir")

    def show_home_screen(self):
        self.central_widget.setCurrentWidget(self.home_screen)

    def show_financial_screen(self):
        self.central_widget.setCurrentWidget(self.financial_screen)

    def show_configuration_screen(self):
        self.central_widget.setCurrentWidget(self.configuration_screen)

    def clear_data(self):
        confirmation = self.app_controller.clear_all_data()
        if confirmation:
            QMessageBox.information(self, "Sucesso", "Todos os dados foram limpos com sucesso.")
        else:
            QMessageBox.warning(self, "Erro", "Falha ao limpar os dados.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Inicializar controlador da aplicação
    encryption_key = b'kMFeIcTPHnVRP1XsZ3qBLRMG6qL0JH8sWuE1yN9ybXU='
    excel_file_path = "caminho/para/arquivo.xlsx"
    app_controller = ApplicationController(encryption_key, excel_file_path)

    main_window = MainWindow(app_controller)
    main_window.show()

    sys.exit(app.exec_())
