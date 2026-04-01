from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel
from PySide6.QtCore import Qt

# Example honeychrome tabbed plugin
# Required objects:
# - plugin_name (string): sets the name of the tab in the honeychrome main window
# - plugin_enabled (boolean): True to show the plugin tab, False otherwise
# - PluginWidget (QWidget): the Pyside6 widget to be displayed in the tab
# - register(bus, controller) (function): a function to initialise PluginWidget and return the instance
# to be displayed in the tab. Bus is the set of Pyside4 Signals for communication with different parts of
# the Honeychrome app. Controller is the object containing the current data loaded in the app, including
# the experiment model and the ephemeral data.

plugin_name = 'Example Tabbed Plugin'
plugin_enabled = True

class PluginWidget(QWidget):
    def __init__(self, bus=None, controller=None, parent=None):
        super().__init__(parent)
        self.bus = bus
        self.controller = controller

        # --- Create widget, scroll area and layouts to hold the plugin content ---
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)

        # make this widget scrollable and resizeable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(content_widget)

        overall_layout = QVBoxLayout(self)
        overall_layout.addWidget(scroll)


        # --- Add some GUI elements to show functionality ---
        self.label = QLabel('')
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.setToolTip('Refresh data')
        self.refresh_button.clicked.connect(self.initialise)
        self.buttons = QWidget()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.refresh_button)

        self.initialise()

    def initialise(self):
        # initialise plots (if statistics already defined) and initialise menu
        self.label.setText('hello world')


def register(bus=None, controller=None):
    widget = PluginWidget(bus=bus, controller=controller)
    return widget
