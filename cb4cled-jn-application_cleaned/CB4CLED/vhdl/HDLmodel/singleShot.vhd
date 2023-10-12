-- Model name		singleShot
-- Description		singleShot Finite State Machine (FSM) 
-- 					A  0 -> 1 transition on input sw results in combinational assertion of a pulse (aShot), 
--                  of max one clk period duration. aShot is an unregistered o/p signal.
-- Author(s)		Fearghal Morgan
-- Company			National University of Ireland, Galway 
-- Date				7th Dec 2004 
-- Change History 	Initial version
-- 
-- Signal data dictionary
--  clk			 System clock strobe, rising edge active
--  rst			 Asynchronous reset signal. Assertion clears all registers, count=0
--  sw 			 0 to 1 transition combinationally asserts signal aShot
-- 				 aShot synchronously deasserts on the subsequent active clk edge
--  aShot	     Asserted combinationally on sw 0 to 1 transition  
-- 				 Synchronously deasserts on the subsequent active clk edge

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity singleShot is
Port (clk   : 	in 	std_logic;
      rst   : 	in 	std_logic;
      sw    : 	in 	std_logic; 	
      aShot	 :  out std_logic  
	  ); 
end singleShot;

architecture RTL of singleShot is  
type stateType is (waitFor1, waitFor0); -- declare enumerated state type
signal CS, NS: stateType;     			-- declare state signals 

begin

-- Synchronous process defining state value
stateReg_i: process (clk, rst)
begin
  if rst = '1' then 		
    CS <= waitFor1;		
  elsif clk'event and clk = '1' then 
    CS <= NS;
  end if;
end process; 

-- Next state and o/p decode process
NSAndOPDec_i: process (CS, sw)
begin
   aShot <= '0';    				-- default assignment of process o/p signals 
   NS 	 <= CS; 				
   
   case CS is
		when waitFor1 => 			-- move to state waitFor0 if sw = '1'. 
									-- Otherwise no change from default values
			if sw = '1' then 
				aShot <= '1';    	-- combinationally assert unregistered o/p
				NS <= waitFor0;
			end if;
		when waitFor0 => 			-- remain in state waitFor0 unless sw = '0'. 
								    -- Otherwise no change from default values
			if sw = '0' then 
				NS <= waitFor1;
			end if;
		when others => 
			null;           		-- do nothing since default assignments apply
   end case;
end process; 
      
end RTL;