#!/bin/bash

#for nwritten in $(seq 10)
#for nwritten in {10,20,30,40,50}
for c in {0,0.5,1,2,4,8,16,32}
do 
	nimi="data_c"$c
	python3 test_proactive_search_new.py 20news --queries ../desktop/20news-data/20news-bydate-test/20news-bydate-test-100-cleaned-unsorted.txt --querypath ../desktop/20news-data/20news-bydate-test --nostem --numwords 50 --removeseenkws --nwritten 50 --nclicked 0:2 --c $c --dime_search_method 2
	mv data $nimi
done

