#!/bin/bash

#for nwritten in $(seq 10)
for nwritten in {10,20,30,40,50}
do
	for c in {0,1,100}
	do 
		nimi="data_c"$c"_"$nwritten
		python3 test_proactive_search_new.py 20news --queries ../desktop/20news-data/20news-bydate-test/20news-bydate-test-100-cleaned-unsorted.txt --querypath ../desktop/20news-data/20news-bydate-test --nostem --numwords 50 --removeseenkws --nwritten $nwritten --nclicked 10:2 --c $c --dime_search_method 3
		#python3 test_proactive_search_new.py 20news --queries ohsumed-first-20000-docs/test/ohsumed-test-all-unsorted-100.txt --querypath ohsumed-first-20000-docs/test --nostem --numwords 50 --removeseenkws --nwritten $nwritten --nclicked 10:2 --c $c --dime_search_method 3
		mv data $nimi
	done
done
