-- Description: Testbench for CB4CLED 4-bit loadable, cascadable up/down, counter with chip enable, asynchronous rst
-- Engineer: Fearghal Morgan
-- viciLogic 
-- Date: 7/12/2012
-- Change History: Initial version

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
 
ENTITY CB4CLED_TB IS  END CB4CLED_TB; -- testbench entity has no inputs or outputs, i.e, it is a closed test environment
 
ARCHITECTURE behaviour OF CB4CLED_TB IS 
 
COMPONENT CB4CLED is -- declare the component to be tested
   Port ( clk 		: in STD_LOGIC;                      
           rst 		: in STD_LOGIC;                      
           load		: in STD_LOGIC;                      
           loadDat	: in STD_LOGIC_VECTOR (3 downto 0);  
           ce 		: in STD_LOGIC;                      
           up 		: in STD_LOGIC;                      
           
           count	: out STD_LOGIC_VECTOR (3 downto 0); 
           TC		: out STD_LOGIC;                     
           ceo		: out STD_LOGIC                      
          );
END COMPONENT;    

-- Declare testbench-level signals. May be different from component signal names
SIGNAL   clk   : std_logic := '1'; -- initialise clk to '1' since std_logic default state is 'u' (undefined). 
signal rst                  : std_logic;
signal load		            : STD_LOGIC;
signal loadDat	            : STD_LOGIC_VECTOR (3 downto 0);
signal ce 		            : STD_LOGIC;
signal up 		            : STD_LOGIC;    
signal count	            : STD_LOGIC_VECTOR (3 downto 0);
signal tc		            : STD_LOGIC;
signal ceo		            : STD_LOGIC;

constant period   : time := 20 ns;	      -- 50MHz clk
signal   endOfSim : boolean := false;     -- assert at end of simulation to show end point.
signal   testNo   : integer;              -- facilitates test numbers. Aids locating each simulation waveform test 
 
BEGIN
  
--	 Instantiate the Unit Under Test (UUT)
uut: CB4CLED PORT MAP -- Instantiate the Unit Under Test (UUT)
         (clk       => clk,
          rst       => rst,
          load      => load,
          loadDat   => loadDat,
          ce        => ce,
          up        => up,
          count     => count,
          tc        => tc,
          ceo       => ceo
		 );

-- clk stimulus continuing until simulation stimulus is no longer applied
clkStim : process (clk)
begin
  if endOfSim = false then
     clk <= not clk after period/2;
  end if;
end process;
 
stim: PROCESS 
-- No sensitivity list required => auto-executes at start of testbench simulation
begin 
	report "%N : Simulation Start.";

    report "Test 0: Initialise i/ps. Toggle rst and move sim time to 0.2*period after active clk edge"; 
    testNo <= 0;
    load    <= '0'; 
    loadDat <= X"D"; 
    ce      <= '0'; 
    up      <= '0'; 
    rst     <= '1';		 -- assert/deassert rst signal sequence
	wait for period*1.2; -- 0.2*period after active clk edge
    rst     <= '0';
    wait for period;	
 	
    load    <= '1';
    wait for period;                           

    load    <= '0';
    ce      <= '1'; 
    up      <= '1'; 
    wait for 3*period;                          

    ce      <= '0'; 
    wait for period;                          

    ce      <= '1'; 
    wait for period;                          

    up      <= '0'; 
    wait for period;                          

    ce      <= '0'; 
    wait for period;                          

    loadDat <= X"2"; 
    load    <= '1';
    wait for period;                           

    load    <= '0';
    ce      <= '1'; 
    wait for 20*period;                          

	endOfSim <= true;   -- assert flag, to stop clk signal generation
    report "simulation done";   
    wait;               -- wait forever
END PROCESS;

END behaviour;