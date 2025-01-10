import FreeCAD as App
import FreeCADGui as Gui
from PySide.QtGui import QColor
import os
import sys

# Define the translation
translate = App.Qt.translate

preferences = App.ParamGet("User parameter:BaseApp/Preferences/Mod/FreeCAD-Ribbon")


class Settings:

    # region -- Functions to read the settings from the FreeCAD Parameters
    # and make sure that a None type result is ""
    def GetStringSetting(settingName: str) -> str:
        result = preferences.GetString(settingName)

        if result.lower() == "none":
            result = ""
        return result

    def GetIntSetting(settingName: str) -> int:
        result = preferences.GetInt(settingName)
        if result == "":
            result = None
        return result

    def GetFloatSetting(settingName: str) -> int:
        result = preferences.GetFloat(settingName)
        if result == "":
            result = None
        return result

    def GetBoolSetting(settingName: str) -> bool:
        result = preferences.GetBool(settingName)
        if str(result).lower() == "none":
            result = False
        return result

    def GetColorSetting(settingName: str) -> object:
        # Create a tuple from the int value of the color
        result = QColor.fromRgba(preferences.GetUnsigned(settingName)).toTuple()

        # correct the order of the tuple and divide them by 255
        result = (result[3] / 255, result[0] / 255, result[1] / 255, result[2] / 255)

        return result

    # endregion

    # region - Functions to write settings to the FreeCAD Parameters
    #
    #
    def SetStringSetting(settingName: str, value: str):
        if value.lower() == "none":
            value = ""
        preferences.SetString(settingName, value)
        return

    def SetBoolSetting(settingName: str, value):
        if str(value).lower() == "true":
            Bool = True
        if str(value).lower() == "none" or str(value).lower() != "true":
            Bool = False
        preferences.SetBool(settingName, Bool)
        return

    def SetIntSetting(settingName: str, value: int):
        if str(value).lower() != "":
            preferences.SetInt(settingName, value)


# region - Define the resources ----------------------------------------------------------------------------------------
ICON_LOCATION = os.path.join(os.path.dirname(__file__), "Resources", "Icons")
# endregion ------------------------------------------------------------------------------------------------------------

# The pixmap for the general tool icon
genericToolIcon_Pixmap = os.path.join(ICON_LOCATION, "Tango-Tools-spanner-hammer.svg")
