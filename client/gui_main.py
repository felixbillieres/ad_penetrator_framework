import sys
import os
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QTextEdit, QStatusBar, QLabel,
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QLineEdit, QDialog, QDialogButtonBox,
    QFormLayout, QFrame
)
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer

# Tentative d'importation de APIClient
try:
    from client.api_client import APIClient
except ModuleNotFoundError:
    # Solution de contournement pour les exécutions où le PYTHONPATH n'est pas bien configuré
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from client.api_client import APIClient

# --- Configuration Dialog ---
class ConfigDialog(QDialog):
    def __init__(self, parent=None, current_c2_url="http://localhost:8000"):
        super().__init__(parent)
        self.setWindowTitle("Configuration du Serveur C2")
        layout = QFormLayout(self)
        self.c2_url_input = QLineEdit(current_c2_url)
        layout.addRow("URL du Serveur C2:", self.c2_url_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_c2_url(self):
        return self.c2_url_input.text().strip()

# --- Worker Thread for API Calls ---
class ApiWorker(QThread):
    agents_fetched = pyqtSignal(object)
    server_status_checked = pyqtSignal(tuple)

    def __init__(self, api_client_instance, action, params=None):
        super().__init__()
        self.api_client = api_client_instance
        self.action = action
        self.params = params if params is not None else {}

    def run(self):
        if not self.api_client:
            if self.action == "get_agents":
                self.agents_fetched.emit(None)
            elif self.action == "check_status":
                self.server_status_checked.emit((False, "Client API non initialisé"))
            return

        if self.action == "get_agents":
            try:
                agents = self.api_client.get_agents()
                self.agents_fetched.emit(agents)
            except Exception as e:
                print(f"Erreur dans le thread ApiWorker (get_agents): {e}")
                self.agents_fetched.emit(None)
        elif self.action == "check_status":
            try:
                status, message = self.api_client.check_server_status()
                self.server_status_checked.emit((status, message))
            except Exception as e:
                print(f"Erreur dans le thread ApiWorker (check_status): {e}")
                self.server_status_checked.emit((False, f"Erreur interne du worker: {e}"))

# --- Views ---
class DashboardView(QWidget):
    def __init__(self, parent=None, api_client_instance=None):
        super().__init__(parent)
        self.api_client = api_client_instance
        self.worker = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        info_font = QFont("Segoe UI", 12)

        # Cadre pour le statut du serveur
        server_status_frame = QFrame(self)
        server_status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        server_status_layout = QVBoxLayout(server_status_frame)
        self.server_status_title = QLabel("Statut du Serveur C2")
        self.server_status_title.setFont(title_font)
        self.server_status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.server_status_label = QLabel("Vérification...")
        self.server_status_label.setFont(info_font)
        self.server_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.server_status_label.setWordWrap(True)
        server_status_layout.addWidget(self.server_status_title)
        server_status_layout.addWidget(self.server_status_label)
        layout.addWidget(server_status_frame)

        # Cadre pour les statistiques des agents
        agents_stats_frame = QFrame(self)
        agents_stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        agents_stats_layout = QVBoxLayout(agents_stats_frame)
        self.agents_stats_title = QLabel("Statistiques des Agents")
        self.agents_stats_title.setFont(title_font)
        self.agents_stats_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connected_agents_label = QLabel("Agents Connectés : N/A")
        self.connected_agents_label.setFont(info_font)
        self.connected_agents_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        agents_stats_layout.addWidget(self.agents_stats_title)
        agents_stats_layout.addWidget(self.connected_agents_label)
        layout.addWidget(agents_stats_frame)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Timer pour rafraîchir le dashboard périodiquement
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_dashboard_data)
        self.refresh_timer.start(30000) # Rafraîchir toutes les 30 secondes

    def refresh_dashboard_data(self):
        # Cette méthode sera appelée par MainWindow ou directement si la vue est active
        if self.api_client and self.isVisible():
            # Déclencher la vérification du statut du serveur (géré par MainWindow)
            # Déclencher la récupération des agents pour les stats
            if self.worker and self.worker.isRunning():
                return
            self.worker = ApiWorker(self.api_client, "get_agents")
            self.worker.agents_fetched.connect(self.update_agents_stats)
            self.worker.finished.connect(self._clear_worker)
            self.worker.start()

    def update_server_status(self, server_ok, message):
        if server_ok:
            self.server_status_label.setText(f"<font color='#4CAF50'>{message}</font>") # Vert
        else:
            self.server_status_label.setText(f"<font color='#F44336'>{message}</font>") # Rouge

    def update_agents_stats(self, agents_data):
        if agents_data is not None:
            active_agents = [agent for agent in agents_data if agent.get('status', '').lower() == 'active']
            self.connected_agents_label.setText(f"Agents Actifs : <font color='#2196F3'>{len(active_agents)}</font> / {len(agents_data)} total")
        else:
            self.connected_agents_label.setText("Agents Actifs : <font color='#F44336'>Erreur de récupération</font>")

    def _clear_worker(self):
        if self.worker:
            self.worker.deleteLater()
        self.worker = None
        
    def set_api_client(self, api_client):
        self.api_client = api_client
        # Rafraîchir les données si le client API est (re)défini et que la vue est visible
        if self.isVisible():
            self.refresh_dashboard_data()
            # La vérification du statut du serveur est généralement initiée par MainWindow
            # mais on peut forcer ici si nécessaire.
            if hasattr(self.parent().parent(), 'check_server_connection_status'):
                 self.parent().parent().check_server_connection_status()

