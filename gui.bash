#! /bin/bash
LINES=$(tput lines)
COLUMNS=$(tput cols)

# Define colors for the terminal interface
export NEWT_COLORS='
root=,blue
checkbox=,brightblue
entry=,brightblue
title=brightgreen,gray
textbox=,lightgray
window=,gray
sellistbox=,green
actsellistbox=,green
button=,green
actbutton=,green
actcheckbox=,green
border=,gray
'

# Clear the terminal
clear

# Run EasyDIVER and enrichment counts back-to-back
function diveAndSail {
  {
    # Use whiptail to create a checklist for selecting EasyDIVER options
    options=$(whiptail --title "Select Options" --checklist "Choose EasyDIVER options with the arrow and space keys. Press enter to confirm:" 20 60 10 \
        "Input Directory" "" ON \
        "Output Directory" "" OFF \
        "Forward Primer Sequence" "" OFF \
        "Reverse Primer Sequence" "" OFF \
        "Retain Individual Lane Outputs" "" OFF \
        "Number of Threads" "" OFF \
        "Translate to Amino Acids" "" OFF \
        "Extra Flags for PANDASeq" "" OFF \
        3>&1 1>&2 2>&3)
            counts_type=""
        if (whiptail --title "Find Enrichments" --yesno "Calculate enrichment statistics for amino acid counts? (Yes- AA, No- Nucleotide)" 8 78); then
      counts_type="counts.aa"
    else
      counts_type="counts"
    fi
    input_dir=""
    outdir=""
    if [ ! -z "$options" ]; then
        selected_options="Selected options:\n$options"
        whiptail --title "Options Selected" --msgbox "$selected_options" 20 60

        # Construct the EasyDIVER command based on selected options
        command="bash easydiver.sh"

        if [[ $options == *"Input Directory"* ]]; then
            input_dir=$(whiptail --inputbox "Enter input directory filepath:" 10 60 3>&1 1>&2 2>&3)
            command+=" -i \"$input_dir\""
        fi
          if [[ $options == *"Output Directory"* ]]; then
            outdir=$(whiptail --inputbox "Enter output directory filepath:" 10 60 3>&1 1>&2 2>&3)
            command+=" -o \"$output_dir\""
          else
            outdir="pipeline.output" # Default output directory
        fi

        if [[ $options == *"Forward Primer Sequence"* ]]; then
            forward_primer=$(whiptail --inputbox "Enter forward primer sequence:" 10 60 3>&1 1>&2 2>&3)
            command+=" -p \"$forward_primer\""
        fi

        if [[ $options == *"Reverse Primer Sequence"* ]]; then
            reverse_primer=$(whiptail --inputbox "Enter reverse primer sequence:" 10 60 3>&1 1>&2 2>&3)
            command+=" -q \"$reverse_primer\""
        fi

        if [[ $options == *"Retain Individual Lane Outputs"* ]]; then
            command+=" -r"
        fi

        if [[ $options == *"Number of Threads"* ]]; then
            num_threads=$(whiptail --inputbox "Enter number of threads:" 10 60 3>&1 1>&2 2>&3)
            command+=" -T \"$num_threads\""
        fi

        if [[ $options == *"Translate to Amino Acids"* ]]; then
            command+=" -a"
        fi

        if [[ $options == *"Extra Flags for PANDASeq"* ]]; then
            extra_flags=$(whiptail --inputbox "Enter extra flags for PANDASeq:" 10 60 3>&1 1>&2 2>&3)
            command+=" -e \"$extra_flags\""
        fi
        eval "$command"
        # | whiptail --gauge "Running EasyDIVER..." 6 60 0 # Run the constructed command and display a progress gauge
    else
        whiptail --title "Options Selected" --msgbox "No options selected" 10 40
    fi

    #======================================= Enrichments calculation section ==================================================
      outdir="$input_dir/$outdir"
      counts_dir="$outdir/$counts_type"
      echo "###########################################################################################################################################################"
      echo "Hello! This is a script that computes enrichment statistics for an in-vitro selection experiment."
      echo "You must include an out/post-sel file."
      echo "  -out out_file   : File name for out/post-selection file (.txt)"
      echo "These arguments are optional and can be provided in any order:"
      echo "  -in in_file       : File name for the input file (.txt)"
      echo "  -neg neg_file     : File name for negative control file (.txt). If there is no in_file, this must be the neg_file for the round after the current out."
      echo "  -res res_file     : File name for results file (.txt)"
      echo "###########################################################################################################################################################"
      echo
      # Get the maximum round
      max_round=0
      for file in "$counts_dir/"*"-out"*"_"$counts_type".txt"; do
          filename=$(basename "$file")
          round=${filename%%-out*}  # TODO: Debug with print statements
          if [ $round -gt $max_round ]; then
              max_round=$round
          fi
      done
      progress=$((5))
      echo "(Approx.) Progress: $progress%"

      in_format="*-in*_$counts_type.txt"
      neg_format="*-neg*_$counts_type.txt"
      # Check if there are any files matching the format "*-in*_counts.txt"
      if [ ! -n "$(find "$counts_dir" -name "$in_format" -print -quit)" ]; then
          # Cases 1A and 1B: Loop up to max_round - 1
          for ((i = 1; i < max_round; i++)); do
              # Run the modified_counts_bash.sh script with the appropriate arguments
              if [ ! -n "$(find "$counts_dir" -name "$neg_format" -print -quit)" ]; then
                python3 ./modified_counts.py -out "$counts_dir/$i-out"*"_$counts_type.txt" -res "modified_counts/$i-res.txt"
              else
                python3 ./modified_counts.py -out "$counts_dir/$i-out"*"_$counts_type.txt" -neg "$counts_dir/$(($i + 1))-neg"*"_$counts_type.txt" -res "$outdir/modified_counts/$i-res.txt"
              fi

              # Calculate progress
              progress=$((i * 100 / (max_round - 1)))
              echo "(Approx.) Progress: $progress%"
          done
      else
          # Case 2A and 2B: Loop up to max_round
          for ((i = 1; i <= max_round; i++)); do
              # Run the modified_counts_bash.sh script with the appropriate arguments
              if [ ! -n "$(find "$counts_dir" -name "$neg_format" -print -quit)" ]; then
                python3 ./modified_counts.py -in "$counts_dir/$i-in*_$counts_type.txt" -out "$counts_dir/$i-out"*"_$counts_type.txt" -res "modified_counts/$i-res.txt"
              else
                python3 ./modified_counts.py -in "$counts_dir/$i-in"*"_$counts_type.txt" -out "$counts_dir/$i-out"*"_$counts_type.txt" -neg "$counts_dir/$i-neg"*"_$counts_type.txt" -res "$outdir/modified_counts/$i-res.txt"
              fi

              # Calculate progress
              progress=$((i * 100 / max_round))
              echo "(Approx.) Progress: $progress%"
          done
      fi
  }
}

