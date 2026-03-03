# Readme

This repository contains all the code developed during the thesis titled "Modeling, Simulation and Optimization of Organ Transplantation Processes". The reader will find the code for the different sections of the thesis in separate branches. For the curated repository of result files, please consult the accompanying repository, as the result files for the respective sections are only found in the relevant branch.
## Structure of this repository

The relevant modules are as follows:

- **agents**: Module where the different agents are defined (country, hospital, organs, scandiatransplant, waiting lists)
- **book_keeping**: Module where constant values are stored (organ type, locations, populations...) as well as the maps used for the animation.
- **logs**: Where the different logs ared outputted during runs.
- **matching**: The matching module, which contains all the logic regarding the matching rules, grouping and ordering of the priority groups, etc.
- **metaheuristic**: The code developed for the metaheuristic optimization section.
- **patient_generators**: Module to create synthetic donors and recipients.
- **scenarios**: Folder where the different scenarios are stored.
- **testing_files**: Folder where the relevant logs for different tests are kept, as well as the patients used.
- **utils**: Miscelaneous code of helper functions: logger, auxiliary functions ...
- **visualizer**: Where the code responsible for the animations, plots, and result stats is found.

And relevant files:

- **main.py**: run this script to execute the module
- **test.py**: script from where different functions are called for testing purposes.


## How to create patients
In order to generate synthetic patients, the donor and recipient generation modules should be called. During this thesis I have called it from test.py, with the following commands:

donor_generator.generate_donor(550, 1, 365, r"testing_files/advanced_donor.csv")

recipient_generator.generate_recipient(3394, 1, 365, r"testing_files/advanced_recipient.csv")

In both cases, the number of patients, first timestep and last timestep, as well as output path, should be specified. Additionally, for the recipient generation, a 60% of the recipients will be assigned to timestep zero, meaning they are on the waiting list at the beginning of the run. This can be modified in the generate_timesteps call.

Keep in mind that this step is not deterministic, so each run will generate a different set of patients (with the same probabilistic characteristics).

## How to run the matching

In order to run the code, the main.py script should be executed. The relevant scenario file should be included, which links the donor and recipient sets used. For each branch, running the main.py file will execute the corresponding model.
