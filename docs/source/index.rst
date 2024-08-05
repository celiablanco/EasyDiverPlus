.. EasyDIVER 2.0 documentation master file, created by
   sphinx-quickstart on Wed Jul 31 23:20:47 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

EasyDIVER 2.0
============================

Introduction
----------------------------

EasyDIVER 2.0 is an improved build of the EasyDIVER tool [LINK]. This tool can be used to accomplish blah blah blah. 
Additionally, for v2.0, the authors have created an application with a GUI that can be run quite simply. 

EasyDIVER 2.0 unlocks a new capability, namely the ability to run Enrichment Analysis on the outputs of EasyDIVER (the `counts` and `counts_aa` folders).
Upon completion of the Enrichment Analysis, the user may also choose to create graphical outputs via a GUI that allows for 
customization of different parameters (and outputs the subsequent graph from each graph generation to a tab in the default web browser).
This graph generating GUI can also be run independently from the main entry point of the GUI-based application, as long as the user already has
run the enrichment analysis and has the subsequent `modified_counts` and `modified_counts_aa` folders in place.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   modules
   development
   contributing
   license

Installation
============================

.. toctree::
   :maxdepth: 1

Usage
============================

When opening the application, the main interface will appear, featuring options for both EasyDIVER 2.0 and the Graph Builder.

.. image:: _static/images/img1.png
   :alt: EasyDIVER Logo
   :align: center

EasyDIVER 2.0
----------------------------

Selecting the “EasyDIVER 2.0” option will run the EasyDIVER application. The only required field is the path to the input directory. Once the required field is filled, the optional parameters will show up. 

* **Input Directory Path**: Field to specify the directory containing raw sequencing files. This field is mandatory.
   
.. image:: _static/images/img2.png
   :alt: EasyDIVER 2.0
   :align: center

Optional Parameters:

* **Output Directory Path**: Field for specifying where the output files should be saved. If left blank, the default is ``pipeline.output``.
* **Forward Primer Sequence**: Input for the forward primer sequence used in extraction.
* **Reverse Primer Sequence**: Input for the reverse primer sequence used in extraction.
* **Extra Flags for PANDASeq**: Allows additional parameters for PANDASeq to be entered, enclosed in quotes.
* **Skip Processing (enrichment analysis only)**: This options allows to run the enrichment analysis wihtout running the processing step first. 
  Use this option only if you have already run the processing step. 
  This option can be specially helpful in the case of many rounds of selection (processing can be run for separate batches of rounds to keep running time manageable, and the analysis can be run using the outputs from the several processing runs). 
* **Translate to Amino Acids**: Checkbox option to translate nucleotide sequences into amino acids.
* **Retain Individual Lane Outputs**: Checkbox to retain output files for each sequencing lane.
* **Run Enrichment Analysis**: Checkbox to enable enrichment analysis for consecutive rounds of selection/amplification. 

.. image:: _static/images/img3.png
   :alt: EasyDIVER 2.0
   :align: center

If Run Enrichment Analysis is selected, two options show up:

* **Output Decimal Precision**: Spin box to set the precision of decimal numbers in the enrichment output files (default is 6, max is 10).
* **Required: Sort Files into Rounds and Types**: A button to open a sorting interface where users can categorize files.

.. image:: _static/images/img4.png
   :alt: EasyDIVER 2.0
   :align: center

In the sorting interface, the user must first specify how many rounds of selection the experiment has:

* **How many rounds?**: Spin box to set the number of rounds. Default is 1.
* **Start sorting**: A button to open the buckets to assign files from the input directory to each bucket type (Pre-, Post-, Neg-).

.. image:: _static/images/img5.png
   :alt: EasyDIVER 2.0
   :align: center

Once a number of rounds has been selected, and after clicking 'Start sorting', the files in the input directory and the buckets will show up:

.. image:: _static/images/img6.png
   :alt: EasyDIVER 2.0
   :align: center

The files can be dragged to their corresponding bucket. 

* **Save choices and continue**: A button to save a csv file with the file names and their corresponding type of selection. 

.. image:: _static/images/img7.png
   :alt: EasyDIVER 2.0
   :align: center

Once sorting has been completed, the app will return to the parameters interface. 
This interface has three Control Buttons. 
There is also a text box at the bottom of the interface displaying the real-time output of the processing script, including progress and any errors. 
Each field box displays a question mark icon providing additional information.

* **Submit**: Starts the data processing and analysis pipeline with the specified parameters.
* **Help**: Opens a dialog with detailed information about the application.
* **Cancel**: Closes the application.

Upon submitting a job, the text box in the bottom will start printing real-time information from the run. 


Graph Builder
----------------------------

The Graph Builder can only be use if the data has been processed and analyzed, as the graphs are built using the output from the analyssy part. 
If the Graph Builder option is selected, the main interface will appear: 

.. image:: _static/images/img8.png
   :alt: EasyDIVER 2.0
   :align: center

* **Input Directory Selection**: Field to specify the directory containing the modified_counts folder. 
  This filed only shows up if EasyDIVER 2.0 has not been run right before.
  If you run EasyDIVER 2.0 at a different time, this field should be filled with the Output Directory Path from EasyDIVER 2.0. 
  If you did not specified an output directory name when running EasyDIVER, this will be ``pipeline.output``

