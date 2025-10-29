import pandas as pd

def matching(scandiatransplant, heuristic="greedy", verbose=True, **kwargs):
    if verbose:
        print(f"Running matching with heuristic: {heuristic}")

    if heuristic == "greedy":
        _greedy_match(scandiatransplant, verbose=verbose, **kwargs)
    #elif heuristic == "priority":
        #_priority_match(scandiatransplant, verbose=verbose, **kwargs)
    else:
        raise ValueError(f"Unknown heuristic: {heuristic}")
    

def _greedy_match(scandiatransplant, verbose=True, **kwargs):
    if verbose:
        print("Using greedy matching")
    # Access scandiatransplant.recipient_waitlist, donor_list, etc.
    