class AgentsView(QWidget):
    def __init__(self, parent=None, api_client_instance=None, base_font=None):
        super().__init__(parent)
        self.api_client = api_client_instance
        self.worker = None
        self.base_font = base_font if base_font else QFont("Segoe UI", 10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)

        title_font = QFont(self.base_font)
        title_font.setPointSize(16)
        title_font.setBold(True)

        title_label = QLabel("Gestion des Agents Connectés")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.agents_table = QTableWidget()
        self.agents_table.setFont(self.base_font)
        self.agents_table.setColumnCount(6)
        self.agents_table.setHorizontalHeaderLabels([
            "Statut", "ID Agent/Hostname", "IP Interne",
            "Utilisateur Agent", "OS Cible", "Dernier Check-in"
        ])
        header = self.agents_table.horizontalHeader()
        header.setFont(self.base_font)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.agents_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.agents_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.agents_table.setAlternatingRowColors(True)
        layout.addWidget(self.agents_table)

        action_buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton(" Rafraîchir la Liste")
        self.refresh_button.setFont(self.base_font)
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_button.clicked.connect(self.fetch_agents_data)
        action_buttons_layout.addWidget(self.refresh_button)
        layout.addLayout(action_buttons_layout)
        self.setLayout(layout)

        if self.api_client:
            self.fetch_agents_data()
            
    def set_api_client(self, api_client):
        self.api_client = api_client
        if self.isVisible(): self.fetch_agents_data()

    def fetch_agents_data(self):
        if not self.api_client:
            if self.isVisible(): # Afficher le message seulement si la vue est visible
                QMessageBox.critical(self, "Erreur API", "Client API non configuré. Configurez l'URL du C2 (Paramètres).")
            self.update_agent_list([])
            return
        if self.worker and self.worker.isRunning(): return
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText(" Rafraîchissement...")
        self.worker = ApiWorker(self.api_client, "get_agents")
        self.worker.agents_fetched.connect(self.handle_agents_fetched)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def handle_agents_fetched(self, agents_data):
        if agents_data is None:
            if self.isVisible():
                QMessageBox.warning(self, "Erreur Récupération", "Impossible de récupérer les agents. Vérifiez C2 & logs.")
            self.update_agent_list([])
        else:
            self.update_agent_list(agents_data)
            if not agents_data and self.isVisible() and self.parent() and hasattr(self.parent().parent(), 'statusBar'):
                self.parent().parent().statusBar().showMessage("Aucun agent trouvé.", 3000)

    def on_worker_finished(self):
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText(" Rafraîchir la Liste")
        if self.worker: self.worker.deleteLater(); self.worker = None

    def update_agent_list(self, agents_data):
        self.agents_table.setRowCount(0)
        if not agents_data: return
        self.agents_table.setRowCount(len(agents_data))
        for row_idx, agent in enumerate(agents_data):
            status_icon = "⚫"; agent_s = agent.get('status','u').lower()
            if agent_s=="active": status_icon="🟢"
            elif agent_s=="inactive": status_icon="🔴"
            elif agent_s=="pending": status_icon="🟡"
            dt_str="N/A"; dt_raw=agent.get('last_checkin_time')
            if dt_raw:
                try: dt_str=datetime.datetime.fromisoformat(str(dt_raw).replace('Z','+00:00')).strftime("%Y-%m-%d %H:%M:%S")
                except: dt_str=str(dt_raw)
            hn=agent.get('hostname','N/A'); did=f"{agent.get('id','N/A')} ({hn})" if hn!='N/A' else agent.get('id','N/A')
            row=[status_icon,did,agent.get('internal_ip','N/A'),agent.get('username','N/A'),agent.get('os_target','N/A'),dt_str]
            for col_idx, data in enumerate(row):
                item=QTableWidgetItem(data); item.setFont(self.base_font)
                if col_idx==0: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.agents_table.setItem(row_idx,col_idx,item)
        self.agents_table.resizeColumnsToContents()
        self.agents_table.resizeRowsToContents()

