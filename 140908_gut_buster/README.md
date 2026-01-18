gut-buster
==========

A simple tool for scoring documents in a corpus via word counts. 


Lately I've noticed that there's a lot of racist language in some of the
old, expired-copyright ebooks that are freely available from places
like Project Gutenberg (which is a great site). Given that I'm always looking
for books to read with my kids, I wanted a simple way I could grep through
the collection and do a first order estimate of which books had offensive
material. Normally, I'd do this kind of thing by unpacking a corpus and
grepping the hell out of it. However, Go has some nice file input features
that make it easy to analyze packed files in place, so I decided to write a
simple program to chew on the corpus.

# Building Gut-Buster

Download and install Go. Then type `go build` in the gut-buster directory.


# Getting Source Data

The first step in using gut-buster is to get some data. There's nothing fancy 
about it. You feed it a list of text or zip files and it analyzes them. If 
you're reading from zips, it expects that you're processing Gutenberg archives.
Gut-buster will look inside the file and try reading the text file that's the
most likely one to be the ebook.

**Don't crawl Gutenberg** - They have DVD iso snapshots every so often that have
everything you'd want. The one I found is from 2010, and is called 
pgdvd042010.iso. In Linux you can mount the downloaded image via:

sudo mount pgdvd042010.iso /mnt/tmp


# Defining a Dictionary

Gut-Buster asks you to provide a dictionary file so it can know what terms you're
looking for. The dictionary is a simple text file format, with one term per line.
You can provide an optional "severity" identifier (0-2) at the end of the line to
say how important the word is. Words that are more sever get more points.

I'm including a couple simple dictionaries in the project, chok-full of nastiness.
Sadly, there are worse things on the internet.


# Pointing Gut-Buster at Data

Gut-Buster expects you to give it a dictionary file and a list of files you 
want to look at. Inside this project is a handy script that walks through 
a directory tree and passes all of the files into Gut-Buster. You can
invoke it via:

./scan-path.sh

This should spew out data about each file it's analyzing. If there are matches
from your dictionary, you'll see a list of how many times each word appeared.
The summary for an individual book is in a line that begins with "Result:".
In addition to some meta data (author/title), you get a score value for the
book and a breakdown of how many terms were found.

# Parsing the Output

It's handy to strip out the stats from the data. The simplest thing to do is to
obtain the book id and its score. You can do this with the following command:

./scan-path.sh | grep  Result all.txt | awk ' {print $2 " " $3}'| grep -v '[a-z]' | sort -n >results.txt


Some books don't use numerical ids, so I tend to toss them when I'm plotting things.
Other books have high id values that probably mean something else. 

# Plotting the Scores

There's a pylab script for plotting out the results. It expects two columns of 
numerical data: id and score. It tries cramming as many books into the same 
plot as possible, just by breaking them up into a 2D grid. You can run it with

python squareplot.py results.txt

You'll probably want to change settings to make it look better. 

# Comments

That's about it. It isn't fancy, but it's good enough for me. If you have comments
or other ideas of what to do with this data, please let me know.

thanks,
-Craig






