import sys
from Qt import QtWidgets, QtCore, QtGui


class MultiselectionCombobox(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(MultiselectionCombobox, self).__init__(parent)

        model = QtGui.QStandardItemModel()
        view = QtWidgets.QListView(self)
        view.setModel(model)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = view
        self.model = model



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