* **Select Data Type**: dropdown menu to choose between ‘DNA’ and ‘AA’. 
  This determines which modified_counts folder is used (modified_counts or modified_counts_aa).

* **Select Round**: dropdown menu with the available rounds based on the selected directory.
  Choose the desired round for which you want to generate graphs.

User can customize various cutoff thresholds for the graphs entering the desired values in these fields
* **Count_out cutoff threshold**: Minimum count reads in the post-selection. 
* **Freq_out cutoff threshold**: Minimum relative frequency in the post-selection.
* **Count_in cutoff threshold**: Minimum count reads in the pre-selection.
* **Freq_in cutoff threshold**: Minimum relative frequency in the pre-selection.
* **Count_neg cutoff threshold**: Minimum count reads in the negative selection.
* **Freq_neg cutoff threshold**: Minimum relative frequency in the negative selection.
* **Enr_out cutoff threshold**: Minimum relative enrichment in the post-selection.
* **Enr_neg cutoff threshold**: Minimum relative enrichment in the negative selection.

The button “Generate Graphs” will start the graph generation process.
The application will use the provided input parameters and the selected round to generate graphs.
If the graphs are generated successfully, a confirmation message will appear.

Click the “Exit” button to close the application.


Usage Example
============================

Here, we will run both EasyDIVER 2.0 and the graph generator for the test data provided in the GitHub repository (ADD LINK).

EasyDIVER 2.0
----------------------------

First, we downloaded the test data and place in a directory called ``raw.data``. 
The forward and reverse primers for the test dataset are TACATTACAGCA and GATGGTGATGGTG, respectively. 
The test dataset correspods to two rounds of an experimental in vitro evolution of mRNA-displayed
peptides (unpublished), so 'Translate to Amino Acids' is selected.  

.. image:: _static/images/ex1.png
   :alt: EasyDIVER 2.0
   :align: center

There are 3 samples per round, corresponding to pre-selection, post-selection and negative control selection. 
Once the number of rounds has been set to 2, the 6 files can be assigned to their corresponding buckets:

.. image:: _static/images/ex2.png
   :alt: EasyDIVER 2.0
   :align: center

After saving choices, the file ``enrichment_analysis_file_sorting_logic.csv`` will be saved in the output directory. 

.. image:: _static/images/table.png
   :alt: EasyDIVER 2.0
   :align: center

Upon submitting the job, the text box in the bottom will start printing real-time information from the run. 

.. image:: _static/images/ex3.png
   :alt: EasyDIVER 2.0
   :align: center

Once data processing and analysis is over, the output directory should have seven folders, a log.txt file and the sorting csv table. 

.. image:: _static/images/ex4.png
   :alt: EasyDIVER 2.0
   :align: center

In the ``modified_counts`` folders there will be one ``round_00X_enrichment_analysis.csv`` file for each round. These files will have all metrics for each sequence in the post-selection sample for each round. 
For details on how the metrics are calculated see [PAPER REF].
There will also be anotehr six other csv, corresponding to the frequency and the enrichment of all sequences traced across all rounds of selection:

.. image:: _static/images/ex4.png
   :alt: EasyDIVER 2.0
   :align: center


Graph Builder
----------------------------

To run the Graph Builder with the processed and analyzed testdata, the input directoy directory must correspond to the output from EasyDIVER 2.0: 

.. image:: _static/images/img8.png
   :alt: EasyDIVER 2.0
   :align: center

Since the dataset corresponds to mRNA-displayed peptides, data type is ‘AA’. 
For testing purposes, we will plot the metrics corresponding to the last round of selection (round 2).
The button “Generate Graphs” will start the graph generation process. 
Once completed, an html window will open displayignb the plots.
If not cutoffs values are specified, the Graph Builder will include all data in the files (in this case, the plots will look crammed and frankly, ugly).

.. image:: _static/images/plot1.png
   :alt: EasyDIVER 2.0
   :align: center

There are two ways in which the user can chose to focus on specific areas or data points in the graphs:

#. By selecting specific plotting regions. The graphs interface is interactive, and specific areas of the plots can be selected by dragging the mouse. 
#. By setting more astringent cutoff values. The user can fill the values in the Graph Builder interface as many times as needed, and a new html window will open every time “Generate Graphs” is selected.

For example, increasing the Count_out cutoff threshold, reduces significantly the number of datapoints being representedfor 

.. image:: _static/images/plot2.png
   :alt: EasyDIVER 2.0
   :align: center

Clicking in the legend elements will display and hide different elements in the grpahs.
Hoovering the mouse over any datapoint will display information about the corresponding sequence. 
Hoovering over th top right corner will shop icons with options to: download the plots as png, zoom, pan, box select, lasso select, zoom in, zoom out, autoscale and reset axis.

.. toctree::
   :maxdepth: 1
Modules
============================

.. toctree::
   :maxdepth: 1

Development
============================

.. toctree::
   :maxdepth: 1

Contributing
============================

.. toctree::
   :maxdepth: 1

License
============================

.. toctree::
   :maxdepth: 1

Indices and tables
============================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`