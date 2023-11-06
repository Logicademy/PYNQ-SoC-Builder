module RISCV_RB(
		clk,
		rst,
		RWr,
		rd,
		rs1,
		rs2,
		rs1D,
		rs2D,
		WBDat,
		ce
	);

	// Port definitions
	input  clk;
	input  rst;
	input  RWr;
	input [4:0] rd;
	input [4:0] rs1;
	input [4:0] rs2;
	output [31:0] rs1D;
	output [31:0] rs2D;
	input [31:0] WBDat;
	input  ce;

    //reg [31:0] rs1D;
    //reg [31:0] rs2D;
    wire [31:0] rs1D;
    wire [31:0] rs2D;

    // Internal signal declarations
    reg [31:0] NSArray [31:0] ;
    reg [31:0] CSArray [31:0] ;

integer i;

    always @(RWr or rd or WBDat 
    or CSArray[31] or CSArray[30] or CSArray[29] or CSArray[28] or CSArray[27] or CSArray[26] or CSArray[25] or CSArray[24]
    or CSArray[23] or CSArray[22] or CSArray[21] or CSArray[20] or CSArray[19] or CSArray[18] or CSArray[17] or CSArray[16]
    or CSArray[15] or CSArray[14] or CSArray[13] or CSArray[12] or CSArray[11] or CSArray[10] or CSArray[ 9] or CSArray[ 8]
    or CSArray[7]  or CSArray[ 6] or CSArray[ 5] or CSArray[ 4] or CSArray[ 3] or CSArray[ 2] or CSArray[ 1] or CSArray[ 0]
    )
    begin : NSDecode_p
    		for (i=0; i<32; i=i+1)
    		begin
    			NSArray[i] <= CSArray[i];
    		end
///    	NSArray <= CSArray; // Default assignment
    	if (RWr == 1'b1)
    	begin
    		if (rd > 1'b0)
    			NSArray[rd] <= WBDat;
    	end
    end

    assign rs1D = CSArray[rs1];
    assign rs2D = CSArray[rs2];

    always @(posedge clk or posedge rst)
    begin : stateReg_p	
    	if (rst == 1'b1)
    	begin
    		for (i=0; i<32; i=i+1)
    		begin
    			CSArray[i] <= 32'b0;
    		end
    	end
    	else
    	begin
    		if (ce)
    		begin
     		 for (i=0; i<32; i=i+1)
    		 begin
    			CSArray[i] <= NSArray[i];
    		 end
    	    end 
    	end
    end

endmodule
