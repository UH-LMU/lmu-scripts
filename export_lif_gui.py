from export_lif import LifExporter
from iterate_lif import iterateLif
from ij.io import DirectoryChooser,OpenDialog

def main():
    """
    Download iterate_lif.py, export_lif.py and export_lif_gui.py.

    Then in Fiji:
    Plugins -> Install Plugin... iterate_lif.py
    Plugins -> Install Plugin... export_lif.py
    File -> New -> Script...
    Script Editor -> File -> Open... export_lif_gui.py
    Script Editor -> Run
    """
    filename = OpenDialog("Choose LIF").getPath()
    if not filename:
        # user canceled dialog
        return
    exportDir = DirectoryChooser("Choose export directory").getDirectory()
    if not exportDir:
        # user canceled dialog
        return

    exporter = LifExporter(exportDir)

    iterateLif(filename,exporter)

if __name__ == "__main__":
    main()
