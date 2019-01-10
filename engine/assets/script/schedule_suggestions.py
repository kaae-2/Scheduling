"""algorithm examples for constraint satisfaction:"""

"""
for col1 in cols:
    for col2 in cols:
        if col1 < col2:
                problem.addConstraint(lambda row1, row2, col1=col1, col2=col2: 
                                        abs(row1-row2) != abs(col1-col2) 
                                        and row1 != row2, 
                                        (col1, col2))


def constraintFunction (col1, col2):
    def innerFunction (row1, row2):
        return abs(row1 - row2) != abs(col1 - col2) and row1 != row2
    return innerFunction

"""



domain1 = 2
domain2 = 2
scene = ['POS', [2, 6, 8, 13, 16, 32, 35, 38, 42, 46, 47, 49, 51, 53, 54, 78, 79, 80, 84, 88, 90, 95, 99, 110, 111, 113, 115, 119, 136, 139, 142, 146, 149, 155, 156, 163, 164, 166, 168, 170, 171, 203, 204, 205, 206, 210, 214, 216, 221, 224, 240, 243, 246, 250, 254, 255, 257, 259, 261, 262, 286, 287, 288]]
domains = [domain1, domain2]
print(domains)
print(sum([domain1 in scene[1], domain2 in scene[1]]))
print(sum([el in scene[1] for el in domains])>=2)
print(not all([domain1 in scene[1], domain2 in scene[1]]))

""" 
Minimal conflicts algorithm
function MinConflicts(csp, max_steps)
// csp, max_steps is number of steps before giving up
    current = an initial assignment for csp
    for i=1 to max_steps do
        if current is a solution for csp
            return current
        var = a randomly chosen conflicted variable in csp
        value = the value v for var that minimizes Conflicts
        set var = value in current
    return failure
"""

"""
Backtracking algorithm:
function BacktrackingSearch(csp)
    return Backtrack({}, csp) //return solution or failure
    
function Backtrack(assignment, csp)
    if assignment is complete return assignment
    u_var = SelectUnassignedVariable(csp)
    for each value in OrderDomainValues(u_var, assignment, csp) do
        if IsConsistent(value, assignment)
            add {u_var=value) to assignment
            inferences = Inference(csp, u_var, value)
            if inferences != failure
                add inferences to assignment
                result = Backtrack(assignment, csp)
                if result != failure then
                    return result
        remove {u_var = value} and inferences from assignment
    return failure 
"""


"""
Forward checking algorithm
function ForwardChecking(csp) //returns a new domain for each var
    for each variable X in csp do
        for each unassigned variable Y connected to X do
            if d is inconsistent with Value(X)
                Domain(Y) = {Domain(x) - d}
    return csp //with the modified domains
"""

"""
import constraint
class ConstraintProblem(constraint.Problem):
    def __init__(self, my_input_df):
        super(ConstraintProblem, self).__init__()
        self.csp = my_input_df
        for _, variable in self.csp.iterrows():
            # print(variable['VARIABLE'], variable['DOMAINS'])
            self.addVariable(constraint.Variable(str(variable['VARIABLE'])), constraint.Domain(variable['DOMAINS']))
        self.addConstraint(constraint.AllDifferentConstraint())
        self.setSolver(constraint.MinConflictsSolver())

"""