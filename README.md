## Feature specific folders


- "bifurcation" folder to compute attractors, repulsors... 

- "calibration" folder to run a dynamical model with observation constraint & forcing 

- "continuation" folder to run a continuation algorithm for a dynamical model

- "simulation" folder contains code to load observations

## Cross-feature folders

- "data" folder contains the data from various sources 

- "docs" folder contains some documentation, i.e. code examples and generated figures

- "projects" folder contains folders to generate results/plots using the 

- "results" folder will contain the generated plots 

- "tests" folder contain all tests 

- "utils" folder contains transverse classes/functions that are used in all other folders.

## Code convention

- Variables and functions names must be explicit and with type hinting. Documentation should be used only for tricky functions
- Class names should have the same name as their file. By default, child classes should have the same prefix as their parents. Object name should be the same as its class (replacing CamelCaseStyle with an underscore_style)  
- Long python files must be avoided (using code decoupling or sub-folders, and by creating utils_*.py files to store decoupled functions) 

