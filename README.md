# vfatqc-python-scriptsi

1. For VFAT2s QC1 test:
   
	> python testing.py

	>> GLIB IP: e.g. 192.168.0.171

	Then hit "enter" 5 times 

2. For VFAT2s QC2/3 test: (Off detector: 35~40 mins per chip; On detector: 55~60 mins per chip!)
   
	> python pythonScript.py

	>> GLIB IP: e.g. 192.168.0.171

	>> QC Test Name:  e.g. 2016_09_09_QC3

	Then hit "enter" 5 times 

3. To save VFAT's output (QC2/3) results as root files: (all the output files should in the same dir)
   
	Each VFAT has a rootfile: e.g. 2016_11_10_OnDetNoVoltageSCurveBot_VFAT0_ID_0xf6e7_ScurveOutput.root
	
	All VFATs from one detector will have a combined rootfile: ScurveOutput.root 
	
	> #python ProduceRootFiles.py
	
	(Out of date!) To plot each VFAT's output results: (all the output files should in the same dir)
   
	> python read_and_plot.py
	
	(Out of date!) To plot all VFATs' results: (all the output files should in the same dir)
   
	> python read_and_plot_all.py

4. To MASK the channels 
   
	The only input file: ScurveOutput.root
	
	Channles masking for each VFAT: e.g. #choose one of them for masking 
	
	> Mask_TRIM_DAC_value_by_MEAN_cut0_VFAT0_ID_0xf950
	
	> Mask_TRIM_DAC_value_by_MEAN_cut1_VFAT0_ID_0xf950
	
	> Mask_TRIM_DAC_value_by_MEAN_cut2_VFAT0_ID_0xf950
	
	> Mask_TRIM_DAC_value_by_SIGMA_VFAT0_ID_0xf950
	
	> Mask_TRIM_DAC_value_by_SIGMA_and_MEAN_cut0_VFAT0_ID_0xf950
	
	> Mask_TRIM_DAC_value_by_SIGMA_and_MEAN_cut1_VFAT0_ID_0xf950
	
	> Mask_TRIM_DAC_value_by_SIGMA_and_MEAN_cut2_VFAT0_ID_0xf950
	
	> #python MaskChannels.py

5. Plotting s-curves for each VFAT in different ieat region 
   
	The only input file: ScurveOutput.root
	
	> #python Plots_Scurve_iEta.py

6. To set the TrimDAC values and scan the threshold: (70~80s 24 chips!) 
   
	First, we need to make a txt file to list all the TrimDAC files: TrimDACfiles.txt
   
	> python setTRIMDAC.py

	>> GLIB IP:  e.g. 192.168.0.171

	>> Test Name: e.g. 2016_09_09_SetTrimDAC

	Then hit "enter" 5 times 

7. To set the TrimDAC values and make the S-Curve scanning: (8~15 mins per chip!)
   
	First, we need to make a txt file to list all the TrimDAC files: TrimDACfiles.txt
   
	> python setTRIMDAC_and_Scurve.py

	>> GLIB IP:  e.g. 192.168.0.171

	>> Test Name: e.g. 2016_09_09_SetTrimDAC

	Then hit "enter" 5 times 

8. (Not a good idea!!) To set the TrimDAC values, set thresholds and make the S-Curve scanning:
   
	First, we need to make a txt file to list all the TrimDAC files: TrimDACfiles.txt

	Second, make a txt file to list all the Threshold files: Datafiles.txt
   
	> python setTRIMDAC_and_Threshold.py

	>> GLIB IP:  e.g. 192.168.0.171

	>> Test Name: e.g. 2016_09_09_SetTrimDAC

	Then hit "enter" 5 times 