# Function to use EasyDIVER
function useEasyDiver {
  {
    # Use whiptail to create a checklist for selecting EasyDIVER options
    options=$(whiptail --title "Select EasyDIVER Options" --checklist "Choose EasyDIVER options by hitting the space key. Press enter to confirm:" 20 60 10 \
        "Input Directory" "" ON \
        "Output Directory" "" OFF \
        "Forward Primer Sequence" "" OFF \
        "Reverse Primer Sequence" "" OFF \
        "Retain Individual Lane Outputs" "" OFF \
        "Number of Threads" "" OFF \
        "Translate to Amino Acids" "" OFF \
        "Extra Flags for PANDASeq" "" OFF \
        3>&1 1>&2 2>&3)

    if [ ! -z "$options" ]; then
        selected_options="Selected options:\n$options"
        whiptail --title "Options Selected" --msgbox "$selected_options" 20 60

        # Construct the EasyDIVER command based on selected options
        command="bash easydiver.sh"
        if [[ $options == *"Input Directory"* ]]; then
            input_dir=$(whiptail --inputbox "Enter input directory filepath:" 10 60 3>&1 1>&2 2>&3)
            command+=" -i \"$input_dir\""
        fi
          if [[ $options == *"Output Directory"* ]]; then
            output_dir=$(whiptail --inputbox "Enter output directory filepath:" 10 60 3>&1 1>&2 2>&3)
            command+=" -o \"$output_dir\""
        fi
        if [[ $options == *"Forward Primer Sequence"* ]]; then
            forward_primer=$(whiptail --inputbox "Enter forward primer sequence:" 10 60 3>&1 1>&2 2>&3)
            command+=" -p \"$forward_primer\""
        fi

        if [[ $options == *"Reverse Primer Sequence"* ]]; then
            reverse_primer=$(whiptail --inputbox "Enter reverse primer sequence:" 10 60 3>&1 1>&2 2>&3)
            command+=" -q \"$reverse_primer\""
        fi

        if [[ $options == *"Retain Individual Lane Outputs"* ]]; then
            command+=" -r"
        fi

        if [[ $options == *"Number of Threads"* ]]; then
            num_threads=$(whiptail --inputbox "Enter number of threads:" 10 60 3>&1 1>&2 2>&3)
            command+=" -T \"$num_threads\""
        fi

        if [[ $options == *"Translate to Amino Acids"* ]]; then
            command+=" -a"
        fi

        if [[ $options == *"Extra Flags for PANDASeq"* ]]; then
            extra_flags=$(whiptail --inputbox "Enter extra flags for PANDASeq:" 10 60 3>&1 1>&2 2>&3)
            command+=" -e \"$extra_flags\""
        fi

        # Run the constructed command and display a progress gauge
        eval "$command"
        # | whiptail --gauge "Running EasyDIVER..." 6 60 0
    else
        whiptail --title "Options Selected" --msgbox "No options selected" 10 40
    fi
  }
}

