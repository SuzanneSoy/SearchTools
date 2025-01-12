import FreeCAD as App
import FreeCADGui as Gui
import os

from PySide6.QtCore import (
    Qt,
    SIGNAL,
    QSize,
    QIdentityProxyModel,
    QPoint,
)
from PySide6.QtWidgets import (
    QTabWidget,
    QSlider,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QLabel,
    QTabWidget,
    QSizePolicy,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QListView,
    QAbstractItemView,
    QWidget,
    QVBoxLayout,
    QApplication,
    QListWidget,
)
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QColor,
    QStandardItemModel,
    QShortcut,
    QKeySequence,
    QStandardItem,
)

from SearchBoxLight import SearchBoxLight
import Parameters_SearchBar as Parameters

genericToolIcon = QIcon(Parameters.genericToolIcon_Pixmap)

globalIgnoreFocusOut = False

# Define the translation
translate = App.Qt.translate


def easyToolTipWidget(html):
    foo = QTextEdit()
    foo.setReadOnly(True)
    foo.setAlignment(Qt.AlignmentFlag.AlignTop)
    foo.setText(html)
    return foo


class SearchBox(QLineEdit):
    # The following block of code is present in the lightweight proxy SearchBoxLight
    """
    resultSelected = QtCore.Signal(int, int)
    """

    @staticmethod
    def lazyInit(self):
        if self.isInitialized:
            return self
        getItemGroups = self.getItemGroups
        getToolTip = self.getToolTip
        getItemDelegate = self.getItemDelegate
        maxVisibleRows = self.maxVisibleRows
        # The following block of code is executed by the lightweight proxy SearchBoxLight
        """
    # Call parent constructor
    super(SearchBoxLight, self).__init__(parent)
    # Connect signals and slots
    self.textChanged.connect(self.filterModel)
    # Thanks to https://saurabhg.com/programming/search-box-using-qlineedit/ for indicating a few useful options
    ico = QIcon(':/icons/help-browser.svg')
    #ico = QIcon(':/icons/WhatsThis.svg')
    self.addAction(ico, QtGui.QLineEdit.LeadingPosition)
    self.setClearButtonEnabled(True)
    self.setPlaceholderText('Search tools, prefs & tree')
    self.setFixedWidth(200) # needed to avoid a change of width when the clear button appears/disappears
    """

        # Save arguments
        # self.model = model
        self.getItemGroups = getItemGroups
        self.getToolTip = getToolTip
        self.itemGroups = None  # Will be initialized by calling getItemGroups() the first time the search box gains focus, through focusInEvent and refreshItemGroups
        self.maxVisibleRows = (
            maxVisibleRows  # TODO: use this to compute the correct height
        )
        # Create proxy model
        self.proxyModel = QIdentityProxyModel()
        # Filtered model to which items are manually added. Store it as a property of the object instead of a local variable, to prevent grbage collection.
        self.mdl = QStandardItemModel()
        # self.proxyModel.setModel(self.model)
        # Create list view
        self.listView = QListView(self)
        self.listView.setWindowFlags(Qt.WindowType.ToolTip)
        self.listView.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.listView.setSelectionMode(self.listView.SelectionMode.SingleSelection)
        self.listView.setModel(self.proxyModel)
        self.listView.setItemDelegate(
            getItemDelegate()
        )  # https://stackoverflow.com/a/65930408/324969
        self.listView.setMouseTracking(True)
        # make the QListView non-editable
        self.listView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Create pane for showing extra info about the currently-selected tool
        # self.extraInfo = QtGui.QLabel()
        self.extraInfo = QWidget()
        self.extraInfo.setWindowFlags(Qt.WindowType.ToolTip)
        self.extraInfo.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.extraInfo.setLayout(QVBoxLayout())
        self.extraInfo.layout().setContentsMargins(0, 0, 0, 0)
        self.setExtraInfoIsActive = False
        self.pendingExtraInfo = None
        self.currentExtraInfo = None
        # Connect signals and slots
        self.listView.clicked.connect(
            lambda x: self.selectResult("select", x)
        )  # This makes all workbenches appear. TODO: findout why, a click event seems not logic
        self.listView.selectionModel().selectionChanged.connect(
            self.onSelectionChanged
        )  # This updates the details when using the keyboard
        # Add custom mouse events. On windows the click events were not working for Searcbar versions 1.2.x and older.
        # These events and their proxies in the SearchBorLight fixes this
        self.listView.mousePressEvent = lambda event: self.proxyMousePressEvent(event)
        self.listView.mouseMoveEvent = lambda event: self.proxyMouseMoveEvent(event)
        self.extraInfo.leaveEvent = lambda event: self.proxyLeaveEvent(event)

        # Note: should probably use the eventFilter method instead...
        wdgctx = Qt.ShortcutContext.WidgetShortcut

        QShortcut(
            QKeySequence(Qt.Key.Key_Down), self, context=wdgctx
        ).activated.connect(self.listDown)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, context=wdgctx).activated.connect(
            self.listUp
        )
        QShortcut(
            QKeySequence(Qt.Key.Key_PageDown), self, context=wdgctx
        ).activated.connect(self.listPageDown)
        QShortcut(
            QKeySequence(Qt.Key.Key_PageUp), self, context=wdgctx
        ).activated.connect(self.listPageUp)

        # Home and End do not work, for some reason.
        # QShortcut(QKeySequence.MoveToEndOfDocument, self, context = wdgctx).activated.connect(self.listEnd)
        # QShortcut(QKeySequence.MoveToStartOfDocument, self, context = wdgctx).activated.connect(self.listStart)
        # QShortcut(QKeySequence(Qt.Key.Key_End), self, context = wdgctx).activated.connect(self.listEnd)
        # QShortcut(QKeySequence('Home'), self, context = wdgctx).activated.connect(self.listStart)

        QShortcut(
            QKeySequence(Qt.Key.Key_Enter), self, context=wdgctx
        ).activated.connect(self.listAccept)
        QShortcut(
            QKeySequence(Qt.Key.Key_Return), self, context=wdgctx
        ).activated.connect(self.listAccept)
        QShortcut(QKeySequence("Ctrl+Return"), self, context=wdgctx).activated.connect(
            self.listAcceptToggle
        )
        QShortcut(QKeySequence("Ctrl+Enter"), self, context=wdgctx).activated.connect(
            self.listAcceptToggle
        )
        QShortcut(QKeySequence("Ctrl+Space"), self, context=wdgctx).activated.connect(
            self.listAcceptToggle
        )

        QShortcut(
            QKeySequence(Qt.Key.Key_Escape), self, context=wdgctx
        ).activated.connect(self.listCancel)

        # Initialize the model with the full list (assuming the text() is empty)
        # self.proxyFilterModel(self.text()) # This is done by refreshItemGroups on focusInEvent, because the initial loading from cache can take time
        self.firstShowList = True
        self.isInitialized = True
        return self

    @staticmethod
    def proxyMousePressEvent(self, event):
        if self.listView.underMouse():
            self.selectResult(mode=None, index=self.listView.currentIndex())
        else:
            event.ignore()
        return

    @staticmethod
    def proxyMouseMoveEvent(self, arg__1):
        index = self.listView.indexAt(arg__1.pos())
        self.listView.setCurrentIndex(index)

        self.setExtraInfo(index)
        # Poor attempt to circumvent a glitch where the extra info pane stays visible after pressing Return
        if not self.listView.isHidden():
            self.showExtraInfo()
        if self.listView.isHidden():
            self.hideExtraInfo()
        return

    @staticmethod
    def refreshItemGroups(self):
        self.itemGroups = self.getItemGroups()
        self.proxyFilterModel(self.text())

    @staticmethod
    def proxyFocusInEvent(self, qFocusEvent):
        # if the extrainfo is under the cursor, don't focus but only show the list
        if self.extraInfo.underMouse():
            self.showList()
            qFocusEvent.ignore()
            return
        if self.firstShowList:
            mdl = QStandardItemModel()
            mdl.appendRow(
                [
                    QStandardItem(
                        genericToolIcon,
                        translate(
                            "SearchBar", "Please wait, loading results from cache…"
                        ),
                    ),
                    QStandardItem("0"),
                    QStandardItem("-1"),
                ]
            )
            self.proxyModel.setSourceModel(mdl)
            self.showList()
            self.firstShowList = False
            Gui.updateGui()
        global globalIgnoreFocusOut
        if not globalIgnoreFocusOut:
            self.refreshItemGroups()
        self.showList()
        super(SearchBoxLight, self).focusInEvent(qFocusEvent)
        return

    @staticmethod
    def proxyFocusOutEvent(self, qFocusEvent):
        global globalIgnoreFocusOut
        if not globalIgnoreFocusOut:
            self.hideList()
            # super(SearchBoxLight, self).focusOutEvent(qFocusEvent)

    @staticmethod
    def proxyLeaveEvent(self, qFocusEvent):
        self.clearFocus()
        self.hideList()
        return

    @staticmethod
    def movementKey(self, rowUpdate):
        currentIndex = self.listView.currentIndex()
        self.showList()
        if self.listView.isEnabled():
            currentRow = currentIndex.row()
            nbRows = self.listView.model().rowCount()
            if nbRows > 0:
                newRow = rowUpdate(currentRow, nbRows)
                index = self.listView.model().index(newRow, 0)
                self.listView.setCurrentIndex(index)

    @staticmethod
    def proxyListDown(self):
        self.movementKey(lambda current, nbRows: (current + 1) % nbRows)

    @staticmethod
    def proxyListUp(self):
        self.movementKey(lambda current, nbRows: (current - 1) % nbRows)

    @staticmethod
    def proxyListPageDown(self):
        self.movementKey(
            lambda current, nbRows: min(
                current + max(1, self.maxVisibleRows / 2), nbRows - 1
            )
        )

    @staticmethod
    def proxyListPageUp(self):
        self.movementKey(
            lambda current, nbRows: max(current - max(1, self.maxVisibleRows / 2), 0)
        )

    @staticmethod
    def proxyListEnd(self):
        self.movementKey(lambda current, nbRows: nbRows - 1)

    @staticmethod
    def proxyListStart(self):
        self.movementKey(lambda current, nbRows: 0)

    @staticmethod
    def acceptKey(self, mode):
        currentIndex = self.listView.currentIndex()
        self.showList()
        if currentIndex.isValid():
            self.selectResult(mode, currentIndex)

    @staticmethod
    def proxyListAccept(self):
        self.acceptKey("select")

    @staticmethod
    def proxyListAcceptToggle(self):
        self.acceptKey("toggle")

    @staticmethod
    def cancelKey(self):
        self.hideList()
        self.clearFocus()

    # QKeySequence::Cancel
    @staticmethod
    def proxyListCancel(self):
        self.cancelKey()

    @staticmethod
    def proxyKeyPressEvent(self, qKeyEvent):
        key = qKeyEvent.key()
        modifiers = qKeyEvent.modifiers()
        self.showList()
        if key == Qt.Key.Key_Home and modifiers & Qt.Key.CTRL != 0:
            self.listStart()
        elif key == Qt.Key.Key_End and modifiers & Qt.Key.CTRL != 0:
            self.listEnd()
        else:
            super(SearchBoxLight, self).keyPressEvent(qKeyEvent)

    @staticmethod
    def showList(self):
        self.setFloatingWidgetsGeometry()
        if not self.listView.isVisible():
            self.listView.show()
        self.showExtraInfo()

    @staticmethod
    def hideList(self):
        self.listView.hide()
        self.hideExtraInfo()

    @staticmethod
    def hideExtraInfo(self):
        self.extraInfo.hide()

    @staticmethod
    def selectResult(self, mode: None, index):
        groupId = int(index.model().itemData(index.siblingAtColumn(2))[0])
        self.hideList()
        # TODO: allow other options, e.g. some items could act as combinators / cumulative filters
        self.setText("")
        self.proxyFilterModel(self.text())
        # TODO: emit index relative to the base model
        self.resultSelected.emit(index, groupId)

    @staticmethod
    def proxyFilterModel(self, userInput):
        # TODO: this will cause a race condition if it is accessed while being modified
        def matches(s):
            return userInput.lower() in s.lower()

        def filterGroup(group):
            if matches(group["text"]):
                # If a group matches, include the entire subtree (might need to disable this if it causes too much noise)
                return group
            else:
                subitems = filterGroups(group["subitems"])
                # if len(subitems) == 0:
                #     self.index = 0
                if len(subitems) > 0 or matches(group["text"]):
                    return {
                        "id": group["id"],
                        "text": group["text"],
                        "icon": group["icon"],
                        "action": group["action"],
                        "toolTip": group["toolTip"],
                        "subitems": subitems,
                    }
                else:
                    return None

        def filterGroups(groups):
            groups = (filterGroup(group) for group in groups)
            return [group for group in groups if group is not None]

        self.mdl = QStandardItemModel()
        self.mdl.appendColumn([])

        def addGroups(filteredGroups, depth=0):
            for group in filteredGroups:
                # TODO: this is not very clean, we should memorize the index from the original itemgroups
                self.mdl.appendRow(
                    [
                        QStandardItem(group["icon"] or genericToolIcon, group["text"]),
                        QStandardItem(str(depth)),
                        QStandardItem(str(group["id"])),
                    ]
                )
                addGroups(group["subitems"], depth + 1)

        addGroups(filterGroups(self.itemGroups))
        self.proxyModel.setSourceModel(self.mdl)
        self.currentExtraInfo = None  # Unset this so that the ExtraInfo can be updated
        # TODO: try to find the already-highlighted item
        indexSelect = 1
        nbRows = self.listView.model().rowCount()
        if nbRows > 0:
            index = self.listView.model().index(indexSelect, 0)
            self.listView.setCurrentIndex(index)
            self.setExtraInfo(index)
        else:
            self.clearExtraInfo()
        # self.showList()

    @staticmethod
    def setFloatingWidgetsGeometry(self):
        def getScreenPosition(widget):
            geo = widget.geometry()
            parent = widget.parent()
            parentPos = (
                getScreenPosition(parent) if parent is not None else QPoint(0, 0)
            )
            return QPoint(geo.x() + parentPos.x(), geo.y() + parentPos.y())

        pos = getScreenPosition(self)
        siz = self.size()
        screen = QApplication.screenAt(pos)
        x = pos.x()
        y = pos.y() + siz.height()
        hint_w = self.listView.sizeHint().width()
        # TODO: this can still bump into the bottom of the screen, in that case we should flip
        w = max(siz.width(), hint_w)
        h = 200  # TODO: set height / size here according to desired number of items
        extraw = w  # choose a preferred width that doesn't change all the time,
        # self.extraInfo.sizeHint().width() would change for every item.
        extrax = x - extraw
        if screen is not None:
            scr = screen.geometry()
            x = min(scr.x() + scr.width() - hint_w, x)
            extraleftw = x - scr.x()
            extrarightw = scr.x() + scr.width() - x
            # flip the extraInfo if it doesn't fit on the screen
            if extraleftw < extraw and extrarightw > extraleftw:
                extrax = x + w
                extraw = min(extrarightw, extraw)
            else:
                extrax = x - extraw
                extraw = min(extraleftw, extraw)
        self.listView.setGeometry(x, y, w, h)
        self.extraInfo.setGeometry(extrax, y, extraw, h)

    @staticmethod
    def proxyOnSelectionChanged(self, selected, deselected):
        # The list has .setSelectionMode(QAbstractItemView.SingleSelection),
        # so there is always at most one index in selected.indexes() and at most one
        # index in deselected.indexes()
        selected = selected.indexes()
        deselected = deselected.indexes()
        if len(selected) > 0:
            index = selected[0]
            self.setExtraInfo(index)
            # Poor attempt to circumvent a glitch where the extra info pane stays visible after pressing Return
            if not self.listView.isHidden():
                self.showExtraInfo()
        elif len(deselected) > 0:
            self.hideExtraInfo()

    @staticmethod
    def setExtraInfo(self, index):
        if self.currentExtraInfo == (index.row(), index.column(), index.model()):
            # avoid useless updates of the extra info window; this also prevents segfaults when the widget
            # is replaced when selecting an option from the right-click context menu
            return
        self.currentExtraInfo = (index.row(), index.column(), index.model())
        # TODO: use an atomic swap or mutex if possible
        if self.setExtraInfoIsActive:
            self.pendingExtraInfo = index
            # print("boom")
        else:
            self.setExtraInfoIsActive = True
            # print("lock")
            # setExtraInfo can be called multiple times while this function is running,
            # so just before existing we check for the latest pending call and execute it,
            # if during that second execution some other calls are made the latest of those will
            # be queued by the code a few lines above this one, and the loop will continue processing
            # until an iteration during which no further call was made.
            while True:
                groupId = str(index.model().itemData(index.siblingAtColumn(2))[0])
                # TODO: move this outside of this class, probably use a single metadata
                # This is a hack to allow some widgets to set the parent and recompute their size
                # during their construction.
                parentIsSet = False

                def setParent(toolTipWidget):
                    nonlocal parentIsSet
                    parentIsSet = True
                    w = self.extraInfo.layout().takeAt(0)
                    while w:
                        if hasattr(w.widget(), "finalizer"):
                            # The 3D viewer segfaults very easily if it is used after being destroyed, and some Python/C++ interop seems to overzealously destroys some widgets, including this one, too soon?
                            # Ensuring that we properly detacth the 3D viewer widget before discarding its parent seems to avoid these crashes.
                            # print('FINALIZER')
                            w.widget().finalizer()
                        if w.widget() is not None:
                            w.widget().hide()  # hide before detaching, or we have widgets floating as their own window that appear for a split second in some cases.
                            w.widget().setParent(None)
                        w = self.extraInfo.layout().takeAt(0)
                    self.extraInfo.layout().addWidget(toolTipWidget)
                    self.setFloatingWidgetsGeometry()

                toolTipWidget = self.getToolTip(groupId, setParent)
                if isinstance(toolTipWidget, str):
                    toolTipWidget = easyToolTipWidget(toolTipWidget)
                if not parentIsSet:
                    setParent(toolTipWidget)
                if self.pendingExtraInfo is not None:
                    index = self.pendingExtraInfo
                    self.pendingExtraInfo = None
                else:
                    break
            # print("unlock")
            self.setExtraInfoIsActive = False

    @staticmethod
    def clearExtraInfo(self):
        # TODO: just clear the contents but keep the widget visible.
        self.extraInfo.hide()

    @staticmethod
    def showExtraInfo(self):
        self.extraInfo.show()
