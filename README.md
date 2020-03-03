# Android Apps Similarity

This work is to analyze what are the techniques currently used to detect code-relationships between android apps for finding potential malicious apps, and prospects to get the best of all for a possible new tool.

## Script dataset

There's a CLI to download a dataset from Androzoo. Run `cd data && ./download_pairs.py -h` for usage (not necessary, the main script will download automatically if an apk is not found)

## Main script

`cd src && ./main.py` will run the main script and give an analysis on the dataset. It compares all the pairs based on specific rules, produces a confusion matrix, f1 score and detailed report of comparisons. Folder `report` contains the reports of the runs.


## Extras

Script `./find_details.py [path_to_full_log] [id_pair]` shows the comparison details of a pair