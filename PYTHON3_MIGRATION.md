# XChemExplorer Python 3 Migration Documentation

## Overview

This document describes the migration of XChemExplorer from Python 2.7 to Python 3, including all code changes, installation requirements, how to launch the program, and current known issues.

## Migration Status

The Python 3 version launches successfully and the GUI is functional. However, there are authentication issues preventing SLURM cluster job submission.

---

## Code Changes Made

### 1. Python 2 to Python 3 Syntax Fixes

#### HTTP Library Migration
**File**: `xce/lib/cluster/slurm.py`
- Changed: `import httplib` → `import http.client`
- Updated all references: `httplib.HTTPSConnection` → `http.client.HTTPSConnection`

#### Iterator Protocol Updates
**File**: `xce/lib/cluster/slurm.py` (line 140-141)
```python
# Old (Python 2):
final_line = stdout.next()

# New (Python 3):
final_line = next(stdout)
```

#### String Encoding Fixes
Python 3 strings are Unicode by default, so `.encode()` calls were removed where they caused type mismatches:

**Files Modified**:
- `xce/lib/XChemDB.py` (lines 1222, 1300, 1414, 1708)
- `xce/web/process_sqlite.py` (line 418)

```python
# Old (Python 2):
Chem.MolFromSmiles(row["CompoundSMILES"].encode("ascii"))

# New (Python 3):
Chem.MolFromSmiles(row["CompoundSMILES"])
```

---

### 2. PyQt4 → PyQt5 Migration

#### Import Changes (17 files affected)
```python
# Old (Python 2):
from PyQt4 import QtCore, QtGui

# New (Python 3):
from PyQt5 import QtCore, QtGui, QtWidgets
```

**Key Change**: Widget classes moved from `QtGui` to `QtWidgets` module:
- `QtGui.QWidget` → `QtWidgets.QWidget`
- `QtGui.QMainWindow` → `QtWidgets.QMainWindow`
- `QtGui.QPushButton` → `QtWidgets.QPushButton`
- etc.

#### Files Modified:
1. `xce/XChemExplorer.py`
2. `xce/lib/cluster/slurm.py`
3. `xce/gui_scripts/data_collection_tab.py`
4. `xce/gui_scripts/datasets_summary_tab.py`
5. `xce/gui_scripts/deposition_tab.py`
6. `xce/gui_scripts/initial_model_tab.py`
7. `xce/gui_scripts/layout_functions.py`
8. `xce/gui_scripts/maps_and_density_tab.py`
9. `xce/gui_scripts/overview_tab.py`
10. `xce/gui_scripts/pandda_tab.py`
11. `xce/gui_scripts/refinement_tab.py`
12. `xce/gui_scripts/settings_tab.py`
13. `xce/gui_scripts/stylesheet.py`
14. `xce/lib/XChemMain.py`
15. `xce/lib/XChemPANDDA.py`
16. `xce/lib/XChemRefine.py`
17. `xce/lib/XChemUtils.py`

---

### 3. Qt5 API Compatibility Fixes

#### Signal/Slot Connection Syntax (92 occurrences)
**File**: `xce/XChemExplorer.py`

```python
# Old (Qt4):
self.connect(widget, QtCore.SIGNAL("activated(QString)"), handler)

# New (Qt5):
widget.activated[str].connect(handler)
```

Common patterns changed:
- `SIGNAL("activated(QString)")` → `.activated[str].connect()`
- `SIGNAL("clicked()")` → `.clicked.connect()`
- `SIGNAL("currentIndexChanged(int)")` → `.currentIndexChanged.connect()`
- `SIGNAL("toggled(bool)")` → `.toggled.connect()`
- `SIGNAL("cellChanged(int, int)")` → `.cellChanged.connect()`

#### QInputDialog Parameter Change
**File**: `xce/lib/cluster/slurm.py` (line 50-52)