class ADDataView(QWidget):
    def __init__(self, parent=None, base_font=None):
        super().__init__(parent); layout = QVBoxLayout(self); 
        lbl = QLabel("Vue Données Active Directory (Contenu à venir)"); lbl.setFont(base_font if base_font else QFont("Segoe UI", 10)); layout.addWidget(lbl); self.setLayout(layout)

class PlaybooksView(QWidget):
    def __init__(self, parent=None, base_font=None):
        super().__init__(parent); layout = QVBoxLayout(self); 
        lbl = QLabel("Vue Playbooks (Contenu à venir)"); lbl.setFont(base_font if base_font else QFont("Segoe UI", 10)); layout.addWidget(lbl); self.setLayout(layout)

class ModulesView(QWidget):
    def __init__(self, parent=None, base_font=None):
        super().__init__(parent); layout = QVBoxLayout(self); 
        lbl = QLabel("Vue Modules (Contenu à venir)"); lbl.setFont(base_font if base_font else QFont("Segoe UI", 10)); layout.addWidget(lbl); self.setLayout(layout)

class SettingsView(QWidget):
    config_changed = pyqtSignal(str)
    def __init__(self, parent=None, current_c2_url="http://localhost:8000", base_font=None):
        super().__init__(parent)
        self.current_c2_url = current_c2_url
        self.base_font = base_font if base_font else QFont("Segoe UI", 10)
        layout = QVBoxLayout(self); layout.setContentsMargins(20,20,20,20)
        form_layout = QFormLayout()
        self.c2_url_label = QLabel("URL du Serveur C2:"); self.c2_url_label.setFont(self.base_font)
        self.c2_url_input = QLineEdit(self.current_c2_url); self.c2_url_input.setFont(self.base_font)
        form_layout.addRow(self.c2_url_label, self.c2_url_input)
        self.save_button = QPushButton("Enregistrer et Appliquer"); self.save_button.setFont(self.base_font)
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_config)
        layout.addLayout(form_layout); layout.addWidget(self.save_button); layout.addStretch()
        self.setLayout(layout)
    def save_config(self):
        new_url = self.c2_url_input.text().strip()
        if not new_url: QMessageBox.warning(self,"Erreur","URL C2 vide."); return
        if not (new_url.startswith("http://") or new_url.startswith("https://")): QMessageBox.warning(self,"Erreur","URL C2 invalide."); return
        self.current_c2_url = new_url; self.config_changed.emit(self.current_c2_url)
        QMessageBox.information(self,"Config",f"URL C2 MàJ: {self.current_c2_url}")
    def get_c2_url(self): return self.c2_url_input.text().strip()


