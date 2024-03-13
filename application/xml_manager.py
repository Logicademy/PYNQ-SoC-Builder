import xml.dom.minidom
import os
import xml.etree.ElementTree as ET

class Xml_Manager:
    def __init__(self, hdlgen_path):
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


    def create_config_xml(self):
        # Create root element
        root = ET.Element("PYNQBuild")

        # Settings Child Element
        settings = ET.SubElement(root, "settings")

        # ioConfig Child Element
        ioConfig = ET.SubElement(root, "ioConfig")

        # Create XML tree
        tree = ET.ElementTree(root)
        tree.write(self.pynq_build_path + "/PYNQBuildConfig.xml")

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
        connections = root.getElementsByTagName("connections")
        # Scan connections, return updated IO Map
        for connection in connections:
            io = connection.getElementsByTagName("io")[0].firstChild.data
            signal = connection.getElementsByTagName("signal")[0].firstChild.data

            # If the connection goes nowhere, ignore it.
            if io == None or io == "None":
                continue

            # Add to IO Map
            try:
                before = io_config[io] # Do this to raise a key error if the IO doesn't exist in IO Map
                io_config[io] = signal
            except KeyError:
                print(f"The IO ({io}) could not be found in IO map provided. Ignoring connection for: {signal}")
        
        print(f"Loaded the following io config from file: \n{io_config}")
        return io_config
    
    def write_io_config(self, io_config):
        # Remove all the old connections

        # Load File
        buildconfig = xml.dom.minidom.parse(self.pynq_build_path + "/PYNQBuildConfig.xml")
        # Find root
        root = buildconfig.documentElement
        # Find ioConfig tag
        ioConfig = root.getElementsByTagName("ioConfig")[0]
        # Load connections
        connections = ioConfig.getElementsByTagName("connections")
        # Delete all existing connections
        for connection in connections:
            root.removeChild(connection)

        for pynq_io, comp_io in io_config.items():
            if comp_io == None or comp_io == "None":
                continue    # Skip empty connections

            connection = buildconfig.createElement("connection")

            signal = buildconfig.createElement("signal")
            signal_text = buildconfig.createTextNode(comp_io)
            signal.appendChild(signal_text)

            io = buildconfig.createElement("io")
            io_text = buildconfig.createTextNode(pynq_io)
            io.appendChild(io_text)

            connection.appendChild(signal)
            connection.appendChild(io)

            root.getElementsByTagName("ioCofnig")[0].appendChild(connection)

        with open(self.pynq_build_path + "/PYNQBuildConfig.xml", "w") as xml_file:
            buildconfig.writexml(xml_file)