```python
# Old (Qt4):
password, ok = QtWidgets.QInputDialog.getText(
    None, POPUP_TITLE, password_prompt, mode=QtWidgets.QLineEdit.Password
)

# New (Qt5):
password, ok = QtWidgets.QInputDialog.getText(
    None, POPUP_TITLE, password_prompt, echo=QtWidgets.QLineEdit.Password
)
```

#### Layout Margin Method
**File**: `xce/gui_scripts/layout_functions.py` (line 116)

```python
# Old (Qt4):
vbox.setMargin(0)

# New (Qt5):
vbox.setContentsMargins(0, 0, 0, 0)
```

#### Application Object Location
**File**: `xce/gui_scripts/stylesheet.py` (line 86)

```python
# Old (Qt4):
QtGui.qApp.setStyle()

# New (Qt5):
QtWidgets.qApp.setStyle()
```

#### Style Name Change
**File**: `xce/gui_scripts/stylesheet.py`

```python
# Old (Qt4):
QtWidgets.qApp.setStyle("Cleanlooks")

# New (Qt5):
try:
    QtWidgets.qApp.setStyle("Cleanlooks")
except:
    QtWidgets.qApp.setStyle("Fusion")  # Cleanlooks removed in Qt5
```

---

### 4. QtWebEngine Migration

**File**: `xce/gui_scripts/pandda_tab.py`

Added conditional import with fallback for systems without QtWebEngine:

```python
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    class QWebEngineView(QtWidgets.QTextEdit):
        def __init__(self, parent=None):
            super(QWebEngineView, self).__init__(parent)
            self.setReadOnly(True)

        def load(self, url):
            if isinstance(url, QtCore.QUrl):
                url_str = url.toString()
            else:
                url_str = str(url)
            self.setPlainText(f"Web view not available.\nURL: {url_str}")

        def setHtml(self, html):
            self.setPlainText("Web view not available")
```

---

### 5. GTK2 (PyGTK) → GTK3 (PyGObject) Migration

**Files**:
- `xce/lib/cluster/slurm.py`
- `xce/lib/XChemRefine.py`

Added conditional imports to support both Python 2 (PyGTK) and Python 3 (PyGObject):

```python
import sys

# GTK import - migrate from Python 2 PyGTK to Python 3 PyGObject
if sys.version_info[0] >= 3:
    # Python 3: Use PyGObject (GTK3)
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        HAS_GTK = True
        GTK_VERSION = 3
    except (ImportError, ValueError):
        HAS_GTK = False
        GTK_VERSION = None
else:
    # Python 2: Use PyGTK (GTK2)
    try:
        import gtk
        HAS_GTK = True
        GTK_VERSION = 2
    except ImportError:
        HAS_GTK = False
        GTK_VERSION = None
```

Updated password dialog functions to support both GTK versions:

```python
def fetch_password_gtk(password_prompt):
    """
    GTK password dialog for Coot plugins.
    Supports both GTK2 (Python 2) and GTK3 (Python 3).
    """
    if not HAS_GTK:
        error_msg = (
            "GTK is not available but is required for Coot plugins.\n"
            "For Python 3, please install PyGObject:\n"
            "  ccp4-python -m pip install --user PyGObject\n"
            "For Python 2, PyGTK should be pre-installed in CCP4."
        )
        raise ImportError(error_msg)

    if GTK_VERSION == 3:
        # Python 3: GTK3 via PyGObject
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=None,
        )
        dialog.set_title(POPUP_TITLE)
        dialog.set_markup(password_prompt)

        entry = Gtk.Entry()
        entry.set_visibility(False)
        content_area = dialog.get_content_area()
        content_area.pack_end(entry, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        password = entry.get_text() if response == Gtk.ResponseType.OK else None
        dialog.destroy()
        return password

    else:
        # Python 2: GTK2 via PyGTK
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL,
            None,
        )
        dialog.set_title(POPUP_TITLE)
        dialog.set_markup(password_prompt)

        entry = gtk.Entry()
        entry.set_visibility(False)
        dialog.vbox.pack_end(entry)
        dialog.show_all()

        dialog.run()
        password = entry.get_text()
        dialog.destroy()
        return password
```

