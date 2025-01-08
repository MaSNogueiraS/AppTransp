import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from ApplicationController import ApplicationController

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

        cash_label = QLabel("Saldo Atual: R$ 0.00")
        cash_label.setAlignment(Qt.AlignCenter)
        cash_label.setStyleSheet("font-size: 18px;")

        forecast_label = QLabel("Previsão: Dados insuficientes")
        forecast_label.setAlignment(Qt.AlignCenter)
        forecast_label.setStyleSheet("font-size: 16px; color: gray;")

        financial_button = QPushButton("Ir para Financeiro")
        financial_button.clicked.connect(self.show_financial_screen)

        config_button = QPushButton("Ir para Configurações")
        config_button.clicked.connect(self.show_configuration_screen)

        layout.addWidget(title)
        layout.addWidget(cash_label)
        layout.addWidget(forecast_label)
        layout.addWidget(financial_button)
        layout.addWidget(config_button)

        widget.setLayout(layout)
        return widget

    def create_financial_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Análise Financeira")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        back_button = QPushButton("Voltar")
        back_button.clicked.connect(self.show_home_screen)

        layout.addWidget(title)
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

    def show_home_screen(self):
        self.central_widget.setCurrentWidget(self.home_screen)

    def show_financial_screen(self):
        self.central_widget.setCurrentWidget(self.financial_screen)

    def show_configuration_screen(self):
        self.central_widget.setCurrentWidget(self.configuration_screen)

    def clear_data(self):
        # Aqui chamamos o método do controlador para limpar os dados
        confirmation = self.app_controller.clear_all_data()
        if confirmation:
            print("Dados limpos com sucesso.")
        else:
            print("Erro ao limpar dados.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Inicializar controlador da aplicação
    encryption_key = b'kMFeIcTPHnVRP1XsZ3qBLRMG6qL0JH8sWuE1yN9ybXU='
    excel_file_path = "caminho/para/arquivo.xlsx"
    app_controller = ApplicationController(encryption_key, excel_file_path)

    main_window = MainWindow(app_controller)
    main_window.show()

    sys.exit(app.exec_())
