import multiprocessing
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView

from xce.gui_scripts import layout_functions


class PanddaTab:
    def setup(self, xce_object):
        ################################################################################
        #                                                                              #
        #                                  PANDDA TAB                                  #
        #                                                                              #
        ################################################################################
        # list of subtabs in PanDDA tab
        pandda_tab_list = [
            "pandda.analyse",
            "Dataset Summary",
            "Processing Output",
            "pandda.inspect",
            "pandda2.inspect",
            "Statistical Map Summaries",
        ]

        # setup tab widget, set up tab dict, and make tab dict
        xce_object.pandda_tab_widget = QtWidgets.QTabWidget()
        xce_object.pandda_tab_dict = {}
        layout_functions.make_tab_dict(
            pandda_tab_list, xce_object.pandda_tab_widget, xce_object.pandda_tab_dict
        )

        # pandda analyse subtab
        # setup a grid to hold everything
        grid_pandda = QtWidgets.QGridLayout()
        grid_pandda.setColumnStretch(0, 20)
        grid_pandda.setRowStretch(0, 20)

        # table - left
        xce_object.pandda_analyse_data_table = QtWidgets.QTableWidget()
        layout_functions.table_setup(
            xce_object.pandda_analyse_data_table, xce_object.pandda_table_columns
        )

        # add table to grid
        frame_pandda = QtWidgets.QFrame()
        grid_pandda.addWidget(xce_object.pandda_analyse_data_table, 0, 0)

        # status of pandda job - under table
        xce_object.pandda_status = "UNKNOWN"
        xce_object.pandda_status_label = QtWidgets.QLabel()

        # status options [filename, test to output, colour of text]
        pandda_status_options = [
            ["/pandda.done", "Finished!", "color: green"],
            ["/pandda.running", "Running...", "color: orange"],
            [
                "/pandda.errored",
                "Error encountered... please check the log files for pandda!",
                "color: red",
            ],
        ]

        # enumerate text options and set text under table
        for option in pandda_status_options:
            if os.path.exists(str(xce_object.panddas_directory + option[0])):
                xce_object.pandda_status = option[1]
                xce_object.pandda_status_label.setStyleSheet(option[2])

        xce_object.pandda_status_label.setText(
            str("STATUS: " + xce_object.pandda_status)
        )
        xce_object.pandda_status_label.setFont(
            QtGui.QFont("Arial", 25, QtGui.QFont.Bold)
        )
        grid_pandda.addWidget(xce_object.pandda_status_label, 3, 0)

        header_font = QtGui.QFont()
        header_font.setBold(True)

        # input parameters for PANDDAs run - right
        frame_right = QtWidgets.QFrame()

        xce_object.pandda_analyse_input_params_vbox = QtWidgets.QVBoxLayout()

        # data directory section
        pandda_input_dir_hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Input data directory:")
        label.setFont(header_font)
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_input_data_dir_entry = QtWidgets.QLineEdit()
        xce_object.pandda_input_data_dir_entry.setText(
            os.path.join(xce_object.initial_model_directory, "*")
        )
        pandda_input_dir_hbox.addWidget(xce_object.pandda_input_data_dir_entry)
        xce_object.select_pandda_input_dir_button = QtWidgets.QPushButton(
            "Select Input Template"
        )
        xce_object.select_pandda_input_dir_button.clicked.connect(
            xce_object.select_pandda_input_template
        )
        pandda_input_dir_hbox.addWidget(xce_object.select_pandda_input_dir_button)
        xce_object.pandda_analyse_input_params_vbox.addLayout(pandda_input_dir_hbox)

        # pdb style section
        pandda_pdb_style_hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("pdb style")
        pandda_pdb_style_hbox.addWidget(label)
        xce_object.pandda_pdb_style_entry = QtWidgets.QLineEdit()
        xce_object.pandda_pdb_style_entry.setText("dimple.pdb")
        pandda_pdb_style_hbox.addWidget(xce_object.pandda_pdb_style_entry)
        xce_object.pandda_analyse_input_params_vbox.addLayout(pandda_pdb_style_hbox)

        # mtz style section
        pandda_mtz_style_hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("mtz style")
        pandda_mtz_style_hbox.addWidget(label)
        xce_object.pandda_mtz_style_entry = QtWidgets.QLineEdit()
        xce_object.pandda_mtz_style_entry.setText("dimple.mtz")
        pandda_mtz_style_hbox.addWidget(xce_object.pandda_mtz_style_entry)
        xce_object.pandda_analyse_input_params_vbox.addLayout(pandda_mtz_style_hbox)

        print((xce_object.initial_model_directory))
        data_dir_string = xce_object.initial_model_directory.replace("/*", "")

        def copy_ligands(obj):
            os.system(
                str(
                    "find "
                    + data_dir_string
                    + '/*/compound -name "*.cif" | while read line; do  echo ${line//"'
                    + data_dir_string
                    + '"/"'
                    + xce_object.panddas_directory
                    + '/processed_datasets/"}| while read line2;+'
                    " do cp $line ${line2//compound/ligand_files} > /dev/null 2>&1; "
                    "done; done;"
                )
            )

            os.system(
                str(
                    "find "
                    + data_dir_string
                    + '/*/compound -name "*.pdb" | while read line; do  echo ${line//"'
                    + data_dir_string
                    + '"/"'
                    + xce_object.panddas_directory
                    + '/processed_datasets/"}| while read line2;'
                    + " do cp $line ${line2//compound/ligand_files} > /dev/null 2>&1; "
                    "done; done;"
                )
            )

            print("==> XCE: Copied ligand restraints over")

        # output directory section
        pandda_output_dir_hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Output directory:")
        label.setFont(header_font)
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_output_data_dir_entry = QtWidgets.QLineEdit()
        xce_object.pandda_output_data_dir_entry.setText(xce_object.panddas_directory)
        pandda_output_dir_hbox.addWidget(xce_object.pandda_output_data_dir_entry)
        xce_object.select_pandda_output_dir_button = QtWidgets.QPushButton(
            "Select PanDDA Directory"
        )
        xce_object.select_pandda_output_dir_button.clicked.connect(
            xce_object.settings_button_clicked
        )
        pandda_output_dir_hbox.addWidget(xce_object.select_pandda_output_dir_button)
        xce_object.pandda_analyse_input_params_vbox.addLayout(pandda_output_dir_hbox)

        pandda_add_ligands_button = QtWidgets.QPushButton(
            "Copy Ligand restraints for PanDDA"
        )
        pandda_add_ligands_button.clicked.connect(lambda: copy_ligands(xce_object))
        xce_object.pandda_analyse_input_params_vbox.addWidget(pandda_add_ligands_button)

        # spacer to separate out sections
        spacer = QtWidgets.QLabel(" ")
        xce_object.pandda_analyse_input_params_vbox.addWidget(spacer)

        label = QtWidgets.QLabel("Submission parameters")
        label.setFont(header_font)
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)

        # qstat or local machine
        label = QtWidgets.QLabel("Submit via:")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_submission_mode_selection_combobox = QtWidgets.QComboBox()
        xce_object.pandda_submission_mode_selection_combobox.addItem("slurm")
        xce_object.pandda_submission_mode_selection_combobox.addItem("local machine")
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_submission_mode_selection_combobox
        )

        # number of processors section
        label = QtWidgets.QLabel("Number of processors:")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_nproc = multiprocessing.cpu_count() - 1
        xce_object.pandda_nproc_entry = QtWidgets.QLineEdit()
        xce_object.pandda_nproc_entry.setText(
            str(xce_object.pandda_nproc).replace(" ", "")
        )
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_nproc_entry
        )

        xce_object.pandda_analyse_input_params_vbox.addWidget(spacer)

        params_hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("PanDDA parameters")
        label.setFont(header_font)
        params_hbox.addWidget(label)

        url_html = (
            '<a href="https://pandda.bitbucket.io/pandda/manual.html">'
            "For docs: click here"
            "</a>"
        )
        label = QtWidgets.QLabel()
        label.setText(url_html)
        label.setOpenExternalLinks(True)
        label.setAlignment(QtCore.Qt.AlignRight)
        params_hbox.addWidget(label)

        xce_object.pandda_analyse_input_params_vbox.addLayout(params_hbox)

        # checkbox for wilson scaling
        xce_object.wilson_checkbox = QtWidgets.QCheckBox("Wilson B-factor Scaling")
        layout_functions.add_checkbox(
            xce_object, xce_object.wilson_checkbox, "xce_object.set_run_dimple_flag"
        )
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.wilson_checkbox
        )

        # crystal form option
        label = QtWidgets.QLabel("Use space group of reference file as filter:")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        # reference file combobox, label with spg display
        hbox = QtWidgets.QHBoxLayout()
        # xce_object.reference_file_list = xce_object.get_reference_file_list('')
        xce_object.pandda_reference_file_selection_combobox = QtWidgets.QComboBox()
        xce_object.populate_reference_combobox(
            xce_object.pandda_reference_file_selection_combobox
        )
        xce_object.pandda_reference_file_selection_combobox.activated[str].connect(
            xce_object.change_pandda_spg_label
        )
        hbox.addWidget(xce_object.pandda_reference_file_selection_combobox)
        xce_object.pandda_reference_file_spg_label = QtWidgets.QLabel()
        hbox.addWidget(xce_object.pandda_reference_file_spg_label)
        xce_object.pandda_analyse_input_params_vbox.addLayout(hbox)

        # how to order events
        label = QtWidgets.QLabel("Order events by:")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_sort_event_combobox = QtWidgets.QComboBox()
        pandda_events = ["cluster_size", "z_peak"]
        layout_functions.populate_combobox(
            pandda_events, xce_object.pandda_sort_event_combobox
        )
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_sort_event_combobox
        )

        # how calculate mean map
        label = QtWidgets.QLabel("Calculate average map by:")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_calc_map_combobox = QtWidgets.QComboBox()
        average_map = ["mean_map", "median_map"]
        layout_functions.populate_combobox(
            average_map, xce_object.pandda_calc_map_combobox
        )
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_calc_map_combobox
        )

        # minimum number of datasets
        label = QtWidgets.QLabel("min_build_datasets")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_min_build_dataset_entry = QtWidgets.QLineEdit()
        xce_object.pandda_min_build_dataset_entry.setText("40")
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_min_build_dataset_entry
        )

        # maximum number of datasets
        label = QtWidgets.QLabel("max_new_datasets")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_max_new_datasets_entry = QtWidgets.QLineEdit()
        xce_object.pandda_max_new_datasets_entry.setText("300")
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_max_new_datasets_entry
        )

        # grid spacing
        label = QtWidgets.QLabel(
            "grid_spacing (default=0.5)\n"
            "Note: higher values speed up calculations, but maps might be less pretty)"
        )
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_grid_spacing_entry = QtWidgets.QLineEdit()
        xce_object.pandda_grid_spacing_entry.setText("0.5")
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_grid_spacing_entry
        )

        # keyword arguments (pandda2)
        label = QtWidgets.QLabel("keyword arguments (pandda2 only)")
        xce_object.pandda_analyse_input_params_vbox.addWidget(label)
        xce_object.pandda_keyword_arguments_entry = QtWidgets.QLineEdit()
        xce_object.pandda_keyword_arguments_entry.setText("")
        xce_object.pandda_analyse_input_params_vbox.addWidget(
            xce_object.pandda_keyword_arguments_entry
        )

        frame_right.setLayout(xce_object.pandda_analyse_input_params_vbox)

        grid_pandda.addWidget(frame_right, 0, 1, 5, 5)
        frame_pandda.setLayout(grid_pandda)

        # these are still currently populated in XCE.py - change
        xce_object.pandda_map_list = QtWidgets.QComboBox()
        xce_object.pandda_maps_html = QWebEngineView()

        # statistical map summaries vbox, add to vbox and add to layout
        xce_object.pandda_map_layout = QtWidgets.QVBoxLayout()
        pandda_map_layout_widgets = [
            xce_object.pandda_map_list,
            xce_object.pandda_maps_html,
        ]
        layout_functions.add_to_box(
            xce_object.pandda_map_layout, pandda_map_layout_widgets
        )
        xce_object.pandda_maps_html.show()

        xce_object.pandda_analyse_hbox = QtWidgets.QHBoxLayout()
        xce_object.pandda_analyse_hbox.addWidget(frame_pandda)

        # change to do select options

        # create context menu... no idea where this lives again.
        xce_object.popMenu_for_pandda_table = QtWidgets.QMenu()
        ignore = QtWidgets.QAction("ignore selected", xce_object.window)
        exclude_characterisation = QtWidgets.QAction(
            "exclude selected from characterisation", xce_object.window
        )
        exclude_zmap = QtWidgets.QAction(
            "exclude selected from z-map analysis", xce_object.window
        )
        deselect = QtWidgets.QAction("deselect highlighted", xce_object.window)
        ignore.triggered.connect(
            lambda: xce_object.select_sample_for_pandda(option="ignore")
        )
        exclude_characterisation.triggered.connect(
            lambda: xce_object.select_sample_for_pandda(option="char")
        )
        exclude_zmap.triggered.connect(
            lambda: xce_object.select_sample_for_pandda(option="zmap")
        )
        deselect.triggered.connect(
            lambda: xce_object.select_sample_for_pandda(option="deselect")
        )
        xce_object.popMenu_for_pandda_table.addAction(ignore)
        xce_object.popMenu_for_pandda_table.addAction(exclude_characterisation)
        xce_object.popMenu_for_pandda_table.addAction(exclude_zmap)
        xce_object.popMenu_for_pandda_table.addAction(deselect)
        xce_object.pandda_analyse_data_table.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        xce_object.pandda_analyse_data_table.customContextMenuRequested.connect(
            xce_object.on_context_menu_pandda
        )

        # next three blocks display html documents created by pandda.analyse
        layout_functions.pandda_html(xce_object)

        xce_object.pandda_initial_html = QWebEngineView()
        xce_object.pandda_initial_html.load(
            QtCore.QUrl(xce_object.pandda_initial_html_file)
        )
        xce_object.pandda_initial_html.show()

        xce_object.pandda_analyse_html = QWebEngineView()
        xce_object.pandda_analyse_html.load(
            QtCore.QUrl(xce_object.pandda_analyse_html_file)
        )
        xce_object.pandda_analyse_html.show()

        xce_object.pandda_inspect_html = QWebEngineView()
        xce_object.pandda_analyse_html.load(
            QtCore.QUrl(xce_object.pandda_inspect_html_file)
        )
        xce_object.pandda_analyse_html.show()

        xce_object.panddas_results_vbox = QtWidgets.QVBoxLayout()
        xce_object.panddas_results_vbox.addWidget(xce_object.pandda_tab_widget)
        xce_object.show_pandda_html_summary()
