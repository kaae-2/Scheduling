#-*- coding: utf-8 -*-

import os
import sys
import json

#from constraint import *
from lib.constraint_input import ShiftInput
from lib.constraint_problem import ConstraintProblem
from lib.constraint_output import combine_solution, format_output
from lib.constraint_testing import timeout


def run_model(shift, iter_time=60, max_iter=10):
    @timeout(iter_time)
    def solver(problem):
        try:
            return problem.getSolution()
        except Exception as e:
            raise e

    print("BEGIN CSP TESTING...")
    Shift = ShiftInput(test_shift)
    print("INPUT CREATED")
    problem_class = ConstraintProblem(Shift)
    print("PROBLEM DEFINED")
    
    i = 0
    print("LOOKING FOR SOLUTION %d ITERATIONS" % max_iter)
    while True:
        try:
            constraint_solution = solver(problem_class)
            break
        except Exception as e:
            print("FAILED TO FIND SOLUTION AT ITERATION %d " % i)
            print(e)
            i+=1
        if i >= max_iter:
            print("FAILED TO FIND ANY SOLUTION AFTER %d ITERATIONS, QUITTING" % max_iter)
            constraint_solution = None
            break
    if constraint_solution is not None:
        print("SOLUTION FOUND")
        output_df = combine_solution(constraint_solution, Shift.input_df)
        output_json = format_output(output_df, Shift)
        return output_json
    else:
        print("NO SOLUTION FOUND, EXITING...")
        return
    


if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    
    test_shift = {
    "increment": "00:30",
    "tours": ["14:30", "15:30", "16:30"],
    "break_time": { 
        "start": "16:00", "end": "16:25"
        },
    "bookings": {   
        1: ["14:00"],
        #2: ["14:00"],
        #3: ["12:00", "18:30"]
        },
    "shifts": { 
        "TK": { "start":"12:15", "end":"20:00"},
        "PP": { "start":"12:15", "end":"20:00"},
        "PA": { "start":"12:15", "end":"20:00"},
        "SS": { "start":"12:15", "end":"20:00"},
        #"AU": { "start":"12:15", "end":"21:00"},
        #"DS": { "start":"12:15", "end":"19:00"},
        }
    }

    if len(sys.argv) > 1:
        test_shift = json.loads(sys.argv[1])
        #print(test_shift)    
    output = run_model(test_shift)

    if len(sys.argv) > 1:
        """ if output == None:
            pass
        else: """
        print(json.dumps(output))
    else:
        if output == None:
            print("Couldn't find solutions.")
        else:
            for key in output:
                print(key, output[key])
        #print(json.dumps(output, ensure_ascii=False))

    #print(str(output))