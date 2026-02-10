## Feature specific folders

- "attribution" folder to run an attribution study with a dynamical model

- "bifurcation" folder to compute attractors, repulsors... 

- "calibration" folder to run a dynamical model with observation constraint & forcing function

- "emulation" folder to train/predict a physical emulator

- "extraction" folder to extract from raw data

- "mediation" folder to extract variables from the Mediation reference chain & run discovery

- "simulation" folder contains code to load climate simulations data and debiase them


## Cross-feature folders

- "data" folder contains the data from various sources 

- "docs" folder contains the documentation, i.e. markdown files with code examples and generated figures

- "projects" folder contains folders to generate results/plots using the 

- "results" folder will contain plots 

- "tests" folder contain all tests (each sub-folder correspond to a main folder of this code)

- "utils" folder contains transverse classes/functions that are used in all other folders.


## Git

- "main" is the production branch, this is the default branch presented online

- "dev" is the branch were all new features/fixes/refactoring are brought

- Other branches start with the owner's name and/or a short description of the topic/feature

- Commit should follow the convention "\<type>[optional scope]: \<description>" with type among (fix, feat, build:, docs:, style:, refactor:, perf:, test:), see for more details see: https://www.conventionalcommits.org/en/v1.0.0/

## Code convention

- Variables and functions names must be explicit and with type hinting. Documentation should be used only for tricky functions
- Class names should have the same name as their file. By default, child classes should have the same prefix as their parents. Object name should be the same as its class (replacing CamelCaseStyle with an underscore_style)  
- Long python files must be avoided (using code decoupling or sub-folders, and by creating utils_*.py files to store decoupled functions) 
- Config files are avoided. Instead, we often rely on python classes without attributes. We rely on inheritance to override some specific methods/properties. Looping on such class enables to test easily many config.

