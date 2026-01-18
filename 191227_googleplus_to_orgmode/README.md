# GooglePlus-to-OrgMode

This is a few scripts I wrote to convert my Google+ data into an Emacs
org-mode format.

Note: This was meant to be a 'first pass' script for converting data and
      downloading files. It's likely that the web downloads will break
      at some point and that you'll still need to manipulate the content or
      script to get anything useful out of it. Also- this was originally
      written as throw away code, so its uncommented and uses static
      filenames. I'm posting it in case someone else needs it.

Summary:
- parsejson.py: Initial generation of org file, downloads missing images
- squash_pic.py: Optional file to limit size of full-size images to 1920w
- find_unused.py: Cleanup unused files that were in data directory


## Background
I used Google's Google+ social media service a good bit for several years. I
know people like to rail on G+, but at the time, I found it pretty useful. I
liked how it was easy to share some text and images with a large number of
people, and that I could use my 'Circles' to limit who saw what. I used it
from around 2012 to 2017, though my posts dropped off in the last year as
I got more jaded with how Google was running it into the ground. In 2018
Google officially announced that it was sending G+ to the
[Google Grave](https://killedbygoogle.com/) to join all the other failed
services that didn't quite "change the world" the way they expected.

One positive thing that Google did when they shut down G+ was offer a way
for people to download "all" the data they posted to G+. I went and
downloaded my data in both XML and JSON formats. 

## Converting to Org Mode
The JSON takeout file I downloaded from Google has a lot of junk in it and
isn't organized in the most useful of manners. I use Emacs Org-mode to store
a lot of stuff at home, so I went about writing some scripts to help me
convert the JSON data into one large org file that has images hosted in
a data directory. In addition to the original images, I create 600px wide
scaled down versions of the images that are big thumbnails. These images have
the suffix "_sm.jpg" so its easy to get the original filename from the small
image.

## Dependencies and Setup
This script uses html2text and Pillow (ie PIL). If you're using 

```
sudo pip3 install html2text
sudo pip3 install Pillow
sudo pip3 install htmlparser
```

The script also needs a data directory for it to put images. You can create
the directory tree from bash like this:

```
for i in $(seq 2011 2018); do mkdir -p data/${i}; done
```
Finally, unpack your takeout file in this directory:

```
tar xf googleplus_parse/original/json-march-takeout-2019xyzabcZ-001.tgz 

```


## Running the Script
The script dumps the org-mode text to stdout and sends progress info to stderr.
You can separate the two like this:


```
python3 parsejson.py >gplus.org 2>errors.txt
```

## Resizing Images
After I ran the above script I realized that some of the original images were
high resolution and didn't need to be as big as they are. I wrote a resize
script to look at all the images and scale the big ones down to be 1920 pixels
wide or less:

```
python3 squash_big.py 
```


## Cleaning Up
The last step was cleaning up some of the intermediate files that were stored
in the data directory. When the parse script does its initial resizing of
images, it saves a copy of some of the images it downloads as a ".orig" file
(in case I wanted to go back and resize the image). I wrote a cleanup script
to move files that aren't referenced by the org file into a removal directory:


```
for i in $(seq 2011 2017); do mkdir -p data_removed/data/${i}; done
python3 find_unused.py
```

