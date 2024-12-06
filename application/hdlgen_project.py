import xml.dom.minidom
import application.xml_manager as xmlm
from datetime import datetime, timedelta
import time
import threading
import os
import application.pynq_manager as pm
import application.hdl_modifier as hdl_modifier
import html
import copy
from application.builder_utils import *
import traceback
class HdlgenProject:

    def __init__(self, path_to_hdlgen=None):
        # If a HDLGen file isn't provided, assume we are in testing mode.
        self.hdlgen = path_to_hdlgen
        # if not path_to_hdlgen:
        #     self.hdlgen = "C:\\hdlgen\\March\\DSPProc_Threshold_Luke\\DSPProc\\HDLGenPrj\\DSPProc.hdlgen"
        self.hdlgen_path = self.hdlgen.replace("\\", "/")
        

        # Load root
        hdlgen = xml.dom.minidom.parse(self.hdlgen_path)
        root = hdlgen.documentElement

        ##############################################
        ###### Get Project Name, Details, Paths ######
        ##############################################

        # Project Manager - Settings
        projectManager = root.getElementsByTagName("projectManager")[0]
        projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
        self.name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
        environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
        location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

        self.environment = environment.replace("\\", "/")   # Make dir safe for use
        self.location = location.replace("\\", "/")


        # HOTFIX: To fix location bug, we are going to pop the last directory from the location variable instead.
        new_path = os.path.dirname(self.location)
        self.environment = new_path


        # Project Manager - EDA
        projectManagerEda = projectManager.getElementsByTagName("EDA")[0]
        tool = projectManagerEda.getElementsByTagName("tool")[0]
        self.vivado_dir = tool.getElementsByTagName("dir")[0].firstChild.data

        # Project Manager - HDL
        projectManagerHdl = projectManager.getElementsByTagName("HDL")[0]
        language = projectManagerHdl.getElementsByTagName("language")[0]
        self.project_language = language.getElementsByTagName("name")[0].firstChild.data

    	# hdlDesign - header
        hdlDesign = root.getElementsByTagName("hdlDesign")[0]
        hdlDesignHeader = hdlDesign.getElementsByTagName("header")[0]
        self.author = hdlDesignHeader.getElementsByTagName("authors")[0].firstChild.data
        self.company = hdlDesignHeader.getElementsByTagName("company")[0].firstChild.data
        self.email = hdlDesignHeader.getElementsByTagName("email")[0].firstChild.data

        # genFolder - VHDL Folders
        genFolder = root.getElementsByTagName("genFolder")[0]
        try:
            model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
            testbench_folder = genFolder.getElementsByTagName("vhdl_folder")[1]
            # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
            # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
            AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
        except Exception:
            model_folder = genFolder.getElementsByTagName("verilog_folder")[0]
            testbench_folder = genFolder.getElementsByTagName("verilog_folder")[1]
            AMDproj_folder = genFolder.getElementsByTagName("verilog_folder")[4]

        self.AMDproj_folder_rel_path = AMDproj_folder.firstChild.data
        self.model_folder_rel_path = model_folder.firstChild.data

        # Model Full Path
        # self.model_file = self.environment + "/" + self.model_folder_rel_path + "/" + self.name   # This is where VHD file is copied into the Vivado project.
        # Vivado COPIES the file in, it is not the model file itself.

        # We need to take the last two directories off of the location dir
        head, tail1 = os.path.split(self.location)
        head, tail2 = os.path.split(head)
        result = os.path.join(tail2, tail1)

        imported_model_file = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".srcs/sources_1/imports/" + tail2 + "/" + self.model_folder_rel_path + "/" + self.name

        model_folder_model_file = self.environment + "/" + self.model_folder_rel_path + "/" + self.name   # This is where VHD file is copied into the Vivado project.
        ext = ""
        if self.project_language == "VHDL":
            ext = ".vhd"
        elif self.project_language == "Verilog":
            ext = ".v"

        # Check if the model file was imported or not
        if os.path.exists(imported_model_file + ext):
            self.model_file = imported_model_file       
        else:
            self.model_file = model_folder_model_file

        ########################################
        ##### Create PYNQ Build XML Object #####   
        ########################################
        self.pynqbuildxml = xmlm.Xml_Manager(self, self.hdlgen_path)  # This is accessible object we can always call on.
        self.pynqbuildxml.check_hdl_modifed_and_handle()

        ###################################
        ###### Parse Entity IO Ports ######
        ###################################

        # hdlDesign - entityIOPorts
        hdlDesign = root.getElementsByTagName("hdlDesign")[0]
        entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
        signals = entityIOPorts.getElementsByTagName("signal")

        self.all_ports = []
        for sig in signals:
            signame = sig.getElementsByTagName("name")[0]
            mode = sig.getElementsByTagName("mode")[0]
            type = sig.getElementsByTagName("type")[0]
            desc = sig.getElementsByTagName("description")[0]
            self.all_ports.append(
                [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
            )
        self.parsed_ports = self.parse_all_ports(self.all_ports)
    
        ####################################
        ###### Parse Internal Signals ######
        ####################################

        # hdlDesign - internalSignals
        internalSignals = hdlDesign.getElementsByTagName("internalSignals")[0]
        intsignals = internalSignals.getElementsByTagName("signal")
        
        self.all_internal = []
        for sig in intsignals:
            signame = sig.getElementsByTagName("name")[0]
            type = sig.getElementsByTagName("type")[0]
            desc = sig.getElementsByTagName("description")[0]
            self.all_internal.append(
                [signame.firstChild.data, type.firstChild.data, desc.firstChild.data]
            )
        self.parsed_internal_sigs = self.parse_all_internal_sigs(self.all_internal)
        # self.parsed_internal_sigs = self.parse_all_internal_sigs(all_internal)

        #############################
        ###### Parse Test Plan ######
        #############################

        # Retrieve TB Data from HDLGen
        testbench = root.getElementsByTagName("testbench")[0]
        try:
            TBNote = testbench.getElementsByTagName("TBNote")[0]
            self.TBNoteData = TBNote.firstChild.data
            self.TBNoteData = html.unescape(self.TBNoteData)    
            # Convert HTML encoded elements into string
        except Exception:
            self.TBNoteData = None

        ###################################
        ##### GUI Object Declarations #####
        ###################################
        self.build_logger = None    # Logger objects with add_to_log_box APIs
        self.synth_logger = None
        self.impl_logger = None

        ############################################
        ##### Derive Vivado Log File Locations #####
        ############################################

        # Note: Synthesis has multiple OOC (Out-of-context) Synthesis locations - Need to figure out how to find them...
        self.syn_log_path = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".runs/" + self.name + "_bd_processing_system7_0_0_synth_1/runme.log"
        # Fortunately Implementation does not have this issue.
        self.impl_log_path = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".runs/impl_1/runme.log"

        # I have not yet figured out how to locate Out-of-context (OOC) Synthesis log files. synth_1/runme.log will update everything at the end.

        # self.syn_log_path = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".runs/" + self.name + "_bd_" + self.name + "_0_0_synth_1/runme.log"
                                                                                                                        #  + "_bd_" + self.name + "_0_0_synth_1/runme.log"
                                                                                                                        #  + "_bd_processing_system7_0_0_synth_1/runme.log"
        
        self.syn_log_path = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".runs/synth_1/runme.log"

        ######################################
        ##### Threading force quit flags #####
        ######################################
        self.build_force_quit_event = threading.Event()
        self.build_running = False
        # self.build_success_event = threading.Event()
        # self.generate_tcl_fail_event = threading.Event()
        # self.execute_vivado_fail_event = threading.Event()
        # self.open_project_fail_event = threading.Event()
        # self.build_block_design_fail_event = threading.Event()
        # self.run_synthesis_fail_event = threading.Event()
        # self.run_implementation_fail_event = threading.Event()
        # self.generate_bitstream_fail_event = threading.Event()
        # self.generate_jupyter_notebook_fail_event = threading.Event()
        # self.copy_output_fail_event = threading.Event()

        ##########################################
        ##### Generate Tcl Derived Variables #####
        ##########################################
        self.path_to_xpr = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".xpr"  # Hotfix change to envrionment
        self.bd_filename = self.name + "_bd"
        # module_source = name
        self.path_to_bd = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".srcs/sources_1/bd"    # hotfix changed to environment
        # XDC Variables
        self.path_to_xdc = self.environment + "/" + self.AMDproj_folder_rel_path + "/" + self.name + ".srcs/constrs_1/imports/generated/"    # hotfix changed to environment
        self.full_path_to_xdc = self.path_to_xdc + "physical_constr.xdc"

        #########################################################################
        ##### Variable used to track what buildstatuspage items are running #####
        #########################################################################
        self.running_build_status_modes = []

        ########################
        ##### Output Paths #####
        ########################
        self.environment = new_path


        self.pynq_build_path = self.environment + "/" + self.name + "/PYNQBuild"
        self.pynq_build_output_path = self.pynq_build_path + "/output"
        self.pynq_build_generated_path = self.pynq_build_path + "/generated"

    ############################################################
    ########## Logger set and add_to_log_box function ##########
    ############################################################
    def set_build_logger(self, build_logger):
        self.build_logger = build_logger

    def set_synth_logger(self, synth_logger):
        self.synth_logger = synth_logger
    
    def set_impl_logger(self, impl_logger):
        self.impl_logger = impl_logger

    def add_to_build_log(self, msg, set=False):
        new_msg = msg.strip() + "\n"
        if self.build_logger:
            self.build_logger.add_to_log_box(msg, set)
        else:
            print("No build logger set")

    def add_to_syn_log(self, msg, set=False):
        new_msg = msg.strip() + "\n"
        if self.synth_logger:
            self.synth_logger.add_to_log_box(new_msg, set)
        else:
            print("No synthesis logger set")

    def add_to_impl_log(self, msg, set=False):
        new_msg = msg.strip() + "\n"
        if self.impl_logger:
            self.impl_logger.add_to_log_box(new_msg, set)
        else:
            print("No implementation logger set")


    ######################################
    ########## Synthesis Logger ##########
    #####################################
    def run_synth_logger(self):

        # Log Paths are derived that the initalising.
        path_to_log = self.syn_log_path # Set the log path.
        
        # Quit Synthesis Logger flag - Available to whole class.
        self.quit_synthesis_logger = False

        # Local variable just for running ...
        waiting_counter = 0

        # The logger is always started before the runme.log is available - we wait for the file to appear then go.

        while not os.path.exists(path_to_log):
            dots = "."*(waiting_counter//2%5)
            self.add_to_syn_log("\nSynthesis is running" + dots, True)
            time.sleep(0.5)
            waiting_counter += 1
            if self.build_force_quit_event.is_set():
                try:
                    self.add_to_syn_log("\nQuit Synthesis Logger Asserted...stopping.")
                finally:
                    return
            # If the quit flag is asserted, we return exiting the function.
            if self.quit_synthesis_logger:
                try:
                    self.add_to_syn_log("\nQuit Synthesis Logger Asserted...stopping.")
                finally:
                    return

        # Start the Status Process
        self.start_build_status_process('run_syn')
            
        with open(path_to_log, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.5)   # No line in buffer, wait 0.5 sec and read again
                else:
                    # Handle line

                    if line == "":
                        time.sleep(0.05)    # Wait 0.05 seconds just to stop infinite loop
                        continue            # If blank line, just skip to next line

                    elif line.startswith("CRITICAL WARNING"):
                        self.add_to_syn_log("\n"+line)
                    elif line.startswith("ERROR"):
                        # Build failed, set error and change build status page to failed
                        # If the line starts with error, print all the remaining lines in the buffer really then quit.
                        self.add_to_syn_log("\n"+line)
                        self.build_force_quit_event.set()   # An error has been detected - Raise quit event.

                        self.fail_build_status_process('run_syn')

                        # Read out the remainder of the file
                        while True:
                            line = file.readline()
                            if not line:    # not line if end of file is reached
                                break
                            self.add_to_syn_log("\n"+line)
                            time.sleep(0.05)

                        return # quit thread as process is complete#
                    
                    elif line.startswith("Synthesis finished with 0 errors,"):
                        # Build successful!!
                        
                        # Read out the remainder of the file
                        while True:
                            line = file.readline()
                            if not line:    # not line if end of file is reached
                                break
                            self.add_to_syn_log("\n"+line)
                            time.sleep(0.05)
                        # Set the build status page flag as completed, and return from the logger.
                        self.end_build_status_process('run_syn')
                        return # quit thread as process is complete.
                    else:
                        self.add_to_syn_log("\n" + line)
                
                if self.build_force_quit_event.is_set():
                    print("Quitting syn as force quit event set.")
                    self.add_to_syn_log("\nQuitting syn as force quit event set.")
                    break

                time.sleep(0.05)

    ###########################################
    ########## Implementation Logger ##########
    ###########################################
    def run_impl_logger(self):

        # Log Paths are derived that the initalising.
        path_to_log = self.impl_log_path # Set the log path.
        
        # Quit Synthesis Logger flag - Available to whole class.
        self.quit_impl_logger = False

        # Local variable just for running ...
        waiting_counter = 0

        # The logger is always started before the runme.log is available - we wait for the file to appear then go.

        while not os.path.exists(path_to_log):
            dots = "."*(waiting_counter//2%5)
            self.add_to_impl_log("\nWaiting for implementation job to start" + dots, True)
            time.sleep(0.5)
            waiting_counter += 1
            if self.build_force_quit_event.is_set():
                try:
                    self.add_to_impl_log("\nQuit Implementation Logger Asserted...stopping.")
                finally:
                    return
            # If the quit flag is asserted, we return exiting the function.
            if self.quit_impl_logger:
                self.add_to_impl_log("\nQuit Implementation Logger Asserted...stopping.")
                return

        # Start the Status Process
        self.start_build_status_process('run_imp')
        self.buildstatuspage.obj_dict['gen_bit']['status'].configure(text="Waiting")
            
        with open(path_to_log, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    time.sleep(1)   # No line in buffer, wait 1 sec and read again
                else:
                    # Handle line

                    if line == "":
                        time.sleep(0.5)     # Wait 0.5 seconds just to stop infinite loop
                        continue            # If blank line, just skip to next line

                    elif line.startswith("CRITICAL WARNING"):
                        self.add_to_impl_log("\n"+line)
                    elif line.startswith("ERROR"):
                        # If the line starts with error, print all the remaining lines in the buffer really then quit.
                        self.add_to_impl_log("\n"+line)
                        self.fail_build_status_process('run_imp')
                        self.build_force_quit_event.set()   # An error has been detected - Raise quit event.

                        # Read out the remainder of the file
                        while True:
                            line = file.readline()
                            if not line:    # not line if end of file is reached
                                break
                            self.add_to_impl_log("\n"+line)
                            time.sleep(0.05)

                        return # quit thread as logging complete.

                    elif "0 Errors encountered." in line:
                        self.end_build_status_process('run_imp')
                        self.start_build_status_process('gen_bit')
                        while True:
                            line = file.readline()
                            if not line:    # not line if end of file is reached
                                break
                            self.add_to_impl_log("\n"+line)
                            time.sleep(0.05)

                        return # quit thread as logging complete.
                    else:
                        self.add_to_impl_log("\n" + line)

                # if self.build_force_quit_event and self.build_force_quit_event.is_set():
                #     self.end_build_status_process('run_imp')
                #     print("Quitting implementation due to quit event.")
                #     break

                # elif not self.build_running:
                #     print("Implementation Logger closing as build is completed.")
                #     self.end_build_status_process('run_imp')
                #     break
                time.sleep(0.05)

    


    ########################################################################
    ########## Parse all ports format from XML into useful format ##########
    ########################################################################
    def parse_all_ports(self, all_ports):
        # All ports recieved as in HDLGen XML.
        #    signame = sig.getElementsByTagName("name")[0]
        #    mode = sig.getElementsByTagName("mode")[0]
        #    type = sig.getElementsByTagName("type")[0]
        #    desc = sig.getElementsByTagName("description")[0]
        # Job here is to convert into:
        # [signal_name, gpio_mode, gpio_width]
        new_array = []
        for io in all_ports:
            gpio_name = io[0]   # GPIO Name
            gpio_mode = io[1]   # GPIO Mode (in/out)
            gpio_type = io[2]   # GPIO Type (single bit/bus/array)

            if (gpio_type == "single bit"):
                gpio_width = 1
            elif (gpio_type[:3] == "bus"):
                # <type>bus(31 downto 0)</type> - Example Type Value
                substring = gpio_type[4:]           # substring = '31 downto 0)'
                words = substring.split()           # words = ['31', 'downto', '0)']
                gpio_width = int(words[0]) + 1      # eg. words[0] = 31
            elif (gpio_type[:5] == "array"):
                print("ERROR: Array mode type is not yet supported :(")
                continue
            else:
                print("ERROR: Unknown GPIO Type")
                print(gpio_type)
                continue
            new_array.append([gpio_name, gpio_mode, gpio_width])
        return new_array
    
    ###################################################################################
    ########## Parse all internal signals format from XML into useful format ##########
    ###################################################################################
    def parse_all_internal_sigs(self, all_ports):
        # All ports recieved as in HDLGen XML.
        #    signame = sig.getElementsByTagName("name")[0]
        #    mode = sig.getElementsByTagName("mode")[0]
        #    type = sig.getElementsByTagName("type")[0]
        #    desc = sig.getElementsByTagName("description")[0]
        # Job here is to convert into:
        # [signal_name, gpio_mode, gpio_width]
        new_array = []
        for io in all_ports:
            gpio_name = io[0]   # GPIO Name
            gpio_type = io[1]   # GPIO Type (single bit/bus/array)

            if (gpio_type == "single bit"):
                gpio_width = 1
            elif (gpio_type[:3] == "bus"):
                # <type>bus(31 downto 0)</type> - Example Type Value
                substring = gpio_type[4:]           # substring = '31 downto 0)'
                words = substring.split()           # words = ['31', 'downto', '0)']
                gpio_width = int(words[0]) + 1      # eg. words[0] = 31
            elif (gpio_type[:5] == "array"):
                print("ERROR: Array mode type is not yet supported :(")
                continue
            else:
                print("ERROR: Unknown GPIO Type, ignoring")
                continue
                # print(gpio_type)
            new_array.append([gpio_name, gpio_width])
        return new_array
    
    #############################################
    ##### Start Build Status Page Reference #####
    #############################################
    def set_build_status_page(self, buildstatuspage):
        self.buildstatuspage = buildstatuspage

    def set_save_project_function(self, save_project):
        self.save_project = save_project

    #########################
    ##### Build Project #####
    #########################
    def build_project(self):
        
        self.save_project(self.pynqbuildxml)

        self.add_to_build_log(f"\nBuild project commencing @ {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")

        # Try change current tab to the Build Status tab
        try:
            self.buildstatuspage.tabview.set("Build Status")
        except Exception as e:
            print(f"Could not set tab to build tab: {e}")

        self.build_running = True    # Flag that build has started
        self.current_step = None     # Set initalise build_step

        # Start Build Status Updater Thread
        self.add_to_build_log(f"\nStarting Build Status Updater Thread")
        thread1 = threading.Thread(target=self.build_status_process)
        thread1.start()
        # Delete existing Vivado log files
        self.add_to_build_log(f"\nDeleting existing Vivado .log and .jou files")
        self.remove_vivado_log_jou_files()

        # Create PYNQ Manager Object
        self.add_to_build_log(f"\nLaunching PYNQ Manager")
        self.pm_obj = pm.Pynq_Manager(self.hdlgen_path)

        # Install board files (if not already)
        self.add_to_build_log(f"\nChecking Vivado has PYNQ Z2 board files installed")
        self.pm_obj.get_board_config_exists()

        # Delete old synthesis and implementation log files
        self.add_to_build_log(f"\nDeleting existing Vivado Project Synthesis and Implementation (runme.log) log files")
        self.remove_vivado_syn_impl_log_files()

        try:

            # First things first - Make copy and inject
            hdl_modifier.make_copy_and_inject(self)
            # Start Logger Threads

            # Delete old log files
            self.delete_runme_logs()
            
            # self.add_to_build_log(f"\nStarting Logger Threads (Build, Synth and Impl loggers)")
            # self.build_logger_thread = threading.Thread(target=self.run_build_logger)
            self.synth_logger_thread = threading.Thread(target=self.run_synth_logger)
            self.impl_logger_thread = threading.Thread(target=self.run_impl_logger)
            # self.build_logger_thread.start()
            self.synth_logger_thread.start()
            self.impl_logger_thread.start()

            self.vivado_logger = threading.Thread(target=self.vivado_state_logger)


            # Execute Program
            self.add_to_build_log(f"\nClearing force close threading flag")
            self.build_force_quit_event.clear()
            self.add_to_build_log(f"\nCreating Build Thread")
            build_thread = threading.Thread(target=self.build)
            self.add_to_build_log(f"\nStarting Build Thread")
            build_thread.start()

            # Steps:
            # 1) Load the XML configuration
            # 2) Run everything as we need.
            # 2.5) Update Build Status Flags
            # 3) Everything handles it self anyways for most part.

        finally:
            # self.build_running = False    # Flag that build has stopped for loggers
            pass
            
        
    ##############################################################
    ###### API for Tcl Generator to know what signals to use #####
    ##############################################################
    def get_generate_conn_signals(self):
        # 1) Load parse signals
        # 2) Append internal signals made external.
        # 3) Return in parsed signals format.

        # 1) Parsed signals is our baseline.
        returned_signals = copy.deepcopy(self.parsed_ports)
        # 2) Read our internal signals config
        internal_signals = self.pynqbuildxml.read_internal_to_port_config()
        # Internal_signals is in form: ['name', int(width)]
        # parsed_ports in form: ['name', 'in/out', 'width']
        for signal in internal_signals:
            returned_signals.append([f"int_{signal[0]}", 'out', signal[1]])  # We know the mode will ALWAYS be out - Not forgetting to add _int prefix.

        return returned_signals

    #############################################################
    ###### Used to flag the various stages for Build Status #####
    #############################################################
    def vivado_state_logger(self):
        vivado_log_path = f"{self.pynq_build_generated_path}" + "/vivado.log"
        # If the vivado.log file hasn't been created yet just wait 1 second.
        
        while not os.path.exists(vivado_log_path):
            self.add_to_build_log("\nWaiting for Vivado to launch...")
            time.sleep(1)
            if self.build_force_quit_event.is_set():
                self.add_to_build_log("\nQuitting Vivado Logger - Quit flag asserted")
                return

        waiting_counter = 0
        # We can progress once the program is open.
        with open(vivado_log_path, 'r') as vivado_log:
            while True:
                if self.build_force_quit_event.is_set():
                    self.add_to_build_log("\nQuitting Vivado Logger - Quit flag asserted")
                    return

                # Will return to this depending on our flag scheme
                # if self.current_running_mode != "run_viv":
                #         break

                line = vivado_log.readline()
                if not line:
                    time.sleep(1)   # No line is available, wait a second
                else:
                    if line == "":
                        pass    # Skip empty lines
                    elif line[0] == '#':
                        pass    # this line just has the tcl script we sourced
                    elif line.startswith("CRITICAL WARNING"):
                        self.add_to_build_log("\n"+line)
                    elif line.startswith("ERROR"):
                        # If an error is detected, we want to set the flag as error.
                        self.add_to_build_log("\n"+line.strip())
                        # Read out the remainder of the lines in buffer
                        while True:
                            line = vivado_log.readline()
                            if not line:
                                break
                            self.add_to_build_log("\n"+line.strip())
                            time.sleep(0.05)
                        # Build failed, set error and change build status page to failed
                        # If the line starts with error, print all the remaining lines in the buffer really then quit.
                        self.build_force_quit_event.set()   # An error has been detected - Raise quit event.

                        self.fail_build_status_process('bld_bdn')
                        self.add_to_build_log("\n\nVivado raised an error and the build could not complete. Please check the log above for more details")
                        self.add_to_build_log("\nBuild is quitting.")
                    elif "open_project" in line:
                        print("OPEN_PROJECT FOUND")
                        self.start_build_status_process('opn_prj')
                        self.add_to_build_log(f"\nOpening Vivado Project {self.path_to_xpr}")
                        self.add_to_build_log("\n" + line.strip())
                    elif "create_bd_design" in line:
                        self.end_build_status_process('opn_prj')
                        self.start_build_status_process('bld_bdn')
                        self.add_to_build_log(f"\nCreating BD Design: {self.path_to_bd}")
                        self.end_build_status_process('opn_prj') ## Force Open Project to stop if it hasn't already.
                        self.add_to_build_log("\n"+line)
                    elif "_0_0_synth_1" in line:
                        self.end_build_status_process('bld_bdn')
                        self.end_build_status_process('opn_prj') ## Force Open Project to stop if it hasn't already.
                        self.buildstatuspage.obj_dict['run_syn']['status'].configure(text="Preparing")
                        self.add_to_build_log("\nStarting Synthesis of Design")
                        self.add_to_build_log("\n"+line.strip())
                    elif "Launched impl_1..." in line:
                        self.add_to_build_log("\nLaunching Implementation\n" +line)
                        self.add_to_build_log(vivado_log.readline())
                    elif "Waiting for impl_1 to finish..." in line:
                        # dots = "."*(waiting_counter//2%5)
                        # if waiting_counter == 0:
                            # self.log_data = self.log_data + "\nWaiting for synthesis & implementation to complete, see syn/impl log tabs for more details"
                        # self.add_to_build_log(self.log_data + dots, True)
                        # time.sleep(0.5)
                        # waiting_counter += 1
                    # elif "" in line:
                        pass
                    elif "Command: write_bitstream -force" in line:
                        self.add_to_build_log("\nGenerating Bitstream")
                        self.start_build_status_process('gen_bit')    
                    elif "write_bitstream completed successfully" in line:
                        self.end_build_status_process('gen_bit')
                        self.add_to_build_log("\nBitstream written successfully.")
                    elif "exit" in line:
                        self.add_to_build_log("\nExit command issued to Vivado. Waiting for Vivado to close.")
                        self.add_to_build_log("\nMoving to next process")
                        return # All dun
                if not self.build_running:
                    return # all dun
                    
    ###################################################################################
    ##### Code to run before commencing a build and to run before closing a build #####
    ###################################################################################
    def build_start(self):
        self.build_running = True
        self.buildstatuspage.build_running = True
        self.lock_sidebar()

    def build_end(self):
        # Some cleanup/completion activities
        self.buildstatuspage.build_running = False
        hdl_modifier.restore(self)
        self.build_running = False
        # self.unlock_sidebar()         # Don't unlock sidebar until reset runs are fixed.
        # Complete.

    ########################################################
    ###### Build thread - Called by build_project func #####
    ########################################################
    def build(self):
        
        self.build_start()

        # Generate TCL
        self.start_build_status_process('gen_tcl')
        self.generate_tcl()
        self.end_build_status_process('gen_tcl')

        if self.build_force_quit_event.is_set():
            self.fail_build_status_process('gen_tcl')
            self.build_end()
            return

        # Run Vivado
        self.start_build_status_process('run_viv')
        self.vivado_logger.start()
        self.run_vivado()
        self.end_build_status_process('run_viv')

        if self.build_force_quit_event.is_set():
            self.fail_build_status_process('run_viv')
            self.build_end()
            return

        # Generate JNB
        self.start_build_status_process('gen_jnb')
        
        if (self.generate_jnb()):
            self.end_build_status_process('gen_jnb')
        else:  
            self.fail_build_status_process('gen_jnb')
        # Copy to Directory
        self.start_build_status_process('cpy_out')
        self.copy_output()
        self.end_build_status_process('cpy_out')

        if self.build_force_quit_event.is_set():
            self.fail_build_status_process('cpy_out')
            self.build_end()
            return

        self.build_end()

    ################################################
    ###### Generate Tcl - Called by build func #####
    ################################################
    def generate_tcl(self):
        
        if self.build_force_quit_event.is_set():
            self.add_to_build_log("\n\nTcl Generation cancelled as force quit flag asserted!")
            print("\n\nTcl Generation cancelled as force quit flag asserted!")
            return # Return to leave function
        try:
            self.pm_obj.generate_tcl(self, self.add_to_build_log)
        except Exception as e:
            self.add_to_build_log(f"\nTcl Generation failed due to the following error:{e}")
            self.build_force_quit_event.set()

    ################################################
    ###### Run Vivado - Called by build func #####
    ################################################
    def run_vivado(self):

        if self.build_force_quit_event.is_set():
            self.add_to_build_log("\n\nRun Vivado cancelled as force quit flag asserted!")
            print("\n\nRun Vivado cancelled as force quit flag asserted!")
            return # Return to leave function

        self.pm_obj.run_vivado(self, self.add_to_build_log)

    ###################################################
    ###### Generate Jupyter Notebook (Full Build) #####
    ###################################################
    def generate_jnb(self):
        # A separate API only for generating JNB
        if self.build_force_quit_event.is_set():
            self.add_to_build_log("\n\nGenerate JNB cancelled as force quit flag asserted!")
            print("\n\nGenerate JNB cancelled as force quit flag asserted!")
            return # Return to leave function
        try:
            self.pm_obj.generate_jnb(self, self.add_to_build_log)
            return True
        except Exception as e:
            print(f"\nNotebook Generation failed due to the following error:" + traceback.print_exc)
            self.add_to_build_log(f"\nNotebook Generation failed due to the following error:" + traceback.print_exc)
            # self.build_force_quit_event.set()     # Generate JNB shouldn't assert this because it doesn't imped other functions
            return False


    ########################################################
    ###### Generate Jupyter Notebook (No Vivado Build) #####
    ########################################################
    def generate_jnb_solo(self):
        self.lock_sidebar()
        # Create PYNQ Manager Object
        self.add_to_build_log(f"\nLaunching PYNQ Manager")
        self.pm_obj = pm.Pynq_Manager(self.hdlgen_path)
        # We are gonna need a 'force gen' option in the gen_jnb api as the switch could be deassert in config file.
        
        try:
            self.pm_obj.generate_jnb(self, self.add_to_build_log, force_gen=True)
        except Exception as e:
            print(f"\nNotebook Generation failed due to the following error:" + traceback.print_exc)
            self.add_to_build_log(f"\nNotebook Generation failed due to the following error:" + traceback.print_exc)
            self.build_force_quit_event.set()
        self.unlock_sidebar()

    ########################################################
    ###### Copy Output Files (Full Build) #####
    ########################################################  
    def copy_output(self):
        print("now copying output...")
        if self.build_force_quit_event.is_set():
            self.add_to_build_log("\n\nCopy Output cancelled as force quit flag asserted!")
            print("\n\nCopy Output cancelled as force quit flag asserted!")
            return # Return to leave function

        try:
            print("all abord the copy ")
            self.pm_obj.copy_to_dir(self)
        except Exception as e:
            self.add_to_build_log(f"\nError: {e}")


    ##########################################################
    ###### Delete Vivado Log Files (.log, .jou from CWD) #####
    ##########################################################
    def remove_vivado_log_jou_files(self):
        
        # Find Vivado log file and delete it.
        try:
            vivado_log_path = f"{self.pynq_build_generated_path}" + "/vivado.log"
            os.remove(vivado_log_path)
            print("Successfully deleted Vivado.log file")
        except FileNotFoundError:
            print("No vivado.log file to delete")
        except Exception as e:
            print(f"An error occured: {e}")
        
        # Note: -nojournal flag added to Vivado args so this section no longer needed
        # Find Vivado jou file and delete it.
        # try:
        #     vivado_jou_path = get_resource_path('vivado.jou', os.path.abspath(__file__))
        #     os.remove(vivado_jou_path)
        #     print("Successfully deleted Vivado.jou file")
        # except FileNotFoundError:
        #     print("No vivado.jou file to delete")
        # except Exception as e:
        #     print(f"An error occured: {e}")

    ####################################################################
    ###### Delete Project Log Files (runme.log for synth and impl) #####
    ####################################################################
    def remove_vivado_syn_impl_log_files(self):
        # Delete old Synthesis Log
        if os.path.exists(self.syn_log_path):
            # If it exists, delete the file
            os.remove(self.syn_log_path)
            print(f"The file {self.syn_log_path} has been deleted.")
        else:
            print(f"The file {self.syn_log_path} does not exist.")

        # Delete old Implementation Log
        if os.path.exists(self.impl_log_path):
            # If it exists, delete the file
            os.remove(self.impl_log_path)
            print(f"The file {self.impl_log_path} has been deleted.")
        else:
            print(f"The file {self.impl_log_path} does not exist.")


    ###########################################################
    ########## Update Build Status Page (Full Build) ##########
    ###########################################################

    def start_build_status_process(self, mode):

        # Check that the mode exists.
        try:
            self.buildstatuspage.obj_dict[mode]
        except KeyError:
            print("Mode not found in start_build_status_process")
            return
        except Exception as e:
            print(f"start_build_status_process: {e}")
            return

        # Add the dictionary to the list of processes currently running.    
        self.running_build_status_modes.append(mode)
        # Then we want to start the process.
        self.buildstatuspage.set_build_status(mode, 'running')

    def end_build_status_process(self, mode):
        if mode in self.running_build_status_modes:
            self.running_build_status_modes.remove(mode)
        self.buildstatuspage.set_build_status(mode, 'success')
        
    def fail_build_status_process(self, mode):
        if mode in self.running_build_status_modes:
            self.running_build_status_modes.remove(mode)
        self.buildstatuspage.set_build_status(mode, 'failed')

    def build_status_process(self):
        # Need this to keep running for as long as the build is running.
        while True:
            time.sleep(1)
            self.buildstatuspage.increment_time(self.running_build_status_modes)

            if not self.build_running or self.build_force_quit_event.is_set():
                return


    ################################################
    ########## Add Second to MM:SS string ##########
    ################################################
    def add_one_second(self, time_str):
        # Convert the time string to a datetime object
        time_obj = datetime.strptime(time_str, "%M:%S")
        
        # Add one second to the time object
        new_time_obj = time_obj + timedelta(seconds=1)
        
        # Convert the new time object back to the string format
        new_time_str = new_time_obj.strftime("%M:%S")
        
        return new_time_str
    
    #######################################################################
    ########## Delete existing runme.log files (synth/impl logs) ##########
    #######################################################################
    def delete_runme_logs(self):
        if os.path.exists(self.syn_log_path):
            # Delete the file
            os.remove(self.syn_log_path)
            print(f"File '{self.syn_log_path}' deleted successfully.")
        else:
            print(f"File '{self.impl_log_path}' does not exist.")

        if os.path.exists(self.impl_log_path):
            # Delete the file
            os.remove(self.impl_log_path)
            print(f"File '{self.impl_log_path}' deleted successfully.")
        else:
            print(f"File '{self.impl_log_path}' does not exist.")


    ################################
    ##### Sidebar Menu Options #####
    ################################
    # Used to lock the build button when the program is running.
    def set_sidebar_lock_function(self, lock):
        self.lock_sidebar = lock

    def set_sidebar_unlock_function(self, unlock):
        self.unlock_sidebar = unlock