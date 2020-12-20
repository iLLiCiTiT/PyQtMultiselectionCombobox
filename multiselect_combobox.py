from math import floor
from Qt import QtCore, QtGui, QtWidgets


class ComboItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    Helper styled delegate (mostly based on existing private Qt's
    delegate used by the QtWidgets.QComboBox). Used to style the popup like a
    list view (e.g windows style).
    """

    def paint(self, painter, option, index):
        option = QtWidgets.QStyleOptionViewItem(option)
        option.showDecorationSelected = True

        # option.state &= (
        #     ~QtWidgets.QStyle.State_HasFocus
        #     & ~QtWidgets.QStyle.State_MouseOver
        # )
        super(ComboItemDelegate, self).paint(painter, option, index)


class MultiSelectionComboBox(QtWidgets.QComboBox):
    value_changed = QtCore.Signal()
    ignored_keys = {
        QtCore.Qt.Key_Up,
        QtCore.Qt.Key_Down,
        QtCore.Qt.Key_PageDown,
        QtCore.Qt.Key_PageUp,
        QtCore.Qt.Key_Home,
        QtCore.Qt.Key_End
    }

    top_bottom_padding = 2
    left_offset = 4
    top_bottom_margins = 2
    item_spacing = 5

    item_bg_color = QtGui.QColor("#777777")

    def __init__(
        self, parent=None, placeholder="", separator=", ", **kwargs
    ):
        super(MultiSelectionComboBox, self).__init__(parent=parent, **kwargs)
        self.setObjectName("MultiSelectionComboBox")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self._popup_is_shown = False
        self._block_mouse_release_timer = QtCore.QTimer(self, singleShot=True)
        self._initial_mouse_pos = None
        self._separator = separator
        self.placeholder_text = placeholder
        self.delegate = ComboItemDelegate(self)
        self.setItemDelegate(self.delegate)

        self.lines = {}
        self.item_height = (
            self.fontMetrics().height()
            + (2 * self.top_bottom_padding)
            + (2 * self.top_bottom_margins)
        )
        self.model().rowsInserted.connect(self._on_row_insert)

    def _on_row_insert(self, _parent_index, row_from, row_to):
        for row in range(row_from, row_to + 1):
            self.model().item(row).setCheckable(True)

    def mousePressEvent(self, event):
        """Reimplemented."""
        self._popup_is_shown = False
        super(MultiSelectionComboBox, self).mousePressEvent(event)
        if self._popup_is_shown:
            self._initial_mouse_pos = self.mapToGlobal(event.pos())
            self._block_mouse_release_timer.start(
                QtWidgets.QApplication.doubleClickInterval()
            )

    def showPopup(self):
        """Reimplemented."""
        super(MultiSelectionComboBox, self).showPopup()
        view = self.view()
        view.installEventFilter(self)
        view.viewport().installEventFilter(self)
        self._popup_is_shown = True

    def hidePopup(self):
        """Reimplemented."""
        self.view().removeEventFilter(self)
        self.view().viewport().removeEventFilter(self)
        self._popup_is_shown = False
        self._initial_mouse_pos = None
        super(MultiSelectionComboBox, self).hidePopup()
        self.view().clearFocus()

    def _event_popup_shown(self, obj, event):
        if not self._popup_is_shown:
            return

        current_index = self.view().currentIndex()
        model = self.model()

        if event.type() == QtCore.QEvent.MouseMove:
            if (
                self.view().isVisible()
                and self._initial_mouse_pos is not None
                and self._block_mouse_release_timer.isActive()
            ):
                diff = obj.mapToGlobal(event.pos()) - self._initial_mouse_pos
                if diff.manhattanLength() > 9:
                    self._block_mouse_release_timer.stop()
            return

        index_flags = current_index.flags()
        state = current_index.data(QtCore.Qt.CheckStateRole)
        new_state = None

        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if (
                self._block_mouse_release_timer.isActive()
                or not current_index.isValid()
                or not self.view().isVisible()
                or not self.view().rect().contains(event.pos())
                or not index_flags & QtCore.Qt.ItemIsSelectable
                or not index_flags & QtCore.Qt.ItemIsEnabled
                or not index_flags & QtCore.Qt.ItemIsUserCheckable
            ):
                return

            if state == QtCore.Qt.Unchecked:
                new_state = QtCore.Qt.Checked
            else:
                new_state = QtCore.Qt.Unchecked

        elif event.type() == QtCore.QEvent.KeyPress:
            # TODO: handle QtCore.Qt.Key_Enter, Key_Return?
            if event.key() == QtCore.Qt.Key_Space:
                # toogle the current items check state
                if (
                    index_flags & QtCore.Qt.ItemIsUserCheckable
                    and index_flags & QtCore.Qt.ItemIsTristate
                ):
                    new_state = QtCore.Qt.CheckState((int(state) + 1) % 3)

                elif index_flags & QtCore.Qt.ItemIsUserCheckable:
                    if state != QtCore.Qt.Checked:
                        new_state = QtCore.Qt.Checked
                    else:
                        new_state = QtCore.Qt.Unchecked

        if new_state is not None:
            model.setData(current_index, new_state, QtCore.Qt.CheckStateRole)
            self.view().update(current_index)
            self.update_size_hint()
            self.value_changed.emit()
            return True

    def eventFilter(self, obj, event):
        """Reimplemented."""
        result = self._event_popup_shown(obj, event)
        if result is not None:
            return result

        return super(MultiSelectionComboBox, self).eventFilter(obj, event)

    def paintEvent(self, event):
        """Reimplemented."""
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)
        painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, option)

        # draw the icon and text
        items = self.values(QtCore.Qt.DisplayRole)
        if not items:
            option.currentText = self.placeholder_text
            option.palette.setCurrentColorGroup(QtGui.QPalette.Disabled)
            painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, option)
            return

        for line, items in self.lines.items():
            top_y = (
                option.rect.top()
                + (line * self.item_height)
                + self.top_bottom_margins
            )
            left_x = option.rect.left() + self.left_offset
            for item in items:
                label_rect = option.fontMetrics.boundingRect(item)
                label_height = label_rect.height()

                if label_rect.height() > label_rect.width():
                    radius = floor(label_rect.width() / 4)
                else:
                    radius = floor(label_rect.height() / 4)

                label_rect.moveTop(top_y)

                bg_rect = QtCore.QRectF(label_rect)
                bg_rect.moveLeft(left_x)
                bg_rect.setWidth(label_rect.width() + (2 * radius))

                label_rect.setHeight(self.item_height)

                bg_rect.setHeight(
                    label_height + (2 * self.top_bottom_padding)
                )
                bg_rect.moveTop(bg_rect.top() + self.top_bottom_margins)

                path = QtGui.QPainterPath()
                path.addRoundedRect(bg_rect, radius, radius)

                painter.fillPath(path, self.item_bg_color)

                label_rect.moveLeft(bg_rect.x() + radius)

                painter.drawText(
                    label_rect,
                    QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                    item
                )

                left_x = bg_rect.right() + self.item_spacing

    def resizeEvent(self, *args, **kwargs):
        super(MultiSelectionComboBox, self).resizeEvent(*args, **kwargs)
        self.update_size_hint()

    def update_size_hint(self):
        self.lines = {}

        items = self.values(QtCore.Qt.DisplayRole)
        if not items:
            self.update()
            return

        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)

        height_radius = floor(option.fontMetrics.height() / 4)
        item_with_width = []
        for item in items:
            rect = option.fontMetrics.boundingRect(item)
            if rect.height() > rect.width():
                radius = floor(rect.width() / 4)
            else:
                radius = height_radius

            width = rect.width() + (2 * radius)
            item_with_width.append((item, width))

        btn_rect = self.style().subControlRect(
            QtWidgets.QStyle.CC_ComboBox,
            option,
            QtWidgets.QStyle.SC_ComboBoxArrow
        )
        total_width = option.rect.width() - btn_rect.width()

        line = 0
        self.lines = {line: []}
        left_x = int(self.left_offset)
        for item, width in item_with_width:
            right_x = left_x + width

            if right_x < total_width:
                self.lines[line].append(item)
                left_x += width + self.item_spacing

            elif self.lines.get(line):
                line += 1
                self.lines[line] = [item]
                left_x = self.left_offset + width + self.item_spacing

            else:
                self.lines[line] = [item]
                line += 1
                left_x = int(self.left_offset)

        self.update()
        self.updateGeometry()

    def sizeHint(self):
        value = super(MultiSelectionComboBox, self).sizeHint()
        lines = len(self.lines)
        if lines == 0:
            lines = 1
        value.setHeight(
            (lines * self.item_height)
            + (2 * self.top_bottom_margins)
        )
        return value

    def setItemCheckState(self, index, state):
        self.setItemData(index, state, QtCore.Qt.CheckStateRole)

    def values(self, role=None):
        if role is None:
            role = QtCore.Qt.DisplayRole

        output = list()
        for idx in range(self.count()):
            state = self.itemData(idx, role=QtCore.Qt.CheckStateRole)
            if state == QtCore.Qt.Checked:
                output.append(self.itemData(idx, role=role))
        return output

    def wheelEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        if (
            event.key() == QtCore.Qt.Key_Down
            and event.modifiers() & QtCore.Qt.AltModifier
        ):
            return self.showPopup()

        if event.key() in self.ignored_keys:
            return event.ignore()

        return super(MultiSelectionComboBox, self).keyPressEvent(event)
