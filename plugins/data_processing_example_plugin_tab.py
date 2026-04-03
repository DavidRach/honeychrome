"""
Honeychrome Plugin Template
---------------------------
This module defines the interface for a Honeychrome tabbed plugin.

Required Attributes:
    plugin_name (str): The display name used for the tab in the main window.
    plugin_enabled (bool): Toggle to True to load the plugin into the UI.
    PluginWidget (class): the widget to be displayed in the tab

Technical Requirements:
    - Framework: PySide6 (Qt for Python)
"""
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel, QComboBox
from PySide6.QtCore import Qt
from honeychrome.view_components.exportable_plot_widget import ExportablePlotWidget
from honeychrome.view_components.ordered_multi_sample_picker import OrderedMultiSamplePicker

plugin_name = 'Data Processing Example Plugin'
plugin_enabled = True

class PluginWidget(QWidget):
    """
    The main UI container for the plugin.

    Required arguments:
        bus: the signals to communicate with the rest of the honeychrome app
        controller: the honeychrome controller including all ephemeral data and the experiment model
    """
    def __init__(self, bus=None, controller=None, parent=None):
        super().__init__(parent)
        self.bus = bus
        self.controller = controller

        # --- Create widget, scroll area and layouts to hold the plugin content ---
        self.label = QLabel('Data Processing Example')
        self.label_disabled = QLabel('Data Processing Example: unmixed data not available. Set up the spectral model first.')

        # the content widget goes in a scroll widget, which goes in the PluginWidget
        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)

        # make this widget scrollable and resizeable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(self.content_widget)

        overall_layout = QVBoxLayout(self)
        overall_layout.addWidget(self.label_disabled)
        overall_layout.addWidget(scroll)

        # --- Add gui objects for a data processing workflow ---

        # Add sample picker
        self.picker = OrderedMultiSamplePicker(title="Choose Source Samples for Processing")
        # Add gate selection combobox
        self.gate_combo = QComboBox()
        self.gate_combo.addItem("Select Gate:")  # placeholder for "no selection"

        # --- Add gui elements ---
        self.build_button = QPushButton('Build model')
        self.build_button.setToolTip('Runs the process on selected samples')
        self.build_button.clicked.connect(self.build)

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.picker)
        self.main_layout.addWidget(self.gate_combo)
        self.main_layout.addWidget(self.build_button)
        self.main_layout.addStretch()

        self.bus.modeChangeRequested.connect(self.initialise_gui)

    def initialise_gui(self, mode):
        # re-iniitialise if user selects this tab
        if mode == plugin_name:
            # only if unmixing already done
            if self.controller.experiment.process['unmixing_matrix'] is not None:
                self.label_disabled.setVisible(False)
                self.content_widget.setVisible(True)

                selection = self.picker.get_ordered_list()
                if not selection:
                    # populate sample picker if selection wasn't already made
                    all_samples = self.controller.experiment.samples['all_samples']
                    source_samples_relative_to_raw = [str(Path(sample).relative_to(self.controller.experiment.settings['raw']['raw_samples_subdirectory']))
                                                      for sample in all_samples]
                    self.picker.set_items(source_samples_relative_to_raw)

                if self.gate_combo.currentText() == "Select Gate:":
                    # populate gate selection if selection wasn't already made
                    self.gate_combo.clear()
                    self.gate_combo.addItem("Select Gate:")  # placeholder for "no selection"
                    unmixed_gate_names = ['root'] + [g[0].lower() for g in self.controller.unmixed_gating.get_gate_ids()]
                    self.gate_combo.addItems(unmixed_gate_names)

            else:
                self.label_disabled.setVisible(True)
                self.content_widget.setVisible(False)

    def build(self):
        print('Build!')

        from matplotlib import pyplot as plt
        figure, ax = plt.subplots(1)
        ax.plot([0,1],[0,1],'-.')
        plot_widget = ExportablePlotWidget(figure)
        self.main_layout.addWidget(plot_widget)

