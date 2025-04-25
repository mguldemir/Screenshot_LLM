from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QAction
from .ui import ScreenshotAnalyzer

class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayApp, self).__init__(icon, parent)
        self.create_menu()
        self.window = None  # Store the window reference

    def create_menu(self):
        menu = QMenu()
        exit_action = QAction("Exit", self, triggered=self.exit_app)
        config_action = QAction("Config", self, triggered=self.config_app)
        menu.addAction(config_action)
        menu.addAction(exit_action)
        self.setContextMenu(menu)
        self.setToolTip("Screenshot LLM")

    def exit_app(self):
        QApplication.quit()
        
    def config_app(self):
        # Only create a new window if one doesn't exist already
        if not self.window:
            try:
                self.window = ScreenshotAnalyzer()
                # Add a safety check for the apply_stylesheet method
                if not hasattr(self.window, 'apply_stylesheet'):
                    # This is a monkey patch to fix the missing method
                    def apply_stylesheet(self):
                        pass
                    setattr(self.window.__class__, 'apply_stylesheet', apply_stylesheet)
            except Exception as e:
                print(f"Error creating ScreenshotAnalyzer: {e}")
                return
                
        # Show the window
        if self.window:
            self.window.show()
