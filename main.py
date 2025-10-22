import book_keeping
from patient_generators import *
from patient_generators import generating_utils
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

donor_generator.generate_donor(10)