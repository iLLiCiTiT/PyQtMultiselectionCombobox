import sys
from Qt import QtWidgets, QtCore, QtGui


class MultiselectionCombobox(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(MultiselectionCombobox, self).__init__(parent)

        model = QtGui.QStandardItemModel()
        icon_view = QtWidgets.QListView(self)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(icon_view)



class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        combobox = MultiselectionCombobox(self)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(combobox)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
