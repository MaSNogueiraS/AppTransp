import os
import logging
import threading
import hashlib
import time
import socket

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SecurityMonitor:
    def __init__(self, data_paths):
        """
        Monitoramento de segurança para proteger arquivos e detectar acessos não autorizados.
        :param data_paths: Lista de caminhos de dados para monitorar.
        """
        self.data_paths = data_paths
        self.access_logs = "utils/security/logs.txt"
        self.lock = threading.Lock()
        self.file_hashes = {}
        self.blocked_ips = set()

        # Configuração inicial
        if not os.path.exists(os.path.dirname(self.access_logs)):
            os.makedirs(os.path.dirname(self.access_logs))

    def monitor(self):
        """
        Inicia o monitoramento de acessos aos dados.
        """
        logging.info("Monitoramento de segurança iniciado.")
        for path in self.data_paths:
            if not os.path.exists(path):
                logging.warning(f"Caminho não encontrado para monitoramento: {path}")

        # Iniciar threads de monitoramento
        threading.Thread(target=self._monitor_file_changes).start()
        threading.Thread(target=self._monitor_access_attempts).start()

    def _monitor_file_changes(self):
        """
        Monitora mudanças nos arquivos, verificando seus hashes.
        """
        while True:
            with self.lock:
                for path in self.data_paths:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            self._check_file_integrity(file_path)
            time.sleep(30)  # Verificar a cada 30 segundos

    def _check_file_integrity(self, file_path):
        """
        Verifica a integridade do arquivo usando hashes MD5.
        """
        try:
            file_hash = self._calculate_file_hash(file_path)
            if file_path in self.file_hashes:
                if self.file_hashes[file_path] != file_hash:
                    logging.error(f"Alteração não autorizada detectada no arquivo: {file_path}")
                    self._log_security_event(f"Alteração detectada no arquivo: {file_path}")
            self.file_hashes[file_path] = file_hash
        except Exception as e:
            logging.error(f"Erro ao verificar integridade do arquivo {file_path}: {e}")

    def _calculate_file_hash(self, file_path):
        """
        Calcula o hash MD5 de um arquivo.
        """
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _monitor_access_attempts(self):
        """
        Monitora tentativas de acesso aos arquivos e rastreia IPs suspeitos.
        """
        while True:
            ip = self._get_current_ip()
            if ip in self.blocked_ips:
                logging.warning(f"Tentativa de acesso bloqueada do IP: {ip}")
                self._log_security_event(f"IP bloqueado tentou acesso: {ip}")
            time.sleep(10)  # Verificar a cada 10 segundos

    def _get_current_ip(self):
        """
        Obtém o IP do sistema local (simulação).
        """
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception as e:
            logging.error(f"Erro ao obter IP do sistema: {e}")
            return "127.0.0.1"

    def block_ip(self, ip):
        """
        Adiciona um IP à lista de bloqueio.
        """
        self.blocked_ips.add(ip)
        logging.info(f"IP bloqueado: {ip}")

    def _log_security_event(self, message):
        """
        Registra eventos de segurança em um arquivo de log.
        """
        with open(self.access_logs, 'a') as log_file:
            log_file.write(f"{message}\n")

# Exemplo de uso
if __name__ == "__main__":
    data_paths = [
        "utils/data/custos/",
        "utils/data/receitas/",
        "utils/data/programados/"
    ]
    security_monitor = SecurityMonitor(data_paths)
    security_monitor.monitor()