# Function to find enrichments
function findEnrichments {
  {
    counts_type=""
    if (whiptail --title "Find Enrichments" --yesno "Calculate enrichment statistics for amino acid counts? (Yes- AA, No- Nucleotide)" 8 78); then
      counts_type="counts.aa"
    else
      counts_type="counts"
    fi

    # Get the EasyDIVER output directory path
    dir=$(whiptail --inputbox "Enter the filepath for the EasyDIVER output directory:" 10 60 3>&1 1>&2 2>&3)
    {
      outdir="$dir"
      counts_dir="$outdir/$counts_type"
      echo "###########################################################################################################################################################"
      echo "Hello! This is a script that computes enrichment statistics for an in-vitro selection experiment."
      echo "You must include an out/post-sel file."
      echo "  -out out_file   : File name for out/post-selection file (.txt)"
      echo "These arguments are optional and can be provided in any order:"
      echo "  -in in_file       : File name for the input file (.txt)"
      echo "  -neg neg_file     : File name for negative control file (.txt). If there is no in_file, this must be the neg_file for the round after the current out."
      echo "  -res res_file     : File name for results file (.txt)"
      echo "###########################################################################################################################################################"
      echo

      # Get the maximum round
      max_round=0
      for file in "$counts_dir/"*"-out"*"_"$counts_type".txt"; do
          filename=$(basename "$file")
          round=${filename%%-out*}  # TODO: Debug with print statements
          if [ $round -gt $max_round ]; then
              max_round=$round
          fi
      done
      progress=$((5))
      echo "(Approx.) Progress: $progress%"

      in_format="*-in*_$counts_type.txt"
      neg_format="*-neg*_$counts_type.txt"
      # Check if there are any files matching the format "*-in*_counts.txt"
      if [ ! -n "$(find "$counts_dir" -name "$in_format" -print -quit)" ]; then
          # Cases 1A and 1B: Loop up to max_round - 1
          for ((i = 1; i < max_round; i++)); do
              # Run the modified_counts_bash.sh script with the appropriate arguments
              if [ ! -n "$(find "$counts_dir" -name "$neg_format" -print -quit)" ]; then
                python3 ./modified_counts.py -out "$counts_dir/$i-out"*"_$counts_type.txt" -res "modified_counts/$i-res.txt"
              else
                python3 ./modified_counts.py -out "$counts_dir/$i-out"*"_$counts_type.txt" -neg "$counts_dir/$(($i + 1))-neg"*"_$counts_type.txt" -res "$outdir/modified_counts/$i-res.txt"
              fi

              # Calculate progress
              progress=$((i * 100 / (max_round - 1)))
              echo "(Approx.) Progress: $progress%"
          done
      else
          # Case 2A and 2B: Loop up to max_round
          for ((i = 1; i <= max_round; i++)); do
              # Run the modified_counts_bash.sh script with the appropriate arguments
              if [ ! -n "$(find "$counts_dir" -name "$neg_format" -print -quit)" ]; then
                python3 ./modified_counts.py -in "$counts_dir/$i-in*_$counts_type.txt" -out "$counts_dir/$i-out"*"_$counts_type.txt" -res "modified_counts/$i-res.txt"
              else
                python3 ./modified_counts.py -in "$counts_dir/$i-in"*"_$counts_type.txt" -out "$counts_dir/$i-out"*"_$counts_type.txt" -neg "$counts_dir/$i-neg"*"_$counts_type.txt" -res "$outdir/modified_counts/$i-res.txt"
              fi

              # Calculate progress
              progress=$((i * 100 / max_round))
              echo "(Approx.) Progress: $progress%"
          done
      fi
    }
    # | whiptail --gauge "Finding enrichments..." 6 60 0
  }
}

