
# Python notebooks for analysis of CFG arrays

> Find high binders and general analysis of glycans in CFG arrays

TLDR:
> I have wanted to use CFG array data in machine learning but this has been an interesting challenge.
Can all the RF data for all the glycans for a certain array version be used to classify the features of high binders and low binders for a particular disease/lectin ?
I am not sure how to solve this problem but what I have learnt is how to infer which glycans are high binding for a particular array with a fair degree of confidence. This is based on the paper by Cholleti et al. (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3459425/#SD2)


## Getting started

1. Make sure you have the correct dependencies installed (see dependencies section)
2. `source activate pynotes`
3. `jupyter-notebook`
4. browse to `localhost:8888` (or your notebook server)
5. open notebooks/overview.ipynb


## Notebooks tips
 - when the output is getting out of hand, go to cell | all output | toggle scrolling.
 - when making code changes to notebooks and commiting, please clear all outputs first.

## Dependencies
Python

- Download Anaconda python & Install
https://www.continuum.io/downloads
`bash Anaconda2-4.0.0-Linux-x86_64.sh`
- Make a new environment with rdkit notebook etc
`conda create -n pynotes jupyter PIL matplotlib pandas seaborn xlrd scikit-learn`
-  To activate this environment, use: `source activate pynotes` To deactivate this environment, use: `source deactivate`

### additional dependencies

````
source activate pynotes
conda install xlrd # only use pip if desperate
pip install beautifulsoup
pip install glypy
pip install mechanize
```
see pip_requirements.txt and conda_env.snapshot for a current view ofthe dependencies (environment needs a retest)
in conda_env.snapshot, any items designated <pip> were installed using pip inside the conda env

## Project Layout

- *data* - array data for galectin and sna
- *results* - where results of analyses will be written
- *notebooks* - notebooks for analysis
- *sample_data* - example pickled data set
- *scripts* - handy scripts that maybe should rather be managed with a submodule

## Bugs and problems
- Load on the RINGS server may cause some calls to be slow. Wait it out, run fewer analyses or ... create a local db of glycans for this array D:-)
- When running a batch MCAW analysis sometime output is not seen. Rerun the individual notebook.


## resources
http://pyinformatics.blogspot.co.za/2015/05/nested-heatmaps-in-pandas.html
http://chrisalbon.com/python/pandas_normalize_column.html

http://www.analyticsvidhya.com/blog/2016/01/12-pandas-techniques-python-data-manipulation/
http://dataconomy.com/14-best-python-pandas-features/

# Forked from
https://bitbucket.org/rxncor/ml-notebooks/
