
        # AMD-Xilinx Vivado project start and tcl script: Create project, xc7z020clg400-1 technology, %lang model 

        # To execute, 

        # open cmd window 

        # cd to project folder 

        # start Vivado (with tcl file parameter) 

        # e.g, for project name RISCV_RB 

        # cmd 

        # cd {C:/2023/vicilogic/HDLGenTop/HDLGen_V160823/User_Projects/RISCV_V1/RISCV_RB} 

        # $vivado_bat_path -source C:/2023/vicilogic/HDLGenTop/HDLGen_V160823/User_Projects/RISCV_V1/RISCV_RB/Verilog/AMDPrj/RISCV_RB.tcl 


        # Vivado tcl file RISCV_RB.tcl, created in AMDprj folder 

        cd {C:/2023/vicilogic/HDLGenTop/HDLGen_V160823/User_Projects/RISCV_V1/RISCV_RB} 

        # Close_project  Not required. Will advise that Vivado sessions should be closed. 

        start_gui

        create_project  RISCV_RB  ./Verilog/AMDprj -part xc7z020clg400-1 -force

        set_property target_language Verilog [current_project]

        add_files -norecurse  ./Verilog/model/RISCV_RB.v



        update_compile_order -fileset sources_1

        set_property SOURCE_SET sources_1 [get_filesets sim_1]

        add_files -fileset sim_1 -norecurse ./Verilog/testbench/RISCV_RB_TB.v

        update_compile_order -fileset sim_1

        # Remove IOBs from snthesised schematics

        current_run [get_runs synth_1]

        set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} -value -no_iobuf -objects [get_runs synth_1]


        # Save created wcfg in project

        set_property SOURCE_SET sources_1 [get_filesets sim_1]

        add_files -fileset sim_1 -norecurse ./Verilog/AMDPrj/RISCV_RB_TB_behav.wcfg

        # save_wave_config {./Verilog/AMDprj/RISCV_RB_TB_behav.wcfg}

    