---

### 6. Matplotlib Backend Update

**File**: `xce/gui_scripts/overview_tab.py`

```python
# Old (Python 2):
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

# New (Python 3):
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
```

---

## Installation Requirements

### Python 3 Version

#### Required Packages (via pip)

1. **PyQt5** (core GUI framework)
   ```bash
   ccp4-python -m pip install --user PyQt5
   ```

2. **PyQtWebEngine** (for web views in PanDDA tab)
   ```bash
   ccp4-python -m pip install --user --only-binary=:all: PyQtWebEngine
   ```

   **Note**: The `--only-binary=:all:` flag prevents building from source, which can cause memory errors.

3. **PyGObject** (for GTK3 dialogs in Coot plugins)
   ```bash
   ccp4-python -m pip install --user PyGObject
   ```

   **⚠️ ISSUE**: PyGObject installation requires system libraries that need admin/root permissions:
   - `gobject-introspection-devel`
   - `cairo-devel`
   - `python3-devel`

   **Workaround**: Contact Diamond IT for system-wide installation, or use Qt dialogs instead of GTK.

#### System Requirements
- CCP4 version 7.0 or higher
- Python 3 (via ccp4-python)
- PHENIX (optional, but recommended)

---

## How to Launch

### Python 2.7 Version (Original - Working)

1. Navigate to the testing directory:
   ```bash
   cd ~/Documents/xce_testing/XChemExplorer
   ```

2. Launch with CCP4 Python 2.7:
   ```bash
   ccp4-python -m xce.XChemExplorer
   ```

### Python 3 Version (Migrated - Has Issues)

1. Navigate to the Python 3 testing directory:
   ```bash
   cd ~/Documents/xce_testing_python3/XChemExplorer
   ```

2. Launch with CCP4 Python 3:
   ```bash
   ccp4-python -m xce.XChemExplorer
   ```

### Monitoring Logs

To monitor the XCE log file in real-time:
```bash
tail -f ~/.xce/xce.log
```

---

## Current Known Issues

### 🔴 CRITICAL: SLURM Authentication Failure (Python 3 Only)

**Status**: Authentication dialog appears and accepts password, but SSH authentication fails.

**Symptoms**:
- Password dialog displays correctly
- User enters password and clicks OK
- Authentication fails with `paramiko.ssh_exception.AuthenticationException`
- Jobs do not submit (no "Submitting job" or "Got response" messages in log)
- Status fields do not update ("Compound status" stays blank instead of "started")

**Error Message**:
```
Traceback (most recent call last):
  File "/home/oqm26972/Documents/xce_testing_python3/XChemExplorer/xce/lib/cluster/slurm.py", line 133, in get_token
    ssh.connect(CLUSTER_BASTION, username=CLUSTER_USER, password=str(password))
  File "/home/oqm26972/Documents/ccp4-8.0/lib/python3.8/site-packages/paramiko/client.py", line 435, in connect
    self._auth(username, password, pkey, key_filenames, allow_agent, look_for_keys, gss_auth, gss_kex, gss_deleg_creds, gss_host, passphrase)
  File "/home/oqm26972/Documents/ccp4-8.0/lib/python3.8/site-packages/paramiko/client.py", line 764, in _auth
    raise saved_exception
  File "/home/oqm26972/Documents/ccp4-8.0/lib/python3.8/site-packages/paramiko/client.py", line 751, in _auth
    self._transport.auth_password(username, password)
  File "/home/oqm26972/Documents/ccp4-8.0/lib/python3.8/site-packages/paramiko/transport.py", line 1614, in auth_password
    return self.auth_handler.wait_for_response(my_event)
  File "/home/oqm26972/Documents/ccp4-8.0/lib/python3.8/site-packages/paramiko/auth_handler.py", line 259, in wait_for_response
    raise e
paramiko.ssh_exception.AuthenticationException: Authentication failed.
```

