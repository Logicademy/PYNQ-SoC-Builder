-- Model name		CB4CLED_Top
-- Description		4-bit loadable, cascadable up/down counter with chip enable and asynchronous rst
-- Author(s)		Fearghal Morgan
-- Company			National University of Ireland, Galway 
-- Date				7th Dec 2012 
-- Change History 	Initial version
--
-- CB4CLED with singleShot pulse signals connected to signals ce and load
--
-- Signal dictionary
--  clk			 System clock strobe, rising edge active
--  rst			 Asynchronous reset signal. Assertion clears all registers, count=0
--  loadDat(3:0) 4-bit load data value
--  load		 Assertion (H) synchronously loads count(3:0) register with loadDat(3:0) 
--               Load function does not require assertion of signal ce
--  ce			 Assertion (H) enables synchronous count behaviour, if load is deasserted
--  up			 Assertion (H) / deassertion (L) enables count up/down behaviour
--  count(3:0)	 Counter value, changes synchronously on active (rising) clk edge
--  TC	         Terminal count, asserted (H) when in up   counter mode (up=1) and count(3:0)=0xF 
-- 					                      or  when in down counter mode (up=0) and count(3:0)=0
--  ceo	Chip enable output, asserted (H) when both ce and TC are asserted

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity CB4CLED_Top is
    Port ( clk 		: in STD_LOGIC;   
           rst 		: in STD_LOGIC;   
           loadDat	: in STD_LOGIC_VECTOR (3 downto 0); 
           load		: in STD_LOGIC;                
           ce 		: in STD_LOGIC;                
           up 		: in STD_LOGIC;                
           count	: out STD_LOGIC_VECTOR (3 downto 0);
           TC		: out STD_LOGIC;                    
           ceo		: out STD_LOGIC                     
           );
end CB4CLED_Top;

architecture struct of CB4CLED_Top is

component singleShot is
Port (clk   : 	in 	std_logic;
      rst   : 	in 	std_logic;
      sw    : 	in 	std_logic; 	
      aShot	 :  out std_logic  
	  ); 
end component;

component CB4CLED is
    Port ( clk 		: in STD_LOGIC;   
           rst 		: in STD_LOGIC;   
           loadDat	: in STD_LOGIC_VECTOR (3 downto 0); 
           load		: in STD_LOGIC;                
           ce 		: in STD_LOGIC;                
           up 		: in STD_LOGIC;                
           count	: out STD_LOGIC_VECTOR (3 downto 0);
           TC		: out STD_LOGIC;                    
           ceo		: out STD_LOGIC                     
           );
end component;

-- Internal signal declarations
signal cePulse   : STD_LOGIC;  
signal loadPulse : STD_LOGIC; 

begin

cePulse_i: singleShot 
Port map (clk   => clk,  
          rst   => rst,  
          sw    => ce,    	
          aShot => cePulse 
	  ); 

loadPulse_i: singleShot 
Port map (clk   => clk,  
          rst   => rst,  
          sw    => load,    	
          aShot => loadPulse 
	  ); 

CB4CLED_i: CB4CLED
Port map ( clk 		=> clk, 		
           rst 		=> rst, 		
           loadDat	=> loadDat,	
           load		=> loadPulse,		
           ce 		=> cePulse, 		
           up 		=> up, 		
           count	=> count,	
           TC		=> TC,		
           ceo		=> ceo	
           );

end struct;