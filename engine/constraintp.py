
from ortools.sat.python import cp_model
import engine


def main():
    
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_nurses = 5
    num_shifts = 3
    num_days = 7
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    shift_requests = [[[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1],
                       [0, 1, 0], [0, 0, 1]],
                      [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0],
                       [0, 0, 0], [0, 0, 1]],
                      [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0],
                       [0, 1, 0], [0, 0, 0]],
                      [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0],
                       [1, 0, 0], [0, 0, 0]],
                      [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0],
                       [0, 1, 0], [0, 0, 0]]]
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))
                print(shifts[(n, d, s)])

    # Each shift is assigned to exactly one nurse in .
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 1)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # min_shifts_assigned is the largest integer such that every nurse can be
    # assigned at least that number of shifts.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = sum(
            shifts[(n, d, s)] for d in all_days for s in all_shifts)
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    model.Maximize(
        sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_nurses
            for d in all_days for s in all_shifts))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print('Day', d)
        for n in all_nurses:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                    if shift_requests[n][d][s] == 1:
                        print('Nurse', n, 'works shift', s, '(requested).')
                    else:
                        print('Nurse', n, 'works shift', s, '(not requested).')
        print()

    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_nurses * min_shifts_per_nurse, ')')
    print('  - wall time       : %f s' % solver.WallTime())


if __name__ == '__main__':
    #main()
    shift = {
        "increment": "00:15",
        "tours": ["14:30", "15:30", "16:30"],
        "break_time": { "start": "16:00",
                        "end": "16:25"},
        "bookings": {   #1: ["14:00"],
                        #2: ["14:00"],
                        #3: ["12:00", "18:30"]
                    },
        "shifts": { "TK": { "start":"12:15",
                            "end":"20:00"},
                    "PP": { "start":"12:15",
                            "end":"20:00"},
                    "PA": { "start":"12:15",
                            "end":"20:00"},
                    "SS": { "start":"12:15",
                            "end":"20:00"},
                    #"AU": { "start":"12:15",
                    #        "end":"21:00"},
                    #"DS": { "start":"12:15",
                    #        "end":"19:00"},
                }
        }

    actor_df = engine.get_actor_df(shift["shifts"])
    roles_df =  engine.get_all_roles()
    scenes_df =  engine.get_all_scenes()
    restaurant_df =  engine.get_restaurants(shift["bookings"])
    all_playable_scene_df, valid_role_list =  engine.get_valid_scenes(scenes_df, roles_df, actor_df)
    playable_scene_dict, time_slices =  engine.get_playable_scene_ids(all_playable_scene_df, shift["shifts"], valid_role_list, actor_df, restaurant_df)
    input_df =  engine.transform_scene_dict_to_df(playable_scene_dict)
    time_increments = engine.get_time_increments(time_slices, increment=shift['increment'])
    problem_class = engine.ConstraintProblem(input_df, time_increments, shift["bookings"])
    
    model = cp_model.CpModel()
    shifts = {}
    for _, i in problem_class.csp.iterrows():
        for k in i['DOMAINS']:
            #print(i['VARIABLE'], k)
            shifts[(i['VARIABLE'], k)] = model.NewBoolVar('shift_%s_d%i' % (i['VARIABLE'], k))
    
    for _, i in problem_class.csp.iterrows():
        model.Add(sum(shifts[(i['VARIABLE'], k)] for k in i['DOMAINS']) == 1)
    

    
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for _, i in problem_class.csp.iterrows():
        for k in i['DOMAINS']:
            if solver.Value(shifts[(i['VARIABLE'], k)]) == 1:
                print(shifts[(i['VARIABLE'], k)])
    print(solver.WallTime())
    #print(problem_class.csp.head())