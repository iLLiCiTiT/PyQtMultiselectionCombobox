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
        view.setResizeMode(QtWidgets.QListView.Adjust)
        view.setFlow(QtWidgets.QListView.LeftToRight)
        view.setLayoutMode(QtWidgets.QListView.Batched)

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

    def addItem(self, icon=None, text=None, userData=None):
        item = QtGui.QStandardItem()
        item.setData(text, QtCore.Qt.DisplayRole)
        item.setData(icon, QtCore.Qt.DecorationRole)
        item.setData(userData, QtCore.Qt.UserRole)
        item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
        self.model.appendRow(item)

    def addItems(self, texts):
        new_items = []
        for text in texts:
            item = QtGui.QStandardItem()
            item.setData(text, QtCore.Qt.DisplayRole)
            item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
            new_items.append(item)

        self.model.invisibleRootItem().appendRows(new_items)

    def _on_arrow_click(self):
        menu = QtWidgets.QMenu()
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            text = index.data(QtCore.Qt.DisplayRole)
            action = QtWidgets.QAction(text, menu)
            menu.addAction(action)
        result = menu.exec_(QtGui.QCursor.pos())
        print(result)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        texts = ["one", "two"]
        combobox = QtWidgets.QComboBox()
        # combobox.setMinimumHeight(100)

        multiselect_combobox = MultiselectionCombobox(self)

        combobox.addItems(texts)
        multiselect_combobox.addItems(texts)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(combobox)
        layout.addWidget(multiselect_combobox)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
