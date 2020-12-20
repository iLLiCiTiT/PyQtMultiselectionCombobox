import sys
from Qt import QtWidgets, QtCore, QtGui


class ViewFilter(QtCore.QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, parent_index):
        index = parent_index.child(source_row, 0)
        checkstate = index.data(QtCore.Qt.CheckStateRole)
        return checkstate == QtCore.Qt.Checked


class MultiselectionCombobox(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(MultiselectionCombobox, self).__init__(parent)

        model = QtGui.QStandardItemModel()

        view_filter = ViewFilter()
        view_filter.setSourceModel(model)

        view = QtWidgets.QListView(self)
        view.setModel(view_filter)

        arrow_btn = QtWidgets.QPushButton("E", self)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(view)
        layout.addWidget(arrow_btn)

        arrow_btn.clicked.connect(self._on_arrow_click)

        self.view = view
        self.model = model
        self.arrow_btn = arrow_btn


    def _on_arrow_click(self):
        pass


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        combobox = QtWidgets.QComboBox()
        multiselect_combobox = MultiselectionCombobox(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(combobox)
        layout.addWidget(multiselect_combobox)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
