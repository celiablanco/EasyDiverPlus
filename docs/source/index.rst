.. Easy Diver 2.0 documentation master file, created by
   sphinx-quickstart on Wed Jul 31 23:20:47 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Easy Diver 2.0
============================

=================
Introduction
=================
Easy Diver 2.0 is an improved build of the Easy Diver tool [LINK]. This tool can be used to accomplish blah blah blah. 
Additionally, for v2.0, the authors have created an application with a GUI that can be run quite simply. 

Easy Diver 2.0 unlocks a new capability, namely the ability to run Enrichment Analysis on the outputs of Easy Diver (the `counts` and `counts_aa` folders).
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

When opening the application, the main interface will appear, featuring options for both Easy Diver 2.0 and the Graph Builder.

.. image:: _static/images/img1.png
   :alt: Easy Diver Logo
   :align: center

Selecting the “Easy Diver 2.0” option will run the Easy Diver application, which is divided in two sections, corresponding to REQUIRED and OPTIONAL parameters:

.. image:: _static/images/img2.png
   :alt: Easy Diver 2.0
   :align: center

Required Parameters:
   •	**Input Directory Path**: Field to specify the directory containing raw sequencing files. This field is mandatory. 
   
Once the required field is filled, the optional parameters will show up.

Optional Parameters:
	•	**Output Directory Path**: Field for specifying where the output files should be saved. If left blank, default is :/pipeline.output:
	•	**Forward Primer Sequence**: Input for the forward primer sequence used in extraction.
	•	**Reverse Primer Sequence**: Input for the reverse primer sequence used in extraction.
	•	**Extra Flags for PANDASeq**: Allows additional parameters for PANDASeq to be entered, enclosed in quotes.
	•	**Translate to Amino Acids**: Checkbox option to translate nucleotide sequences into amino acids.
	•	**Retain Individual Lane Outputs**: Checkbox to retain output files for each sequencing lane.

	•	**Run Enrichment Analysis**: Checkbox to enable enrichment analysis. 
   
   If selected, two options for the analysis show up:
	   •	**Output Decimal Precision**: Spin box to set the precision of decimal numbers in the enrichment output files (default is 6, max is 10).
	   •	**Sort Files into Rounds and Types**: A button to open a sorting interface where users can categorize files.

The interface has three Control Buttons:
	•	**Help**: Opens a dialog with detailed information about the application.
	•	**Cancel**: Closes the application.
	•	**Submit**: Starts the data processing and analysis pipeline with the specified parameters.

There is also an a text box at the bottom of the interface displaying the real-time output of the processing script, including progress and any errors.

Each field box displays an icon providing additional information.




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
   
