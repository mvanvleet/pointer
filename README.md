pointer
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/REPLACE_WITH_OWNER_ACCOUNT/pointer/workflows/CI/badge.svg)](https://github.com/REPLACE_WITH_OWNER_ACCOUNT/pointer/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/pointer/branch/main/graph/badge.svg)](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/pointer/branch/main)


Parameter Optimization for INTERmolecular force fields fit to quantum-mechanical data.


# POInter: Parameter Optimization for Intermolecular Force Fields


<img src="http://www.clipartpal.com/_thumbs/pd/animal/dog/pointer_3.png" width="300" >

Introduction
------------
POInter is an open-source python package for intermolecular force field parameter optimization. 
It has primarily been designed to optimize parameters for the MASTIFF force field, which 
uses a Slater-type functional form to describe short-range effects. In addition, 
POInter can be used to optimize intermolecular potentialss whose short-range effects are 
described by one of the following functional forms:

* Lennard-Jones 12-6 Potentials
* Born-Mayer Potentials
* Stone/Misquitta form: exp(-ar - p))

POInter can be called directly from the command line, or can be executed from within a Python script.


Getting Started
---------------
POInter is a relatively new (and constantly updating) code. 
Email mary.vanvleet at spelman dot edu
if you're willing to become a beta tester for the code.

Documentation can be found in this repository's wiki.

Issues with the code (bugs, unclear documentation, suggestions for improvement)
should be reported with the issue tracker.


Dependencies
------------
To run properly, POInter requires the following python packages:

* Numpy
* Scipy
* Sympy
* [numexpr](https://github.com/pydata/numexpr)
* [dill](https://github.com/uqfoundation/dill) (optional, but speeds up multipole calculations)

Downloads
---------
POInter is free software and is protected under a Creative Commons license. As we're still in beta development,
we kindly appreciate new users filling out the following two-minute survey about how they intend to use the code:

https://goo.gl/forms/sYnJ4iRKQfb1Jnm93


### Copyright

Copyright (c) 2025, Mary Van Vleet


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.11.
