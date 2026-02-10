## Installation

**1. Clone this git project on your computer**

**2. Install the virtual environment**

&nbsp;&nbsp;&nbsp;&nbsp; This virtual environment relies on Python3.11 (limitation due to Torch library), install it.

&nbsp;&nbsp;&nbsp;&nbsp; We recommend to use the integrated tool of the pycharm IDE to easily create this virtual environment from the requirements.txt files 

&nbsp;&nbsp;&nbsp;&nbsp;Click on Settings -> Project tiphyc_wp3 -> Python interpreter -> Add interpreter.

**3. Test that everything works**

&nbsp;&nbsp;&nbsp;&nbsp; Go into the terminal of pycharm, and run the full battery of test with the following command:

&nbsp;&nbsp;&nbsp;&nbsp; (<env_name>)$  pytest --cov=. -W ignore --durations=5 -v 