# Function to graph figures
function graphFigures {
  {
    choice=$(whiptail --title "Graphs" --radiolist \
    "Choose an option:" $LINES $COLUMNS $(( $LINES - 8 )) \
    "Histogram" "Visualize sequence length distribution for a given output/histos folder" ON \
    "Enrichment Scatterplot" "Plot negative control vs output enrichment of each sequence for a given round." OFF \
    "AA Count Line Graph" "Plot unique and total amino acid counts across all rounds" OFF \
    "Txt to Excel" "Convert a given enrichment result output (.txt), convert it to .xslx" OFF \
    3>&1 1>&2 2>&3)

    filepath=""
    graph=""

    if [ $? -eq 0 ]; then
        if [ "$choice" == "Histogram" ]; then
            filepath=$(whiptail --inputbox "Enter EasyDIVER output directory filepath:" 10 60 3>&1 1>&2 2>&3)
            graph="2"
            python3 ./graphs.py "$filepath" "$graph" | whiptail --gauge "Graphing..." 6 60 0
            whiptail --title "Finished" --msgbox "Look in the figures folder to find your output(s)!" 10 40
        elif [ "$choice" == "Enrichment Scatterplot" ]; then
            filepath=$(whiptail --inputbox "Enter Enrichment result .txt filepath:" 10 60 3>&1 1>&2 2>&3)
            graph="1"
            python3 ./graphs.py "$filepath" "$graph" | whiptail --gauge "Graphing..." 6 60 0
            whiptail --title "Finished" --msgbox "Look in the figures folder to find your output(s)!" 10 40
        elif [ "$choice" == "AA Count Line Graph" ]; then
            filepath=$(whiptail --inputbox "Enter EasyDIVER output directory filepath:" 10 60 3>&1 1>&2 2>&3)
            graph="3"
            python3 ./graphs.py "$filepath" "$graph" | whiptail --gauge "Graphing..." 6 60 0
            whiptail --title "Finished" --msgbox "Look in the figures folder to find your output(s)!" 10 40
        elif [ "$choice" == "Txt to Excel" ]; then
            filepath=$(whiptail --inputbox "Enter Enrichment result .txt filepath:" 10 60 3>&1 1>&2 2>&3)
            python3 ./txt_to_xslx.py "$filepath" | whiptail --gauge "Working on it..." 6 60 0
            whiptail --title "Finished" --msgbox "Look in the figures folder to find your output(s)!" 10 40
        fi
    else
        echo "Operation canceled."
    fi
  }
}

# Array containing ASCII art for the welcome message
ascii_art=(
$'
   _____ _                 _       _____         _____ _      _____
  / ____(_)               | |     / ____|  /\   |_   _| |    |  __ \
 | (___  _ _ __ ___  _ __ | | ___| (___   /  \    | | | |    | |__) |
  \___ \| |  _ ` _ \|  _ \| |/ _ \\__ _ \ / /\ \   | | | |    |  _  /
  ____) | | | | | | | |_) | |  __/____) / ____ \ _| |_| |____| | \ \
 |_____/|_|_| |_| |_| .__/|_|\___|_____/_/    \_\_____|______|_|  \_\
                    | |
                    |_|
                  '
)
# Display a welcome message with ASCII art
whiptail --title "Welcome" --msgbox "${ascii_art[0]}
Welcome to the pipeline for Simple Sequence Analysis of In-vitro Laboratory Reads!\n\n
Press OK to continue." 30 85

# Main menu loop
while [ 1 ];
do
CHOICE=$(
whiptail --title "Main Menu" --menu "Choose an option:"  $LINES $COLUMNS $(( $LINES - 8 )) \
	"1)" "Run ALL" \
	"2)" "Use EasyDIVER"   \
	"3)" "Calculate enrichment statistics"  \
	"4)" "Figures and Misc." \
	"5)" "Help"  \
	"6)" "End script"  3>&2 2>&1 1>&3
)

result=""
case $CHOICE in
  "1)")
     diveAndSail
    ;;
	"2)")
	  useEasyDiver
	;;
	"3)")
	  findEnrichments
	;;
	"4)")
	  graphFigures
  ;;
	"5)")
		result="SimpleSAILR is a Bash program that takes input files of selex round reads in fastq(.gz) format and analyzes them, providing
sequence type and length distribution, joined reads, and/or enrichment information. There are also options to visualize sequence distribution,
enrichment, and diversity data.
v2.0 Author: Allison Tee and Celia Blanco
contact: ateecup@stanford.edu or celia.blanco@bmsis.org

	REQUIRED
	Input directory filepath

	OPTIONAL MODIFIERS
	Output directory filepath
	Forward primer sequence for extraction
	Reverse primer sequence for extraction
	Translating to amino acids
	Retaining individual lane outputs
	# of threads
	extra flags for PANDASeq (use quotes, e.g. \"-L 50\")"
	whiptail --msgbox "$result" $LINES $COLUMNS $(( $LINES - 8 ))
  ;;
	"6)")
		    exit
  ;;
esac
done
exit