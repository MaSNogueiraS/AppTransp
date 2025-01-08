import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QDialog, QComboBox, QCheckBox, QFormLayout
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter
from application_controller import ApplicationController
import pandas as pd
import os

class DataSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Dados")
        self.setGeometry(200, 200, 400, 300)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Custos", "Receitas", "Programados"])

        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(2020, QDate.currentDate().year() + 1)])

        self.month_combo = QComboBox()
        self.month_combo.addItems(["01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril", "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto", "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"])

        self.programmed_checkbox = QCheckBox("Dados Programados")

        self.submit_button = QPushButton("Confirmar")
        self.submit_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)

        layout = QFormLayout()
        layout.addRow("Tipo de Dado:", self.type_combo)
        layout.addRow("Ano:", self.year_combo)
        layout.addRow("Mês:", self.month_combo)
        layout.addRow("Programado:", self.programmed_checkbox)
        layout.addRow(self.submit_button, self.cancel_button)

        self.setLayout(layout)

    def get_data(self):
        selected_type = self.type_combo.currentText()
        selected_year = self.year_combo.currentText()
        selected_month = self.month_combo.currentText().split(" - ")[0]
        is_programmed = self.programmed_checkbox.isChecked()
        return selected_type, f"{selected_year}-{selected_month}", is_programmed

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
        data = self.app_controller.analyze_financial_data()
        if data is not None:
            for i, row in data.iterrows():
                series_costs.append(i, row["Custos"])
                series_revenues.append(i, row["Receitas"])
                series_results.append(i, row["Resultado"])
                series_trend.append(i, row["Tendência"])

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
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo Excel", "", "Arquivos Excel (*.xlsx)")

        if file_path:
            dialog = DataSelectionDialog(self)
            if dialog.exec_():
                data_type, selected_date, is_programmed = dialog.get_data()
                file_name = f"{data_type}_{selected_date.replace('-', '_')}"
                self.process_excel_file(file_path, data_type, selected_date, is_programmed, file_name)

    def process_excel_file(self, file_path, data_type, selected_date, is_programmed, file_name):
        try:
            renamed_file_path = os.path.join(self.app_controller.storage_path, f"{file_name}.xlsx")

            if os.path.exists(renamed_file_path):
                response = QMessageBox.question(self, "Arquivo Existente", "Dados para este mês já existem. Deseja adicionar ou sobrescrever?", 
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if response == QMessageBox.No:
                    os.remove(renamed_file_path)

            os.rename(file_path, renamed_file_path)

            success = self.app_controller.import_excel_data(renamed_file_path, data_type, selected_date)
            if success:
                QMessageBox.information(self, "Sucesso", "Dados importados com sucesso.")
                self.update_financial_display()
            else:
                QMessageBox.warning(self, "Erro", "Falha ao adicionar dados.")
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", f"Erro ao processar arquivo: {e}")

    def update_financial_display(self):
        analysis = self.app_controller.analyze_financial_data()
        if analysis is not None:
            self.financial_display.setText(f"Dados Financeiros: {analysis.to_string(index=False)}")
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

    encryption_key = b'kMFeIcTPHnVRP1XsZ3qBLRMG6qL0JH8sWuE1yN9ybXU='
    app_controller = ApplicationController(encryption_key)

    main_window = MainWindow(app_controller)
    main_window.show()

    sys.exit(app.exec_())
