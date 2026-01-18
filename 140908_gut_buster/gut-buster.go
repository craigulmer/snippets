package main

import (
	"archive/zip"
	"bufio"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

// Read in a dictionary text file and stick its contents into a map. If user
// gave an integer value at the end (0-2), stick that in the map so we can
// score the vals later.
func readWordList(filename string) map[string]int {
	wl := make(map[string]int)

	//Load in the wordlist
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.Fields(scanner.Text())
		var severity int
		if len(line) > 1 {
			severity, _ = strconv.Atoi(line[1])
		}
		wl[line[0]] = severity
	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
	return wl
}

// Look inside a Gutenberg zip file and guess at what file we should
// pull out.
func findGutFile(zip_filename string, rdr *zip.ReadCloser) (io.ReadCloser, error) {

	base_name := filepath.Base(zip_filename)
	base_name = strings.Replace(base_name, "_", "-", -1) // 10801_8.zip contains 10801-8.txt
	search_name := strings.TrimSuffix(base_name, ".zip") + ".txt"

	for _, f := range rdr.File {
		inzip_base_name := filepath.Base(f.Name)
		if inzip_base_name == search_name {
			rc, err := f.Open()
			return rc, err
		}
	}
	return nil, errors.New("Could not find " + search_name + " in " + base_name + " full: " + zip_filename)
}

// Give a filename and this
func processFile(filename string, searchwords map[string]int) {

	var scanner *bufio.Scanner
	var id string

	//Gut has many revisions of the same thing (eg 10801_7.zip)
	if strings.Contains(filename, "_") {
		return
	}

	//Neat. Go lets you choose whether you read from a zip or a text file
	if filepath.Ext(filename) == ".zip" {
		//We're pulling from the original gut file
		id = strings.TrimSuffix(filepath.Base(filename), ".zip")
		r, err := zip.OpenReader(filename)
		if err != nil {
			log.Print(err)
			return
		}
		defer r.Close()

		rdr, err := findGutFile(filename, r)
		if err != nil {
			log.Print(err)
			return
		}
		scanner = bufio.NewScanner(rdr)

	} else {

		//Not a zip, assume a regualr text file
		id = strings.TrimSuffix(filepath.Base(filename), ".txt")
		file_in, err := os.Open(filename)
		if err != nil {
			log.Print(err)
			return
		}
		defer file_in.Close()
		scanner = bufio.NewScanner(file_in)
	}

	//Make a regex in advance that just pulls out words
	regex_nonwords, err := regexp.Compile("[^A-Za-z0-9]+")
	if err != nil {
		log.Fatal(err)
	}

	var line_num int

	//Step 1: Read the Gut meta data at the beginning of the file. This
	//        section ends when you see "*** start"
	title := "UNKNOWN"
	author := "UNKNOWN"

	for scanner.Scan() {
		if line_num > 50 {
			break
		}
		line := scanner.Text()
		line = strings.ToLower(line)

		if strings.HasPrefix(line, "title:") {
			title = strings.TrimPrefix(line, "title: ")
			title = strings.Replace(title, " ", "_", -1)

		} else if strings.HasPrefix(line, "author:") {
			author = strings.TrimPrefix(line, "author: ")
			author = strings.Replace(author, " ", "_", -1)

		} else if strings.HasPrefix(line, "*** start") {
			break
		}
		line_num++
	}

	docwords := make(map[string]int)

	//Step 2: run through the guts of the file. Do some simple conversions
	//        and then stick each word in the map
	for scanner.Scan() {

		line := scanner.Text()
		line = strings.ToLower(line)
		line = strings.Replace(line, "'s ", " ", -1)
		line = regex_nonwords.ReplaceAllString(line, " ")

		tokens := strings.Fields(line)
		for _, w := range tokens {
			docwords[w]++
		}
		line_num++
	}

	//Done parsing. Now compute some scores based on counts. Insert
	//code here if you want to do more than flimsy scoring
	var found bool
	var total_counts [3]int  //How many words total in each category
	var unique_counts [3]int //How many types of words did we see
	for k, v := range searchwords {
		if docwords[k] > 0 {
			found = true
			total_counts[v] += docwords[k]
			unique_counts[v]++
			//Comment this out if you don't want to see all the stats
			fmt.Println(filename, " contained ", docwords[k], " occurances of ", k, "severity", v)
		}
	}

	//Only dump books that had words we looked for
	if found {
		score := total_counts[0] + total_counts[1] + 100*total_counts[2]
		fmt.Println("Result:", id, score, author, title, filename, "TotalBadWords:", total_counts,
			"UniqueBadWords:", unique_counts, " docWords: ", len(docwords))
	}

	return
}

func main() {

	var wordlist_filename = flag.String("wordlist", "bad_words.txt", "Wordlist to look for")

	flag.Parse()

	args := flag.Args()
	if len(args) < 1 {
		log.Fatal("Provide one or more files to look at\n")
	}

	//Pull in the list of words to check
	wordlist := readWordList(*wordlist_filename)

	for _, filename := range args {
		processFile(filename, wordlist)
	}

}
