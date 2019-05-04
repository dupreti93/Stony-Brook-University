-----------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------

Programming language and version:
	 
	Python (Version: 3.7)

-----------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------

Libraries used:

	1. sys
	2. time
	3. dnspython	
	4. pycrypto (this library is used by dnspython and should be installed for DNSSEC part)

-----------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------

How to run the programs:

	Part A:

		I have provided both mydig tool and mydig.py for part A.

		To run mydig tool, run as:

						"./mydig <domain> <resoultion type>"

		To run mydig.py, run as:

						"python mydig.py <domain> <resolution type>"
		
									<domain> : Domain to be resolved
									<resolution type> : Type of resolution required ('A', 'NS', 'MX')

------------------------------------------------------------------------------------------------------------------
	Part B:
	
		I have provided mydig_with_dnssec.py for part B.
	
		Run as:
		
						"python mydig_with_dnssec.py <domain> <resolution type>"
		
									resolution type- Choice should be 'A' for checking DNSSEC 

-------------------------------------------------------------------------------------------------------------------
	Part C:

		I have included the PDF in the folder showing the cumulative distributive function of the three experiments.

-------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------

