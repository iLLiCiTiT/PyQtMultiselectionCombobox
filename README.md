# PyQtMultiselectionCombobox
Multiselection combobox fot Python's Qt bindings.

## Version 1
First version of implementation can be found in `multiselect_combobox.py`.
![version 1](./version1_example.gif)
Inherit from `QComboBox` so most of logic is same. To get values use `values` method which return list of checked items. You can specify `role` that will be used to return value by default is used role `QtCore.Qt.DisplayRole` (text).

Background of selected items can't be set with stylesheet. To do so change `item_bg_color` attribute on object or in class definition.

---

## Version 2
Is in progress. Should use QListView with removable items out of menu.

### TODOs:
- [ ] Use QListView as viewer of selection
- [ ] Define height of widget
- [ ] Button to show menu
- [ ] Model abstraction for viewer and menu
- [ ] Menu with highlighted selection or other way of visual representation of selected item in menu
- [ ] Others...
