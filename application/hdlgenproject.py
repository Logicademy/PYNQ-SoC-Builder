import xml.dom.minidom
import application.xml_manager as xmlm

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