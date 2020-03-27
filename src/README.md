# Android Apps Similarity

This work is to analyze what are the techniques currently used to detect code-relationships between android apps for finding potential malicious apps, and prospects to get the best of all for a possible new tool.

## Dataset

There's a CLI to download a dataset from Androzoo. Run `cd data && ./download_pairs.py -h` for usage.
It is not necessary to run this script to go further, the main scripts will download automatically if an apk is not found.

## Pairwise comparison script

`cd src && ./main.py` will run the main script and give an analysis on the dataset. It compares all the pairs based on specific rules, produces a confusion matrix, f1 score and detailed report of comparisons. Folder `report` contains the reports of the runs. In particular it contains the full log that the tool prints out, and a summary presenting only the evaluation results.

#### Usage

`pip install androguard tabulate`

    usage: main.py [-h] [--empty EMPTY] [--pair PAIR] [--processes PROCESSES]
                   [--nocache NOCACHE] [--output OUTPUT] [--dataset DATASET]

    This script runs the comparisons on a given dataset

    optional arguments:
      -h, --help            show this help message and exit
      --empty EMPTY         Rate between 0 and 100 that represents J.I. to assign
                            to equal empty strings and sets
      --pair PAIR           Run comparisons only for the provided index of the
                            pair in the dataset
      --processes PROCESSES
                            Number of processes to use for multiprocessing,
                            defaults to 8
      --nocache NOCACHE     If given to any true value, comparisons will be
                            recomputed ignoring the cache (if any)
      --output OUTPUT       Suffix of the reports, defaults to the current
                            datetime
      --dataset DATASET     Path to the dataset to analyze

### Running using gitlab

A gitlab-ci configuration file is given that is able to run the script using a gitlab-runner, cache the results, and store the reports as artifacts.

## Search Model

Other than the pairwise comparison, a search model has been studied. The script `main_search.py` is meant for that. It's able to run a single search and find a potential similar app in the dataset, or run an evaluation on the dataset to assess the tool.

#### Usage

`pip install androguard sklearn ngram tabulate`

    usage: main_search.py [-h] [-s S] [--dataset DATASET] [--ngrams NGRAMS]
                          [--processes PROCESSES] [--nocache NOCACHE]
                          [--output OUTPUT] [--threshold THRESHOLD] [-n N]

    optional arguments:
      -h, --help            show this help message and exit
      -s S                  Search single hash
      --dataset DATASET     Dataset path
      --ngrams NGRAMS       n grams to use for strings and sets
      --processes PROCESSES
                            Number of processes to use for multiprocessing,
                            defaults to 8
      --nocache NOCACHE     If to use the cache
      --output OUTPUT       Suffix for summary report
      --threshold THRESHOLD
                            Euclidean distance threshold to use for considering
                            two apps similar
      -n N                  Evaluate only the first n lines of the dataset
