import umap
import hdbscan
from line_profiler import profile

from PySide6 import QtWidgets, QtGui, QtCore
import numpy as np


class ClusterTable(QtWidgets.QTableWidget):
    def __init__(self, labels, colors):
        # 1. Prepare data
        unique_labels, counts = np.unique(labels, return_counts=True)
        super().__init__(len(unique_labels), 3)

        # 2. Configure Selection Settings
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Select whole rows
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # Allow Ctrl/Shift multi-select
        self.setHorizontalHeaderLabels(["Cluster ID", "Hex Color", "Count"])
        self.verticalHeader().setVisible(False)

        # 3. Populate Data
        # We find the first occurrence of each label to get its color
        label_to_color = {lbl: colors[np.where(labels == lbl)[0][0]] for lbl in unique_labels}

        for i, label in enumerate(unique_labels):
            name = "Noise" if label == -1 else f"Cluster {label}"

            # Column 0: Name
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(name))

            # Column 1: Hex Code (Copyable text) + Color Swatch
            q_color = QtGui.QColor(label_to_color[label])
            hex_code = q_color.name().upper()
            color_item = QtWidgets.QTableWidgetItem(hex_code)
            color_item.setBackground(QtGui.QBrush(q_color))
            # Contrast check: if color is dark, make text white
            if q_color.lightness() < 128:
                color_item.setForeground(QtGui.QBrush(QtCore.Qt.white))
            self.setItem(i, 1, color_item)

            # Column 2: Count
            self.setItem(i, 2, QtWidgets.QTableWidgetItem(str(counts[i])))

        self.resizeColumnsToContents()

    # 4. Handle Copy Logic
    def keyPressEvent(self, event):
        """Override keyPress to catch Ctrl+C"""
        if event.matches(QtGui.QKeySequence.Copy):
            self.copy_selection()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        """Copies selected cells to clipboard in TSV format"""
        selection = self.selectedRanges()
        if not selection:
            return

        rows = sorted(range(selection[0].topRow(), selection[0].bottomRow() + 1))
        columns = sorted(range(selection[0].leftColumn(), selection[0].rightColumn() + 1))

        output = []
        for r in rows:
            row_data = []
            for c in columns:
                it = self.item(r, c)
                row_data.append(it.text() if it else "")
            output.append("\t".join(row_data))

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText("\n".join(output))

@profile
def main():
    import numpy as np

    # Create a dummy NumPy array
    # 3000 samples, 20 dimensions
    n_samples = 3000
    n_features = 20
    data = np.random.rand(n_samples, n_features).astype(np.float32)

    # Creating some "clusters" so the plot isn't just a random blob
    data[:1000] += 2
    data[1000:2000] -= 2

    # Initialize and fit UMAP
    # n_neighbors: controls local vs global structure (5 to 50 is typical)
    # min_dist: controls how tightly points are packed (0.1 is default)

    subsample = data[np.random.choice(np.arange(len(data)), 1000)]
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, transform_queue_size=1.0, n_components=2).fit(subsample)
    embedding = reducer.transform(subsample)

    # Cluster the UMAP output with HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=50, prediction_data=True).fit(embedding)
    labels = clusterer.labels_

    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtWidgets
    import numpy as np
    import sys

    # 1. Setup the Application
    app = QtWidgets.QApplication(sys.argv)
    view = pg.PlotWidget()
    view.show()

    # 3. Create a Color Map
    # We generate a unique color for each cluster ID
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)
    # Using a high-contrast hsv colormap
    colors = [pg.intColor(i, n_clusters) for i in range(n_clusters)]
    # Map each label to its corresponding color
    point_colors = np.array([colors[l % n_clusters] for l in labels])

    # 4. Create the Scatter Plot Item
    # useCache=True and pxMode=True are CRITICAL for performance at this scale
    scatter = pg.ScatterPlotItem(
        size=2,
        pen=None,
        antialias=False, # Disable antialiasing for speed
        useCache=True    # Cache graphics primitives
    )

    # 5. Add data and display
    # Note: Adding 1M points at once can take a few seconds to 'cook' the brushes
    scatter.setData(pos=embedding, brush=point_colors)
    view.addItem(scatter)

    table = ClusterTable(labels, point_colors)
    table.show()


    # --- Later, with a separate data sample ---
    new_data = np.random.rand(500, 20) # New 20D samples

    # 2. Project new data into the SAME 2D space
    new_embedding = reducer.transform(new_data)

    # 3. Classify into the SAME clusters
    # returns labels and probabilities (certainty)
    new_labels, strengths = hdbscan.approximate_predict(clusterer, new_embedding)

    scatter_new = pg.ScatterPlotItem(
        size=2,
        pen=None,
        antialias=False, # Disable antialiasing for speed
        useCache=True    # Cache graphics primitives
    )

    # 5. Add data and display
    # Note: Adding 1M points at once can take a few seconds to 'cook' the brushes
    point_colors_new = np.array([colors[l % n_clusters] for l in new_labels])
    scatter_new.setData(pos=new_embedding, brush=point_colors_new)
    view.addItem(scatter_new)

    app.exec()

    # Plot with cluster colors
    from matplotlib import pyplot as plt
    plt.figure(figsize=(10, 7))
    plt.scatter(embedding[:, 0], embedding[:, 1], c=labels, s=5, cmap='Spectral')
    plt.colorbar(label='Cluster Label')
    plt.title('UMAP + HDBSCAN Clustering', fontsize=15)
    plt.show()

main()