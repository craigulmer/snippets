#!/bin/bash

SRC_DIR=/mnt/tmp
TERM_FILE=dicts/racist_words.txt
SEARCH_PATTERN="*.zip"

# Parse the command line. Borrowed from s/o 12036445
while getopts d:zth opt; do
    case $opt in
        d)
            TERM_FILE=$OPTARG
            ;;
        z) 
            SEARCH_PATTERN="*.zip"
            ;;
        t)
            SEARCH_PATTERN="*.txt"
            ;;
        *)
            cat <<EOF
scan-path : a simple script to scan a directory tree for files

 $0 [options] /path/to/scan/for/zips
    where options are:
     -d term_file  : use this dictionary to score items
     -z            : search for *.zip files (default)
     -t            : search for *.txt files
     -h            : dump this pretty help file

EOF
            exit
            ;;
        esac
done
shift $((OPTIND - 1))

# Pull out the dir name
if [ $# -gt 0 ]; then
    SRC_DIR=$1
fi


# All this boiler plate just to do a find
#  note: this find will take a while if you're running it on the iso
#NAMES=`find $SRC_DIR -name "*.zip"`
NAMES=`find $SRC_DIR -name "$SEARCH_PATTERN"`


# Now plug all the filenames into gut-buster and let it unpack everything
./gut-buster --wordlist=$TERM_FILE $NAMES


# 

# Parse all the results and dump into id/score file
# grep  Result all.txt | awk ' {print $2 " " $3}'| grep -v '[a-z]' | sort -n 
