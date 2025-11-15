from PyQt5 import QtGui

from xce.gui_scripts import layout_functions


class RefinementTab:
    def setup(self, xce_object):
        ################################################################################
        #                                                                              #
        #                                REFINEMENT TAB                                #
        #                                                                              #
        ################################################################################
        xce_object.summary_vbox_for_table = QtWidgets.QVBoxLayout()

        # table
        xce_object.refinement_table = QtWidgets.QTableWidget()
        layout_functions.table_setup(
            xce_object.refinement_table, xce_object.refinement_table_columns
        )
        xce_object.summary_vbox_for_table.addWidget(xce_object.refinement_table)