class MainWindow(QMainWindow):
    DEFAULT_C2_URL = "http://localhost:8000"
    APP_STYLESHEET = """
        QMainWindow, QDialog {
            background-color: #2E2E2E;
            color: #E0E0E0;
        }
        QListWidget {
            background-color: #3C3C3C;
            color: #E0E0E0;
            border: 1px solid #555555;
            font-size: 11pt;
        }
        QListWidget::item {
            padding: 8px;
        }
        QListWidget::item:selected {
            background-color: #5E81AC; /* Bleu Nord */
            color: #ECEFF4;
        }
        QStackedWidget > QWidget { /* Assure que le fond des vues est aussi sombre */
            background-color: #2E2E2E;
            color: #E0E0E0;
        }
        QFrame {
            background-color: #383838;
            border-radius: 5px;
            border: 1px solid #4A4A4A;
        } 
        QLabel {
            color: #E0E0E0;
            /* Laisser la police être définie par les vues spécifiques ou la police de base */
        }
        QPushButton {
            background-color: #4A4A4A;
            color: #E0E0E0;
            border: 1px solid #555555;
            padding: 8px;
            font-size: 10pt;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #5A5A5A;
        }
        QPushButton:pressed {
            background-color: #6A6A6A;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #777777;
        }
        QTableWidget {
            background-color: #3C3C3C;
            color: #E0E0E0;
            gridline-color: #555555;
            border: 1px solid #555555;
        }
        QTableWidget QHeaderView::section {
            background-color: #4A4A4A;
            color: #E0E0E0;
            padding: 4px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #5E81AC; 
            color: #ECEFF4;
        }
        QLineEdit {
            background-color: #3C3C3C;
            color: #E0E0E0;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 3px;
        }
        QStatusBar {
            color: #E0E0E0;
            font-size: 9pt;
        }
        QMessageBox {
            background-color: #3C3C3C; /* Peut ne pas toujours s'appliquer à toutes les parties de QMessageBox */
        }
        QMessageBox QLabel {
             color: #E0E0E0; /* S'assurer que le texte est lisible */
        }
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AD Penetrator Framework - Client C2")
        self.base_font = QFont("Segoe UI", 10) # Police de base pour l'application
        self.setFont(self.base_font) # Appliquer la police à la fenêtre principale
        self.setGeometry(100, 100, 1350, 950)
        self.c2_url = self.DEFAULT_C2_URL
        self.api_client = None
        self.status_worker = None
        self.setStyleSheet(self.APP_STYLESHEET) # Appliquer le style global
        self.init_ui_structure()
        self.prompt_for_c2_config_on_startup()

    def init_ui_structure(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        self.nav_bar = QListWidget(); self.nav_bar.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.nav_bar.addItems([" Tableau de Bord", " Agents", " Données AD", " Playbooks", " Modules", " Paramètres"])
        # Ajouter des icônes (nécessite des fichiers d'icônes ou des thèmes système)
        # self.nav_bar.item(0).setIcon(QIcon.fromTheme("user-home")) # Exemple
        self.nav_bar.currentRowChanged.connect(self.change_view)
        self.nav_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.nav_bar.setMinimumWidth(200); self.nav_bar.setMaximumWidth(240)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.nav_bar); main_layout.addWidget(self.content_stack)
        self.status_bar = QStatusBar(); self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Veuillez configurer l'URL du serveur C2.")

    def prompt_for_c2_config_on_startup(self):
        dialog = ConfigDialog(self, self.c2_url)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_c2_configuration(dialog.get_c2_url())
        else:
            QMessageBox.information(self, "Config C2", f"Config annulée. URL par défaut: {self.c2_url}. Modifiable via Paramètres.")
            self.update_c2_configuration(self.c2_url, show_success_msg=False)

    def update_c2_configuration(self, new_url, show_success_msg=True):
        new_url = new_url.strip()
        if not (new_url.startswith("http://") or new_url.startswith("https://")):
            QMessageBox.critical(self, "URL Invalide", f"URL '{new_url}' invalide.")
            self.statusBar().showMessage("Config C2 échouée: URL invalide.")
            self.api_client = None
            self.initialize_views_with_api_client(); return
        self.c2_url = new_url
        try:
            self.api_client = APIClient(c2_base_url=self.c2_url)
            if show_success_msg: QMessageBox.information(self, "Config C2", f"Client API OK pour: {self.c2_url}")
            self.statusBar().showMessage(f"API pour {self.c2_url}. Vérification connexion...")
            self.initialize_views_with_api_client()
            self.check_server_connection_status()
            if self.nav_bar.currentRow() < 0: self.nav_bar.setCurrentRow(0)
            else: self.change_view(self.nav_bar.currentRow())
        except ValueError as e:
            QMessageBox.critical(self, "Erreur Init API", f"{e}")
            self.statusBar().showMessage(f"Erreur config API: {e}")
            self.api_client = None; self.initialize_views_with_api_client()

    def initialize_views_with_api_client(self):
        while self.content_stack.count() > 0:
            w = self.content_stack.widget(0); self.content_stack.removeWidget(w); w.deleteLater()
        self.dashboard_view = DashboardView(api_client_instance=self.api_client)
        self.agents_view = AgentsView(api_client_instance=self.api_client, base_font=self.base_font)
        self.ad_data_view = ADDataView(base_font=self.base_font)
        self.playbooks_view = PlaybooksView(base_font=self.base_font)
        self.modules_view = ModulesView(base_font=self.base_font)
        self.settings_view = SettingsView(current_c2_url=self.c2_url, base_font=self.base_font)
        self.settings_view.config_changed.connect(self.update_c2_configuration)
        for view in [self.dashboard_view, self.agents_view, self.ad_data_view, self.playbooks_view, self.modules_view, self.settings_view]:
            self.content_stack.addWidget(view)
        cs = self.nav_bar.currentRow(); self.content_stack.setCurrentIndex(cs if cs >=0 else 0)
        # S'assurer que la vue Dashboard reçoit le client API si elle est la première vue affichée
        if self.content_stack.currentWidget() == self.dashboard_view:
            self.dashboard_view.set_api_client(self.api_client)
        elif self.content_stack.currentWidget() == self.agents_view:
             self.agents_view.set_api_client(self.api_client)

    def check_server_connection_status(self):
        if not self.api_client:
            self.dashboard_view.update_server_status(False, "Client API non configuré.")
            self.statusBar().showMessage("Client API non configuré. Vérifiez Paramètres."); return
        if self.status_worker and self.status_worker.isRunning(): return
        self.statusBar().showMessage(f"Vérification statut de {self.c2_url}...")
        self.status_worker = ApiWorker(self.api_client, "check_status")
        self.status_worker.server_status_checked.connect(self.handle_server_status_checked)
        self.status_worker.finished.connect(self.on_status_worker_finished); self.status_worker.start()

    def on_status_worker_finished(self):
        if self.status_worker: self.status_worker.deleteLater(); self.status_worker = None

    def handle_server_status_checked(self, result):
        status_ok, message = result
        self.dashboard_view.update_server_status(status_ok, message)
        s_msg = f"Serveur C2 ({self.c2_url}): {message}" if status_ok else f"Erreur C2 ({self.c2_url}): {message}"
        self.statusBar().showMessage(s_msg, 7000)
        if status_ok and self.content_stack.currentWidget() == self.agents_view:
            self.agents_view.fetch_agents_data()
        if not status_ok and self.isVisible(): 
            QMessageBox.warning(self, "Statut Serveur C2", f"Problème connexion C2 : {message}")

    def change_view(self, index):
        if index < 0 or index >= self.content_stack.count(): return
        self.content_stack.setCurrentIndex(index)
        c_item = self.nav_bar.item(index).text()
        c2_s = self.c2_url if self.api_client else 'Non configuré'
        self.statusBar().showMessage(f"Vue: {c_item} | C2: {c2_s}")
        current_widget = self.content_stack.currentWidget()
        # Transmettre l'instance api_client si la vue a une méthode set_api_client
        if hasattr(current_widget, 'set_api_client'):
            current_widget.set_api_client(self.api_client)
        # Logique spécifique à la vue après changement
        if current_widget == self.agents_view and self.api_client: self.agents_view.fetch_agents_data()
        elif current_widget == self.dashboard_view and self.api_client:
            self.check_server_connection_status()
            self.dashboard_view.refresh_dashboard_data() # Demander au dashboard de se rafraîchir
            
    def closeEvent(self, event):
        # Nettoyage des workers
        if self.status_worker and self.status_worker.isRunning(): self.status_worker.quit(); self.status_worker.wait()
        # Pour AgentsView, le worker est géré localement mais il est bon de s'assurer qu'il s'arrête
        if hasattr(self.agents_view, 'worker') and self.agents_view.worker and self.agents_view.worker.isRunning():
             self.agents_view.worker.quit(); self.agents_view.worker.wait()
        # Idem pour DashboardView
        if hasattr(self.dashboard_view, 'worker') and self.dashboard_view.worker and self.dashboard_view.worker.isRunning():
            self.dashboard_view.worker.quit(); self.dashboard_view.worker.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    # ... (sys.path modification)
    current_script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_script_path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    app = QApplication(sys.argv)
    try: app.setStyle("Fusion")
    except Exception as e: print(f"Note: Style Fusion non disponible ({e}).")
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 