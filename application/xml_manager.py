import xml.dom.minidom
import os
import xml.etree.ElementTree as ET
import application.hdl_modifier as hdlm

class Xml_Manager:
    ########################################
    ##### Initalize Xml_Manager Object #####
    ########################################
    def __init__(self, hdlgen_prj, hdlgen_path):
        self.hdlgen_prj = hdlgen_prj
        self.hdlgen_path = hdlgen_path
        # The very first thing we want to do is check
        #   0) Read the HDLGen XML for relevant filepaths
        #   1) Does the folder we need exist
        #   2) Does the XML we need exist
        #   3) Validate the XML
        # Done
        hdlgen = xml.dom.minidom.parse(self.hdlgen_path)
        root = hdlgen.documentElement

        # Project Manager - Settings
        projectManager = root.getElementsByTagName("projectManager")[0]
        projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
        self.name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
        self.environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
        self.location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data
        
        # {location}/PYNQBuild/
        self.pynq_build_path = self.location + "/PYNQBuild"
        self.pynq_build_path = self.pynq_build_path.replace("\\", "/")

        # Check the XML exists
        self.check_project_xml_exists()

    ###########################################################
    ##### Check Project XML Exists (if not, generate one) #####
    ###########################################################
    def check_project_xml_exists(self):
        pynq_build_dir_exists = os.path.exists(self.pynq_build_path)
        pynq_build_config_exists = os.path.exists(self.pynq_build_path + "/PYNQBuildConfig.xml")
        if pynq_build_dir_exists:
            print("PYNQ Build Folder Exists")
        else:
            print("PYNQ Build Folder doesn't exist. Creating...")
            os.makedirs(self.pynq_build_path)

        if pynq_build_config_exists:
            print("PYNQ Build Config XML Exists")
        else:
            print("Creating Project XML")
            self.create_config_xml()

    #############################################
    #############################################
    ##### Check XML Modifed Flag and Handle #####
    def check_hdl_modifed_and_handle(self):
        # Read the HDL Modified Parameter and then 
        hdl_is_modified = False
        try:    
            hdl_is_modified = self.read_hdl_modified_flag()
        except Exception as e:
            print(f"No HDL Modified flag to read: {e}")
        print(hdl_is_modified)
        if hdl_is_modified == True:
            hdlm.restore(self.hdlgen_prj)
        else:
            print("HDL Modifed is False - No restore")
    #########################################
    ##### Create Config XML - Empty XML #####
    #########################################
    def create_config_xml(self):
        # Create root element
        root = ET.Element("PYNQBuild")

        # Settings Child Element
        settings = ET.SubElement(root, "settings")

        # ioConfig Child Element
        ioConfig = ET.SubElement(root, "ioConfig")

        # internalSignal Child Element
        internalSignals = ET.SubElement(root, "internalSignals")

        # flags Child Element
        flags = ET.SubElement(root, "flags")

        # Create XML tree
        tree = ET.ElementTree(root)
        tree.write(self.pynq_build_path + "/PYNQBuildConfig.xml")

    #########################################
    ##### Read the PYNQ Board IO Config #####
    #########################################
    def read_io_config(self, io_configuration=None):
        io_config = {}
        if io_configuration==None:
            # Load our default config dictionary
            io_config = {
                "led0":"None",
                "led1":"None",
                "led2":"None",
                "led3":"None",
                "led4_b":"None",
                "led4_g":"None",
                "led4_r":"None",
                "led5_b":"None",
                "led5_g":"None",
                "led5_r":"None"
            }
        else:
            io_config = io_configuration

        # Load file
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Load root node <PYNQBuild>
        root = buildconfig.documentElement
        # Find ioConfig node
        ioConfig = root.getElementsByTagName("ioConfig")[0]
        # Load Connections
        connections = root.getElementsByTagName("connection")
        # Scan connections, return updated IO Map
        for connection in connections:
            io = connection.getElementsByTagName("io")[0].firstChild.data
            signal = connection.getElementsByTagName("signal")[0].firstChild.data
            pin = connection.getElementsByTagName("pin")[0].firstChild.data
            # If the connection goes nowhere, ignore it.
            if signal == None or io == "None":
                continue

            # Add to IO Map
            try:
                before = io_config[io] # Do this to raise a key error if the IO doesn't exist in IO Map
                print(io, signal, pin)
                io_config[io] = [signal, int(pin)]
            except KeyError:
                print(f"The IO ({io}) could not be found in IO map provided. Ignoring connection for: {signal}")
            except Exception as e:
                print(f"Error Reading IO Config: {e}")

        print(f"Loaded the following io config from file: \n{io_config}")
        return io_config
    
    #######################################
    ##### Write PYNQ Boarfd IO Config #####
    #######################################
    def write_io_config(self, io_config):
        # Load File
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Find root
        root = buildconfig.documentElement
        # Find ioConfig tag
        ioConfig = root.getElementsByTagName("ioConfig")[0]
        # Load connections
        connections = ioConfig.getElementsByTagName("connection")
        # Delete all existing connections
        try:
            for connection in connections:
                ioConfig.removeChild(connection)
        except:
            print("No elements to delete")

        for pynq_io, comp_io in io_config.items():
            if comp_io == None or comp_io == "None" or comp_io == ['', 0]:
                continue    # Skip empty connections

            connection = buildconfig.createElement("connection")

            signal = buildconfig.createElement("signal")
            signal_text = buildconfig.createTextNode(str(comp_io[0]))
            signal.appendChild(signal_text)

            pin = buildconfig.createElement("pin")
            pin_text = buildconfig.createTextNode(str(comp_io[1]))
            pin.appendChild(pin_text)

            io = buildconfig.createElement("io")
            io_text = buildconfig.createTextNode(str(pynq_io))
            io.appendChild(io_text)

            connection.appendChild(io)
            connection.appendChild(signal)
            connection.appendChild(pin)

            root.getElementsByTagName("ioConfig")[0].appendChild(connection)

        with open(self.pynq_build_path + "/PYNQBuildConfig.xml", "w") as xml_file:
            buildconfig.writexml(xml_file, addindent="  ", newl='\n', encoding='')

        self.remove_blank_lines(self.pynq_build_path + "/PYNQBuildConfig.xml")

    ###########################################
    ##### Read SoC Builder Project Config #####
    ###########################################
    def read_proj_config(self):
        # Load our default config dictionary
        proj_config = {
            "open_viv_gui": True,
            "keep_viv_opn": False,
            "gen_jnb": True,
            "use_tstpln": True,
            "use_board_io": True,
            "regen_bd": True
        }

        # Load file
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Load root node <PYNQBuild>
        root = buildconfig.documentElement
        # Find ioConfig node
        settings = root.getElementsByTagName("settings")
        # Scan connections, return updated IO Map
        try:
            for entry in settings[0].getElementsByTagName('entry'):
                
                try:
                    name = entry.getElementsByTagName("name")[0].firstChild.data
                    value = entry.getElementsByTagName("value")[0].firstChild.data
                    if value == 'True':
                        value = True
                    elif value == 'False':
                        value = False
                except:
                    print("No entries")
                    continue
                # Add to IO Map
                try:
                    before = proj_config[name] # Do this to raise a key error if the IO doesn't exist in IO Map
                    proj_config[name] = value
                except KeyError:
                    print(f"Adding new key to dictionary {name} with value {value}")
                    proj_config[name] = value

        except Exception as e: 
            print(f"Error reading settings, using defaults: {e}")
            print(f"XML has invalid format - Regenerating a fresh XML.")
            self.create_config_xml()

        print(f"Loaded the following proj config from file: \n{proj_config}")
        return proj_config
    
    ############################################
    ##### Write SoC Builder Project Config #####
    ############################################
    def write_proj_config(self, proj_config):
        # Load File
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Find root
        root = buildconfig.documentElement
        # Find settings
        settings = root.getElementsByTagName("settings")
        # Delete all existing connections
        try:
            for entry in settings[0].getElementsByTagName("entry"):
                settings[0].removeChild(entry)
        except Exception as e:
            print(f"No elements to delete {e}")

        for setting, val in proj_config.items():

            entry = buildconfig.createElement("entry")

            name = buildconfig.createElement("name")
            setting_text = buildconfig.createTextNode(str(setting))
            name.appendChild(setting_text)

            value = buildconfig.createElement("value")
            value_text = buildconfig.createTextNode(str(val))
            value.appendChild(value_text)

            entry.appendChild(name)
            entry.appendChild(value)

            root.getElementsByTagName("settings")[0].appendChild(entry)

        with open(self.pynq_build_path + "/PYNQBuildConfig.xml", "w") as xml_file:
            buildconfig.writexml(xml_file, addindent="  ", newl='\n', encoding='')

        self.remove_blank_lines(self.pynq_build_path + "/PYNQBuildConfig.xml")

    #####################################################################
    ##### Remove Blank Lines from XML File (Makes XML more legible) #####
    #####################################################################
    def remove_blank_lines(self, file):
        # Read in all lines
        with open(file, 'r') as f_in:
            lines = f_in.readlines()
        # Write lines that are not blank
        with open(file, 'w') as f_out:
            for line in lines:
                if line.strip():  # Check if the line is not blank
                    f_out.write(line)

    ######################################################################################
    ##### Write Internal Signals to Connect to Port (name without _int prefix/width) #####
    ######################################################################################
    def write_internal_to_port_config(self, internal_signal_config):
        # Write internal signal mapping to XML.
        # <portName>int_ExampleSig</portName>
        # <portWidth>int_ExampleSig</portWidth>

        # Load File
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Find root
        root = buildconfig.documentElement
        # Find settings
        internalSigs = root.getElementsByTagName("internalSignals")
        # Delete all existing connections
        try:
            for entry in internalSigs[0].getElementsByTagName("signal"):
                internalSigs[0].removeChild(entry)
        except Exception as e:
            print(f"No elements to delete {e}")

        for sig in internal_signal_config:
            internal_signal_name = sig[0]
            gpio_width = sig[1]

            entry = buildconfig.createElement("signal")

            name = buildconfig.createElement("name")
            name_text = buildconfig.createTextNode(str(internal_signal_name))
            name.appendChild(name_text)

            width = buildconfig.createElement("width")
            width_text = buildconfig.createTextNode(str(gpio_width))
            width.appendChild(width_text)

            entry.appendChild(name)
            entry.appendChild(width)

            root.getElementsByTagName("internalSignals")[0].appendChild(entry)

        with open(self.pynq_build_path + "/PYNQBuildConfig.xml", "w") as xml_file:
            buildconfig.writexml(xml_file, addindent="  ", newl='\n', encoding='')

        self.remove_blank_lines(self.pynq_build_path + "/PYNQBuildConfig.xml")

    #####################################################################################
    ##### Read Internal Signals to Connect to Port (name without _int prefix/width) #####
    #####################################################################################
    def read_internal_to_port_config(self):
        loaded_config = []
        # Load file
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Load root node <PYNQBuild>
        root = buildconfig.documentElement
        # Find ioConfig node
        intSignals = root.getElementsByTagName("internalSignals")
        # Scan connections, return updated IO Map
        try:
            for entry in intSignals[0].getElementsByTagName('signal'):
                try:
                    name = entry.getElementsByTagName("name")[0].firstChild.data
                    width = int(entry.getElementsByTagName("width")[0].firstChild.data)
                    loaded_config.append([name, width])
                except ValueError:
                    print(f"Invalid value error when loading internal signal {name} with width {width} - Skipping.")
                except:
                    print("No entries")
                    continue

        except Exception as e: 
            print(f"Error reading internal signals config - Skipping: {e}")

        print(f"Loaded internal signal config: {loaded_config}")
        return loaded_config
    
    ##################################
    ##### Read HDL Modified Flag #####
    ##################################
    # This flag is set to True if the HDL is modified (and a backup is not restored).
    def read_hdl_modified_flag(self):
        return self.read_flag_value('hdl_modified')

    ###################################
    ##### Clear HDL Modified Flag #####
    ###################################
    def clear_hdl_modified_flag(self):
        self.set_flag_and_value('hdl_modified', 'False')

    #################################
    ##### Set HDL Modified Flag #####
    #################################
    def set_hdl_modified_flag(self):
        self.set_flag_and_value('hdl_modified', 'True')

    ##############################
    ##### Set Flag and Value #####
    ##############################
    def set_flag_and_value(self, flag, value):
        # Under the <flags> node, set a flag for "hdl_modified"
        flag_name = flag
        flag_value = value

        # Load File
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Find root
        root = buildconfig.documentElement
        # Find flags
        flags = root.getElementsByTagName("flags")
        # Delete all existing hdl_modified flags (should only ever be one anyways).
        try:
            for flag in flags[0].getElementsByTagName(flag_name):
                flags[0].removeChild(flag)
        except Exception as e:
            print(f"No elements to delete {e}")

        # Create a new tag and give it value "True"


        new_flag = buildconfig.createElement(flag_name)
        new_flag_value = buildconfig.createTextNode(flag_value)
        new_flag.appendChild(new_flag_value)

        root.getElementsByTagName("flags")[0].appendChild(new_flag)

        with open(self.pynq_build_path + "/PYNQBuildConfig.xml", "w") as xml_file:
            buildconfig.writexml(xml_file, addindent="  ", newl='\n', encoding='')

        self.remove_blank_lines(self.pynq_build_path + "/PYNQBuildConfig.xml")


    #####################
    ##### Read Flag #####
    #####################
    def read_flag_value(self, flag):
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Load root node <PYNQBuild>
        root = buildconfig.documentElement
        # Find flags node
        flags = root.getElementsByTagName("flags")

        try:
            for entry in flags[0].getElementsByTagName(flag):
                try:
                    value = entry.firstChild.data
                    return value
                except ValueError:
                    print(f"Error reading {flag} flag from file, assuming False.")
                    return False
                except:
                    print("No entries")
                    continue

        except Exception as e: 
            print(f"Couldn't read {flag}: {e} - returning False")
        return False
