import xml.dom.minidom
import application.xml_manager as xmlm
from datetime import datetime, timedelta
import time
import threading

class HdlgenProject:

    def __init__(self, path_to_hdlgen=None):
        # If a HDLGen file isn't provided, assume we are in testing mode.
        self.hdlgen = path_to_hdlgen
        if not path_to_hdlgen:
            self.hdlgen = "C:\\hdlgen\\March\\DSPProc_Threshold_Luke\\DSPProc\\HDLGenPrj\\DSPProc.hdlgen"
        self.hdlgen_path = self.hdlgen.replace("\\", "/")

        self.pynqbuildxml = xmlm.Xml_Manager(self.hdlgen_path)  # This is accessible object we can always call on.

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
        self.environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
        self.location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

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
        AMDproj_folder_rel_path = AMDproj_folder.firstChild.data

        ###################################
        ###### Parse Entity IO Ports ######
        ###################################

        # hdlDesign - entityIOPorts
        hdlDesign = root.getElementsByTagName("hdlDesign")[0]
        entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
        signals = entityIOPorts.getElementsByTagName("signal")

        all_ports = []
        for sig in signals:
            signame = sig.getElementsByTagName("name")[0]
            mode = sig.getElementsByTagName("mode")[0]
            type = sig.getElementsByTagName("type")[0]
            desc = sig.getElementsByTagName("description")[0]
            all_ports.append(
                [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
            )
        self.parsed_ports = self.parse_all_ports(all_ports)
    
        ####################################
        ###### Parse Internal Signals ######
        ####################################

        # hdlDesign - internalSignals
        internalSignals = hdlDesign.getElementsByTagName("internalSignals")[0]
        intsignals = internalSignals.getElementsByTagName("signal")
        
        all_internal = []
        for sig in intsignals:
            signame = sig.getElementsByTagName("name")[0]
            type = sig.getElementsByTagName("type")[0]
            desc = sig.getElementsByTagName("description")[0]
            all_internal.append(
                [signame.firstChild.data, type.firstChild.data, desc.firstChild.data]
            )
        self.parsed_internal_sigs = self.parse_all_internal_sigs(all_internal)
        # self.parsed_internal_sigs = self.parse_all_internal_sigs(all_internal)

        #############################
        ###### Parse Test Plan ######
        #############################

        # Retrieve TB Data from HDLGen
        testbench = root.getElementsByTagName("testbench")[0]
        try:
            TBNote = testbench.getElementsByTagName("TBNote")[0]
            self.TBNoteData = TBNote.firstChild.data
        except Exception:
            self.TBNoteData = None


        self.build_logger = None
        self.synth_logger = None
        self.impl_logger = None

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
        if self.build_logger:
            self.build_logger.add_to_log_box(msg, set)
        else:
            print("No build logger set")

    def add_to_syn_log(self, msg, set=False):
        if self.synth_logger:
            self.synth_logger.add_to_log_box(msg, set)
        else:
            print("No synthesis logger set")

    def add_to_impl_log(self, msg, set=False):
        if self.impl_logger:
            self.impl_logger.add_to_log_box(msg, set)
        else:
            print("No implementation logger set")

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
    
    ###################################
    ########## Build Project ##########
    ###################################
    def set_build_status_page(self, buildstatuspage):
        self.buildstatuspage = buildstatuspage

    def build_project(self, buildstatuspage=None):
        
        self.build_running = True    # Flag that build has started
        self.current_step = None     # Set initalise build_step

        thread1 = threading.Thread(target=self.update_build_status)
        thread2 = threading.Thread(target=self.update_build_status_tester)

        thread1.start()
        thread2.start()

    # Steps?
    # 1) Load the XML configuration
    # 2) Run everything as we need.
    # 2.5) Update Build Status Flags
    # 3) Everything handles it self anyways for most part.

    def update_build_status_tester(self):
        time.sleep(10)
        self.current_step = "gen_tcl"
        time.sleep(10)
        self.current_step = "opn_prj"
        time.sleep(10)
        self.current_step = "bld_bdn"
        time.sleep(10)
        self.current_step = "run_syn"
        time.sleep(10)
        self.current_step = "run_imp"
        time.sleep(10)
        self.current_step = "gen_bit"
        time.sleep(10)
        self.current_step = "gen_jnb"
        time.sleep(10)
        self.current_step = "cpy_dir"
        time.sleep(10)
        self.error_at_build_step = False
        self.build_running = False

    ##############################################
    ########## Update Build Status Page ##########
    ##############################################
    def update_build_status(self):
        # We will need to listen to a number of flags.
        options = ["gen_tcl", "run_viv", "opn_prj", "bld_bdn", "run_syn", "run_imp", "gen_bit", "gen_jnb", "cpy_out"]
        last_time_tcl = "00:00"
        # This function is going to be threaded tfk cos effort.

        # All status boxes need to be set to the "waiting" state.
        # self.buildstatuspage.gen_tcl_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.run_viv_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.run_viv0_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.run_viv1_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.run_viv2_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.run_viv3_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.run_viv4_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.gen_jnb_status_lbl.configure(text="Waiting")
        # self.buildstatuspage.cpy_dir_status_lbl.configure(text="Waiting")
        modes = ["gen_tcl", "opn_prj", "bld_bdn", "run_syn", "run_imp", "gen_bit", "gen_jnb", "cpy_out"]

        for mode in modes:
            self.buildstatuspage.set_build_status(mode, 'waiting')

        while self.build_running:
            time.sleep(1)
            # Need to simply listen for flags
            if self.current_step == "gen_tcl":
                self.buildstatuspage.gen_tcl_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.gen_tcl_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.gen_tcl_status_lbl.configure(text="Running")
            elif self.current_step == "opn_prj":
                self.buildstatuspage.run_viv_statusbar.start()
                self.buildstatuspage.run_viv0_statusbar.start()
                # self.buildstatuspage.run_viv_statusbar.start()
                # self.buildstatuspage.run_viv0_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.run_viv_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv0_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.gen_tcl_status_lbl.configure(text="Complete")
                self.buildstatuspage.run_viv_status_lbl.configure(text="Running")
                self.buildstatuspage.run_viv0_status_lbl.configure(text="Running")
            elif self.current_step == "bld_bdn":
                self.buildstatuspage.run_viv0_statusbar.stop()
                self.buildstatuspage.run_viv1_statusbar.start()
                # self.buildstatuspage.run_viv_statusbar.start()
                # self.buildstatuspage.run_viv0_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.run_viv_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv1_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv0_status_lbl.configure(text="Complete")
                self.buildstatuspage.run_viv_status_lbl.configure(text="Running")
                self.buildstatuspage.run_viv1_status_lbl.configure(text="Running")
            elif self.current_step == "run_syn":
                self.buildstatuspage.run_viv1_statusbar.stop()
                self.buildstatuspage.run_viv2_statusbar.start()
                # self.buildstatuspage.run_viv_statusbar.start()
                # self.buildstatuspage.run_viv0_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.run_viv_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv2_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv1_status_lbl.configure(text="Complete")
                self.buildstatuspage.run_viv_status_lbl.configure(text="Running")
                self.buildstatuspage.run_viv2_status_lbl.configure(text="Running")
            elif self.current_step == "run_imp":
                self.buildstatuspage.run_viv2_statusbar.stop()
                self.buildstatuspage.run_viv3_statusbar.start()
                # self.buildstatuspage.run_viv_statusbar.start()
                # self.buildstatuspage.run_viv0_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.run_viv_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv3_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv2_status_lbl.configure(text="Complete")
                self.buildstatuspage.run_viv_status_lbl.configure(text="Running")
                self.buildstatuspage.run_viv3_status_lbl.configure(text="Running")
            elif self.current_step == "gen_bit":
                self.buildstatuspage.run_viv3_statusbar.stop()
                self.buildstatuspage.run_viv4_statusbar.start()
                # self.buildstatuspage.run_viv_statusbar.start()
                # self.buildstatuspage.run_viv0_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.run_viv_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv4_time_lbl.configure(text=last_time_tcl)
                self.buildstatuspage.run_viv3_status_lbl.configure(text="Complete")
                self.buildstatuspage.run_viv_status_lbl.configure(text="Running")
                self.buildstatuspage.run_viv4_status_lbl.configure(text="Running")
            elif self.current_step == "gen_jnb":
                self.buildstatuspage.gen_tcl_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.gen_tcl_time_lbl.configure(text=last_time_tcl)

            elif self.current_step == "cpy_out":
                self.buildstatuspage.gen_tcl_statusbar.start()
                last_time_tcl = self.add_one_second(last_time_tcl)
                self.buildstatuspage.gen_tcl_time_lbl.configure(text=last_time_tcl)

        if self.error_at_build_step == "gen_tcl":
            pass
        elif self.error_at_build_step == "opn_prj":
            pass
        elif self.error_at_build_step == "bld_bdn":
            pass
        elif self.error_at_build_step == "run_syn":
            pass
        elif self.error_at_build_step == "run_imp":
            pass
        elif self.error_at_build_step == "gen_bit":
            pass
        elif self.error_at_build_step == "gen_jnb":
            pass
        elif self.error_at_build_step == "cpy_out":
            pass
        else:
            print("Build passed")

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