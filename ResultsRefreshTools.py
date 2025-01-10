import os
from PySide import QtGui
import Serialize_SearchBar
import Parameters_SearchBar as Parameters

genericToolIcon = QtGui.QIcon(QtGui.QIcon(Parameters.genericToolIcon_Pixmap))


def refreshToolsAction(nfo):
    import RefreshTools

    RefreshTools.refreshToolsAction()


def refreshToolsToolTip(nfo, setParent):
    return (
        Serialize_SearchBar.iconToHTML(genericToolIcon)
        + "<p>Load all workbenches to refresh this list of tools. This may take a minute, depending on the number of installed workbenches.</p>"
    )


def refreshToolsResultsProvider():
    return [
        {
            "icon": genericToolIcon,
            "text": "Refresh list of tools",
            "toolTip": "",
            "action": {"handler": "refreshTools"},
            "subitems": [],
        }
    ]
