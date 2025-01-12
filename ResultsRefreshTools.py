import FreeCAD as App
import FreeCADGui as Gui

import os
from PySide import QtGui
import Serialize_SearchBar
import Parameters_SearchBar as Parameters

genericToolIcon = QtGui.QIcon(QtGui.QIcon(Parameters.genericToolIcon_Pixmap))

# Define the translation
translate = App.Qt.translate


def refreshToolsAction(nfo):
    import RefreshTools

    RefreshTools.refreshToolsAction()


def refreshToolsToolTip(nfo, setParent):
    return (
        Serialize_SearchBar.iconToHTML(genericToolIcon)
        + "<p>"
        + translate(
            "SearchBar",
            "Load all workbenches to refresh the cached results. This may take a minute, depending on the number of installed workbenches.",
        )
        + "</p>"
    )


def refreshToolsResultsProvider():
    return [
        {
            "icon": genericToolIcon,
            "text": translate("SearchBar", "Refresh cached results"),
            "toolTip": "",
            "action": {"handler": "refreshTools"},
            "subitems": [],
        }
    ]
