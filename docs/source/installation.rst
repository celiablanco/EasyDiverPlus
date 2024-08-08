Installation
============

To run EasyDIVER 2.0, you should utilize the appropriate `.zip` file for your machine.
These zip files can be found in the Releases section in the EasyDiver2 repo. [link here]

Contained in the zip file is a folder called `dist` (for "distribution"). Within this folder, 
depending on the machine you are using, you will see a folder called EasyDiver and an executable
with the name EasyDiver2 OR you will see just the folder EasyDiver. Within the EasyDiver folder,
you would then find the executable instead.

Once you extract the .zip archive into your computer, you will generally need to right-click on the executable, 
and click **Open** from the menu. This is due to the fact that this is an 'unsigned' executable, and you will have to explicitly 
choose to trust it (see details below).

MacOS (x86_64 and ARM)
----------------------------

To run EasyDIVER 2.0 on MacOS, download the appropriate release for your machine. If you have an 'm' series
machine, with an m1, m2, etc chip, you'll need to use the .zip with `ARM` in the name, otherwise you should use the `x86_64` .zip file.

Right-click on the downloaded .zip file and click **Open** from the menu.. This will prompt the Archive Utility to unzip the 
file into the a folder titled `dist` in the same location as the .zip file.
Within that `dist` folder (or in the EasyDiver subfolder on ARM machines), right-click on the `EasyDiver2` executable (the icon is a black square with `exec`) and click **Open** from the menu.

You will receive a prompt asking whether you are sure you want to open this application, as macOS cannot verify the developer. Click **Open** to continue.

From here, you can follow the instructions detailed in the :any:`usage` section.

Windows (x86_64 / Windows 10+)
-----------------------------------

To run EasyDIVER 2.0 on Windows, download the appropriate release for your machine (Windows x86_64).

If you have :ref:`WSL(2) <https://learn.microsoft.com/en-us/windows/wsl/install>` already set up on your computer, you can just proceed to the last two paragraphs of this section.
Otherwise, you will need to open **Powershell**. Once opened, you will need to run:
.. code-block::
    wsl --install -d Ubuntu

This will open a new window. If you haven't run this before, you'll need to now set up a User & Password for this Ubuntu Virtual Machine.
We suggest using the same username and password as you use for your Windows user. PLEASE NOTE - you will need this password for the next steps!!
You can now close the Ubuntu window that appeared.

Next, you will need to run each of these lines (also in Powershell), so that you can appropriately install :ref:`pandaseq <https://github.com/neufeld/pandaseq>` in that Ubuntu Virtual Machine:
.. code-block::
    wsl -e bash -c "sudo apt-get install -y zlib1g-dev libbz2-dev libltdl-dev libtool zlib1g-dev pkg-config autoconf make python3 python3-pip"
    wsl -e bash -c "git clone http://github.com/neufeld/pandaseq.git/"
    wsl -e bash -c "cd ./pandaseq; bash ./autogen.sh && MAKE=gmake ./configure && make && sudo make install"

To confirm everything has been installed once this has all completed its execution, you can now run the following, which should point to the location of pandaseq in that Ubuntu Virtual Machine:
.. code-block::
    wsl -e bash -c "which pandaseq"

Alternatively to running each of these lines individually, the authors have created a shell script file in the root directory of the EasyDiver2 repository, titled 
Right-click on the downloaded .zip file and click **Extract All** from the menu, and choose a destination for the extracted files, then click **Extract** to unzip the files.
Within the extracted folder, you should now see the `dist` folder. Within that folder, right-click on the `EasyDiver2` executable (the icon is a floppy disk with a yellow python in the upper left corner) and click **Run as Administrator** from the menu.
In the prompt that appears, titled **Windows protected your PC**, you must click `More info` and then click *Run Anyway*.

From here, you can follow the instructions detailed in the :any:`usage` section.
