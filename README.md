# Global wood cycle

This repository contains the BaMFA codebase, and global and regional wood cycle data in the paper 'Current global wood harvest is sufficient for climate-friendly transition to timber cities' by Yayla et al.

See interactive Sankey diagrams <a href="https://alperenyayla.github.io/globalwoodcycle/" style=" text-decoration: none !important; color:red !important;">here &#10140;</a>

# Bayesian material flow analysis

### Overview

The study uses Bayesian material flow analysis (BaMFA) methodology for reconciliation of the available data to quantify uncertainty and improve the reliability of the quantitative results.

The BaMFA model was implemented in Python (v.3.9.16), and `PyMC3` (v3.11.2) was used to conduct Bayesian inference via the No-U-Turn-Sampler algorithm. All input and output datasets are stored in the data repository hosted on<a href="https://doi.org/10.5281/zenodo.10828214" style=" text-decoration: none !important; color:red !important;"> Zenodo &#10140;</a>.

### System Requirements

This BaMFA code requires only a standard computer with enough RAM to support the in-memory operations. The code has been tested on Microsoft Windows 11 Pro, x64-based processor, and 32.0 GB of installed RAM.

### Documentation and installation guide

- See the BaMFA study by Wang et. al. <a href="https://arxiv.org/abs/2211.06178" style=" text-decoration: none !important; color:red !important;">here &#10140;</a>
- See `PyMC3` documentation <a href="https://pymc3-fork.readthedocs.io/en/latest/#" style=" text-decoration: none !important; color:red !important;">here &#10140;</a>

### Python Dependencies

```
pymc3
arviz
pandas
numpy
math
random
matplotlib
os
```

### Instructions

The [BaMFA](../BaMFA) codebase consists of four Python and one Jupyter Notebook source files. The Python source files define the necessary functions to prepare the input data for analysis (‘preprocessingagg.py’), to construct prior distributions for analysis (‘prior.py’), to conduct material flow analysis using Bayes’ theorem (‘model.py’), and lastly to construct posterior predictive distributions and plots for model and data checking (‘posteriorpredictive.py’). An additional Jupyter Notebook file (‘run-wood-model.ipynb’) is used to run the complete BaMFA model and obtain outputs combining all the other source files. An additional Python source file (‘outputforsankey.py’) is used to obtain the BaMFA model results for flows to make it easier to plot them in Sankey diagram format.

The BaMFA model produces posterior distributions of all child stock changes and flows by combining the prior distribution and data (including mass balance for all processes) via Bayes’ Theorem, which includes quantifying and propagating uncertainties. The posterior distribution provides estimates for each stock change or flow of interest via the posterior mean, as well as uncertainty quantification through 95% credible intervals. The expected run time for a wood cycle analysis of a region on a ‘normal’ desktop computer is around 1 hour and 15 minutes.

All quantitative global and regional wood cycle results in this study can be reproduced using specified input data tables and the BaMFA codebase.