**Working Behavior (Python 2.7)**:
- Same dialog and workflow works correctly
- Jobs submit successfully
- Log shows: "Submitting job, 'job_name', to Slurm with body: {...}"
- Log shows: "Got response: {...}"
- Status updates to "started"

**Affected Functionality**:
- "Run Dimple on selected MTZ files" button
- "Create CIF/PDB/PNG" button
- Any SLURM cluster job submission

**Code Location**: `xce/lib/cluster/slurm.py:133`

**Potential Causes**:
1. Password encoding differences between Python 2 and 3
   - Currently using `str(password)` in line 133
   - May need to handle Unicode string differently
2. Paramiko version differences in CCP4 Python 2 vs Python 3
3. SSH protocol handling changes in Python 3
4. Character encoding in password dialog (Qt5 returns Unicode strings)

**Next Steps for Debugging**:
1. Compare paramiko versions between Python 2.7 and Python 3 environments
2. Test password encoding (try `.encode('utf-8')`, `.encode('ascii')`, etc.)
3. Add debug logging to capture password type and content (without exposing actual password)
4. Test direct paramiko connection outside of XCE
5. Check if special characters in password cause encoding issues

---

### ⚠️ WARNING: PyGObject Not Installed

**Status**: Cannot install without admin/root permissions

**Impact**:
- Coot plugin GTK dialogs will not work in Python 3
- Falls back to error message with installation instructions
- Qt dialogs (for main XCE GUI) work fine

**Error if GTK functionality is needed**:
```
ImportError: GTK is not available but is required for Coot plugins.
For Python 3, please install PyGObject:
  ccp4-python -m pip install --user PyGObject
For Python 2, PyGTK should be pre-installed in CCP4.
```

**Required System Libraries** (need admin):
- gobject-introspection-devel
- cairo-devel
- python3-devel

**Workaround**: Contact Diamond IT to install system libraries and PyGObject

---

## Testing Workflow

To test changes between Python 2.7 and Python 3 versions:

1. **Test in Python 2.7 baseline** (verify original functionality):
   ```bash
   cd ~/Documents/xce_testing/XChemExplorer
   ccp4-python -m xce.XChemExplorer
   ```

2. **Test in Python 3 migrated version** (verify migration):
   ```bash
   cd ~/Documents/xce_testing_python3/XChemExplorer
   ccp4-python -m xce.XChemExplorer
   ```

3. **Compare behaviors**:
   - GUI appearance and functionality
   - Button clicks and status updates
   - Log file outputs (`tail -f ~/.xce/xce.log`)
   - Job submission and authentication

---

## Git Branch Information

**Development Branch**: `claude/update-python-3-01LaWN7djzJSduepYGynBQmr`

All Python 3 migration changes are committed to this branch.

---

## Summary

The Python 3 migration has successfully updated:
- ✅ Python 2 syntax to Python 3
- ✅ PyQt4 to PyQt5 (all 17 GUI files)
- ✅ Qt4 to Qt5 API calls (92 signal connections + various methods)
- ✅ GTK2 to GTK3 with backward compatibility
- ✅ Matplotlib backend
- ✅ XCE launches and GUI is functional

Still needs resolution:
- ❌ SLURM authentication failure preventing job submission
- ⚠️ PyGObject installation (requires admin for system libraries)

The authentication issue is the primary blocker for full Python 3 compatibility.

---

## References

- Original repository: https://github.com/xchem/XChemExplorer
- PyQt5 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- PyGObject documentation: https://pygobject.readthedocs.io/
- CCP4 documentation: https://www.ccp4.ac.uk/

---

**Last Updated**: 2025-11-15
