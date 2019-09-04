# Spiking Grid Cell Models on Neuromorphic Hardware
Code for my MSc dissertation titled 'Spiking Grid Cell Models on Neuromorphic Hardware' submitted to The University of Manchester for the degree of Master of Science in the Faculty of Science and Engineering in 2019.

Supervised by Prof. Steve Furber and Dr. Oliver Rhodes.

BibTeX citation: 
@phdthesis{buttigieg_2019, title={Spiking Grid Cell Models on Neuromorphic Hardware}, author={Buttigieg, Nicholas}, year={2019}}

***

## Setting up 

Requires access to SpiNNaker hardware. The simulator may be replaced with another, such as [Brian2](https://brian2.readthedocs.io/en/stable/), though the code is not guaranteed to work without any issues on simulators other than SpiNNaker.

1. Requires Python v2.7 and the SpiNNaker tools (installed automatically when using *setup_virtual_env.sh*)
2. Install virtualenv package: `pip install virtualenv`
3. Create your virtual environment: `virtualenv ENV_NAME`
4. Activate virtual environment: `source ENV_NAME/bin/activate`

The SpiNNaker tools may all be updated using the *update_git_repos.sh* script.
