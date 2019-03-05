1. Before running the program, run the following command. This makes 

	./reset_ns.sh hostname

2. To spawn peers on a machine, simply run the following command

	python3 JoinMarket.py hostname

	ex. 
	To spawn peers on elnux1, you do
	python3 JoinMarket.py elnux1.cs.umass.edu

	To spawn more peers on elnux3, you run the same command 
	python3 JoinMarket.py elnux1.cs.umass.edu 

Note the hostname argument above needs to be consistent when you run the script across different machines. It's just where the naming server is. The peers will always be spawned with the same hostname of the machine where the scrip it run. 


To change the number of peers spawned by one execution of the above script, go into the config file and change N_PEOPLE. It's currently set to 3.


To rerun the program, you have to run step 1 again. This is to ensure the dead peers currently registered with the naming server is cleared out. 