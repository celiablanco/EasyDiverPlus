Installation
============

To run EasyDIVER 2.0, you should utilize the appropriate `.zip` file for your machine.
These zip files can be found in the `Releases section in the EasyDiver2 repository <https://github.com/celiablanco/EasyDiver2/releases>`_.

Contained in the zip file is a folder called `dist` (for "distribution"). Within this folder, 
depending on the machine you are using, you will see a folder called EasyDiver and an executable
with the name EasyDiver2 OR you will see just the folder EasyDiver. Within the EasyDiver folder,
you would then find the executable instead.

Once you extract the .zip archive into your computer, you will generally need to right-click on the executable, 
and click **Open** from the menu. This is due to the fact that this is an 'unsigned' executable, and you will have to explicitly 
choose to trust it (see details below).

MacOS (x86_64 and ARM)
----------------------------

To run EasyDIVER 2.0 on MacOS, download the appropriate release for your machine from the `Releases section in the EasyDiver2 repository <https://github.com/celiablanco/EasyDiver2/releases>`_.. If you have an 'm' series
machine, with an m1, m2, etc chip, you'll need to use the .zip with `ARM` in the name, otherwise you should use the `x86_64` .zip file.

Right-click on the downloaded .zip file and click **Open** from the menu.. This will prompt the Archive Utility to unzip the 
file into the a folder titled `dist` in the same location as the .zip file.
Within that `dist` folder (or in the EasyDiver subfolder on ARM machines), right-click on the `EasyDiver2` executable (the icon is a black square with `exec`) and click **Open** from the menu.

You will receive a prompt asking whether you are sure you want to open this application, as macOS cannot verify the developer. Click **Open** to continue.

From here, you can follow the instructions detailed in the `usage` section.

Pandaseq note
~~~~~~~~~~~~~
If you encounter any issues with pandaseq not running correctly after clicking **Submit** and starting the processing, we recommend
that you download and install `pandaseq <https://github.com/neufeld/pandaseq>`_ locally. The application will always attempt to leverage the local installation first, and this should relieve any potential issues.

If a problem is encountered with newer MacOS versions after installing PANDASeq, you may try the following:

1. Install `Homebrew <https://brew.sh/>`
2. brew install bzip2 pkgconfig libtools
3. Run the ./autogen.sh build step (see PANDASeq manual)

If an error referencing snprintf occurs, identify the file from the error message, open that file and adjust 'snprintf' to be 'printf' instead. During our test runs, this issue was found in line 528 in the pandaseq package args.c file. 
Run the ./autogen.sh build step again. At this point, you might get many ‘warnings’ but you shouldn't get any errors. 

Windows (x86_64 / Windows 10+)
-----------------------------------

To run EasyDIVER 2.0 on Windows, there is a bit of extra work to prepare the Ubuntu environment which will be used to execute the underlying code.

WSL / Ubuntu Virtual Machine Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you have `WSL(2) <https://learn.microsoft.com/en-us/windows/wsl/install>`_ already set up on your computer, you can just proceed to the :ref:`Install pandaseq section<pandaseq_section>`.

Otherwise, you will need to open **Powershell**. Once opened, you will need to run:

.. code-block::
    :dedent:

    wsl --install -d Ubuntu

This will open a new window. If you haven't run this before, you'll need to now set up a User & Password for this Ubuntu Virtual Machine.
We suggest using the same username and password as you use for your Windows user. PLEASE NOTE - you will need this password for the next steps!!
You can now close the Ubuntu window that appeared.

.. _pandaseq_section:

Install pandaseq
~~~~~~~~~~~~~~~~~~
Next, you will need to run each of these lines (also in Powershell), so that you can appropriately install `pandaseq <https://github.com/neufeld/pandaseq>`_ in that Ubuntu Virtual Machine:

.. code-block::
    :dedent:

    wsl -e bash -c "sudo apt-get install -y zlib1g-dev libbz2-dev libltdl-dev libtool zlib1g-dev pkg-config autoconf make python3 python3-pip"
    wsl -e bash -c "git clone http://github.com/neufeld/pandaseq.git/"
    wsl -e bash -c "cd ./pandaseq; bash ./autogen.sh && MAKE=gmake ./configure && make && sudo make install"

To confirm everything has been installed once this has all completed its execution, you can now run the following, which should point to the location of pandaseq in that Ubuntu Virtual Machine:

.. code-block::
    :dedent:

    wsl -e bash -c "which pandaseq"

Alternatively to running each of these lines individually, the authors have created a shell script file in the root directory of the EasyDiver2 repository, titled `install_pandaseq_ubuntu.sh`.
This can be run in one command like the following, which will then execute the shell script (that contains the above code).

.. code-block::
    :dedent:

    wsl -e bash -c "$(curl https://raw.githubusercontent.com/celiablanco/EasyDiver2/main/install_pandaseq_ubuntu.sh )"

Once the above steps are completed, you now have a WSL Ubuntu environment prepared, and EasyDiver2's interface will handle the rest for you. 
You can now proceed to download the .zip archive, extract and run the EasyDiver2.exe file!

.. _run-section:

Download and Run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the zip package for Windows from the `Releases section in the EasyDiver2 repository <https://github.com/celiablanco/EasyDiver2/releases>`_.

Right-click on the downloaded .zip file and click **Extract All** from the menu, and choose a destination for the extracted files, then click **Extract** to unzip the files.

Within the extracted folder, you should now see the `dist` folder. Within that folder, right-click on the `EasyDiver2` executable (the icon is a floppy disk with a yellow python in the upper left corner) and click **Run as Administrator** from the menu.

In the prompt that appears, titled **Windows protected your PC**, you must click `More info` and then click *Run Anyway*.

From here, you can follow the instructions detailed in the :any:`usage` section.
