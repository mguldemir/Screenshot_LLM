import os
import base64
import markdown
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize, QTimer
from .interface import Ui_MainWindow  # Import the generated UI class
from .local_generate import Worker_Local
from .litellm_generate import Worker_litellm
import dotenv

USER_ROLE = "user"
AI_ROLE = "assistant"
SCRLLM_ENV_FILE = os.getenv("SCRLLM_ENV_FILE", ".env")

class ScreenshotAnalyzer(QMainWindow, Ui_MainWindow):
    def __init__(self, image_path = None):
        super().__init__()
        self.setupUi(self)  # Call setupUi on the instance

        self.image_path = image_path
        self.memory = []
        self.setup_ui()
        self.load_config()
        self.model_id_input.setText(self.LLM_MODEL_ID)
        self.api_key_input.setText(self.LLM_API_MODEL)
        self.icon_scheme_combobox.setCurrentText(self.ICON_SCHEME)

        if self.OLLAMA == "1":
            self.ollama_checkbox.setChecked(True)
        else:
            self.ollama_checkbox.setChecked(False)     

        if self.DARK_MODE == "1":
            self.dark_mode_checkbox.setChecked(True)
        else:
            self.dark_mode_checkbox.setChecked(False)

        if self.ICON_SCHEME != "":
            self.icon_scheme_combobox.setCurrentText(self.ICON_SCHEME)
        else:
            self.icon_scheme_combobox.setCurrentText("default")

        self.setup_loading_animation()

    # Eksik metodlar buraya eklendi
    def apply_stylesheet(self):
        if hasattr(self, 'dark_mode_checkbox') and self.dark_mode_checkbox.isChecked():
            self.setStyleSheet(self.get_dark_stylesheet())
        else:
            self.setStyleSheet(self.get_light_stylesheet())

    def get_light_stylesheet(self):
        return """
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QLabel, QTextEdit, QLineEdit, QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QScrollBar {
                background: #f0f0f0;
                width: 10px;
            }
            QScrollBar::handle {
                background: #c0c0c0;
                border-radius: 5px;
            }
            QScrollBar::handle:pressed {
                background: #a0a0a0;
            }
            QLabel {
                background-color: #f8f8f8;
            }
            QTextEdit, QLineEdit {
                background-color: #f8f8f8;
                color: #333333;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a80d2;
            }
            QPushButton:pressed {
                background-color: #2a70c2;
            }
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #333333;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #4a90e2;
            }
            QCheckBox {
                color: #333333;
            }
            QComboBox {
                background-color: #f8f8f8;
                color: #333333;
                border: none;
                border-radius: 8px;
                padding: 12px
            }
        """

    def get_dark_stylesheet(self):
        return """
            QMainWindow, QWidget {
                background-color: #2c2c2c;
                color: #ffffff;
            }
            QLabel, QTextEdit, QLineEdit, QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QScrollBar {
                background: #3c3c3c;
                width: 10px;
            }
            QScrollBar::handle {
                background: #5c5c5c;
                border-radius: 5px;
            }
            QScrollBar::handle:pressed {
                background: #7c7c7c;
            }
            QLabel {
                background-color: #3c3c3c;
            }
            QTextEdit, QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a80d2;
            }
            QPushButton:pressed {
                background-color: #2a70c2;
            }
            QTabWidget::pane {
                border: none;
                background-color: #2c2c2c;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #2c2c2c;
                color: #4a90e2;
            }
            QCheckBox {
                color: #ffffff;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px
            }
        """
    # Eksik metodların sonu

    def load_config(self):
            dotenv.load_dotenv(SCRLLM_ENV_FILE, override=True)
            self.LLM_API_MODEL = os.getenv("LLM_API_KEY")
            self.LLM_MODEL_ID = os.getenv("LLM_MODEL_ID")
            self.OLLAMA = os.getenv("OLLAMA")        
            self.DARK_MODE = os.getenv("DARK_MODE")
            self.ICON_SCHEME = os.getenv("ICON_SCHEME")

    def setup_ui(self):
        self.display_image()
        self.conversation.setReadOnly(True)
        self.send_button.clicked.connect(self.send_text)
        self.reset_memory.clicked.connect(self.reset)
        self.save_button.clicked.connect(self.save_config)
        self.reset_config.clicked.connect(self.reset_configurations)
        self.entry.returnPressed.connect(self.send_text)
        self.entry.setFocus()
        self.loading_label.setText("")
    
    def save_config(self):
        LLM_API_MODEL = self.api_key_input.text()
        LLM_MODEL_ID = self.model_id_input.text()
        ICON_SCHEME = self.icon_scheme_combobox.currentText()
        with open(SCRLLM_ENV_FILE, "w") as env_file:
            env_file.write(f"LLM_API_KEY={LLM_API_MODEL}\n")
            if LLM_MODEL_ID:
                env_file.write(f"LLM_MODEL_ID={LLM_MODEL_ID}\n")
            else:
                env_file.write(f"LLM_MODEL_ID=\n")
            
            if self.ollama_checkbox.isChecked():
                env_file.write(f"OLLAMA=1\n")
            else:
                env_file.write(f"OLLAMA=0\n")
            if self.dark_mode_checkbox.isChecked():
                env_file.write("DARK_MODE=1\n")
            else:
                env_file.write("DARK_MODE=0\n")
            if ICON_SCHEME:
                env_file.write(f"ICON_SCHEME={ICON_SCHEME}")
            else:
                env_file.write(f"ICON_SCHEME=")
        self.load_config()
        self.model_id_input.setText(self.LLM_MODEL_ID)
        self.api_key_input.setText(self.LLM_API_MODEL)
        self.icon_scheme_combobox.setCurrentText(self.ICON_SCHEME)

        self.show_message("Configuration saved successfully!")


    def reset_configurations(self):
        self.LLM_API_MODEL = None
        self.LLM_MODEL_ID = None
        self.OLLAMA = "1"
        self.ollama_checkbox.setChecked(True)
        self.load_config()
        with open(SCRLLM_ENV_FILE, "w") as env_file:
            env_file.write("LLM_API_KEY=\n")
            env_file.write("LLM_MODEL_ID=\n")
            env_file.write("OLLAMA=1\n")
            env_file.write("DARK_MODE=0\n")
            env_file.write("ICON_SCHEME=default")
        self.show_message("Configuration reset successfully!")
        self.api_key_input.
