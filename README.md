# DOA<sub>V</sub>

DOA<sub>V</sub> is a variability-aware expertise-related metric to better support the identification of experts in configurable systems.

## Requirements

This project was developed mainly with Python3, but it uses R to generate graphs and Javascript to get the pull requests from GitHub.

### Javascript

To get the pull requests, [Node.js](https://nodejs.org/en/download/) is necessary. With it installed, install the requirements by doing:
```
cd js/
npm install
```

### Python

It is suggested to make use of `virtualenv`. Therefore, before installing the requirements run:
```
python3 -m venv venv
source venv/bin/activate
```
Then, install the requirements:
```
pip install -r requirements.txt
```

### R

To generate the graphs, it is necessary to install [R](https://www.r-project.org) and, optionally, [RStudio](https://www.rstudio.com/products/rstudio/). Then you can install the requirements:
```
install.packages("ineq")
install.packages("dplyr")
install.packages("readr")
install.packages("ggplot2")
install.packages("reshape2")
install.packages("dgof")
```

## Usage

First, clone the repository:
```
git clone https://github.com/karol-milano/DOAV.git
cd DOAV
```

To download new repositories, edit the repos.json file and execute
```
python3 parse_repositories.py
```

The second stage is to extract the Degree-Of-Authorship and the Ownership of the repositories by executing
```
python3 file_metrics.py
```

All the graphs from this stage can be generated with R. The R scripts for each graph are inside the R folder and can be executed one-by-one or by the R script
```
Rscript 00_GenerateGraphs.R
```

The last stage is carried out in 4 steps:
1. The pull requests of each repository must be downloaded with node.js
```
node getPullRequests.mjs
```

**(Important)** GitHub limits the number of requests that can be made from the same IP. For this reason, this step must be re-executed until there is no further change.


2. With the pull requests, the unified dataset can be created:
```
python3 prepare_dataset.py
```

3. After the files train_dataset.csv and test_dataset.csv were generated, the regression can be executed and the DOA<sub>V</sub> formula can be applied:
```
python3 regression.py

python3 calculate_doav.py
```

4. In the final step, the Jaccard distance between authorship, ownership, DOA<sub>V</sub> and reviewers is calculated
```
python3 generate_jaccard.py
```
