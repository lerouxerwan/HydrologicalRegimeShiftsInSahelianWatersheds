## Installation

**1. Clone this git project on your computer**

**2. Install the virtual environment**

&nbsp;&nbsp;&nbsp;&nbsp; This virtual environment relies on Python3.12, install it.

&nbsp;&nbsp;&nbsp;&nbsp; Install this virtual environment from the requirements.txt files 

&nbsp;&nbsp;&nbsp;&nbsp; If you are not familiar with such installation: 

&nbsp;&nbsp;&nbsp;&nbsp; We recommend to use the pycharm IDE to easily create this virtual environment 

&nbsp;&nbsp;&nbsp;&nbsp;Click on Settings -> Project tiphyc_wp3 -> Python interpreter -> Add interpreter.

**3. Download data folder and place it at the root of the project**

&nbsp;&nbsp;&nbsp;&nbsp; [Link to data folder stored on a google drive](https://drive.google.com/drive/folders/19yuS0SOSbvuXefKs9lj2EeWJnOVyQa93?usp=sharing)

**4. Generate figures for the article**

&nbsp;&nbsp;&nbsp;&nbsp; Run the script located at projects/paper_model/main_paper_model.py 

&nbsp;&nbsp;&nbsp;&nbsp; To run it from a terminal, 1) activate the virtual environment 2) add pythonpath 3) run:

&nbsp;&nbsp;&nbsp;&nbsp; source <virtual_environment_name>/bin/activate 

&nbsp;&nbsp;&nbsp;&nbsp; export PYTHONPATH="projects/paper_model/main_paper_model.py:$PYTHONPATH"

&nbsp;&nbsp;&nbsp;&nbsp; python projects/paper_model/main_paper_model.py 

**Bonus. You can test that everything works**

&nbsp;&nbsp;&nbsp;&nbsp; Go into the terminal of pycharm, and run tests with the following command:

&nbsp;&nbsp;&nbsp;&nbsp; <virtual_environment_name>  pytest --cov=. -W ignore --durations=5 -v 


## Folders


- "bifurcation" folder to compute attractors, repulsors... 

- "calibration" folder to run a dynamical model with observation constraint & forcing 

- "continuation" folder to run a continuation algorithm for a dynamical model

- "data" folder contains the data from various sources 

- "docs" folder contains some documentation, i.e. code examples and generated figures

- "projects" folder contains folders to generate results/plots using the 

- "results" folder will contain the generated plots 

- "simulation" folder contains code to load observations

- "tests" folder contain all tests 

- "utils" folder contains transverse classes/functions that are used in all other folders.

## Code convention

- Variables and functions names must be explicit and with type hinting. Documentation should be used only for tricky functions
- Class names should have the same name as their file. By default, child classes should have the same prefix as their parents. Object name should be the same as its class (replacing CamelCaseStyle with an underscore_style)  
- Long python files must be avoided (using code decoupling or sub-folders, and by creating utils_*.py files to store decoupled functions) 

