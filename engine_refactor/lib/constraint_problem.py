import pandas as pd
import datetime as dt
from constraint import *


class ConstraintProblem(Problem):
    def __init__(self, ShiftClass):
        super(ConstraintProblem, self).__init__()
        self.setSolver(MinConflictsSolver())
        self.shift = ShiftClass.shift
        self.mapping_df = ShiftClass.input_df
        self.booking_input = self.get_booking_input(ShiftClass.shift["bookings"])
        self.csp = self.create_constraint_satisfaction_input(ShiftClass.input_df, ShiftClass.time_increments)
        self.initialize_variables()
        self.set_constraints() 

    def get_booking_input(self, bookings, seating_minutes=120):
        #output format: Dictionary = {
        # domains: list of domain indices, 
        # booking: list of lists of booking beginning and ending times
        # }
        seating_time = dt.timedelta(minutes=seating_minutes)
        booking_input = {}
        for restaurant in bookings:
            booking_input[restaurant] = {"domains": [], "booking": []}
            booking_input[restaurant]["domains"] = self.mapping_df[self.mapping_df["restaurant_id"] == restaurant].index.tolist()
            for booking in bookings[restaurant]:
                begin = dt.datetime.strptime(booking, '%H:%M')
                end = begin + seating_time
                booking_input[restaurant]["booking"].append([begin.strftime('%H:%M'), end.strftime('%H:%M')])
        return booking_input

    def create_constraint_satisfaction_input(self, df, time_increments):
        all_domains = []
        time_slices = sorted(set(df['time']))
        for time in time_increments:
            a = max(x for x in time_slices if x <= time)
            valid_domains = df[df['time']==a].index.tolist()
            pruned_domains = self.remove_domains_outside_booking_small_restaurants(time, valid_domains)
            all_domains.append([time, pruned_domains])
        output_df = pd.DataFrame(all_domains, columns=['VARIABLE', 'DOMAINS'])
        return output_df

    def remove_domains_outside_booking_small_restaurants(self, time, valid_domains, small_restaurants=[1, 2, 3]):
        small_restaurants_with_booking = [x for x in small_restaurants if x in self.booking_input]
        pruned_domains = valid_domains
        for restaurant in small_restaurants_with_booking:
            if all([time <= booking[0] or time > booking[1] for booking in self.booking_input[restaurant]["booking"]]):
                pruned_domains = [x for x in pruned_domains if x not in self.booking_input[restaurant]["domains"]] 
        return pruned_domains
              
    def initialize_variables(self):
        for _, i in self.csp.iterrows():
            self.addVariable(i['VARIABLE'], i['DOMAINS'])

    def set_constraints(self):
        ### Adding all the constraints. 
        #self.addConstraint(AllDifferentConstraint())
        self.set_relational_constraints()
        if len(self.booking_input) > 0:
            self.set_booking_constraints()     

    def set_relational_constraints(self):
        # set constraints that are relevant between 2 time points. 
        variables = self.csp['VARIABLE'].values
        for variable1 in variables:
            self.set_role_rotation_constraints(variable1)
            self.set_scene_rotation_constraints(variable1)
            self.set_actor_changing_time_constraint(variable1)
        print("RELATIONAL CONSTRAINTS ADDED")

    def set_booking_constraints(self, min_visits=2):
        for restaurant in self.booking_input:
            for booking in self.booking_input[restaurant]["booking"]:
                variables = self.csp[(self.csp["VARIABLE"] > booking[0]) & (self.csp["VARIABLE"] <= booking[1])]["VARIABLE"].values.tolist()
                if len(self.booking_input[restaurant]["domains"]) == 0:
                    raise Exception("Domain error: Actors on call cannot fulfill one or more restaurant: %s , bookings: %s" % (restaurant, self.booking_input[restaurant]))
                self.addConstraint(lambda *dom, r=restaurant, m=min_visits: sum([1 if x in self.booking_input[r]["domains"] else 0 for x in dom]) >= m and len(set(dom)) == len(dom), variables)
        print("BOOKING CONSTRAINTS ADDED")
    
    def set_actor_changing_time_constraint(self, variable1, minutes=30):
        variable2 = dt.datetime.strptime(variable1, '%H:%M') + dt.timedelta(minutes=minutes)
        diff = dt.datetime.strptime(self.csp["VARIABLE"].max(), '%H:%M') - variable2
        incr = dt.timedelta(minutes=0)
        if diff < incr:
            return
        variable2 = dt.datetime.strftime(variable2, '%H:%M')
        variables = self.csp[(self.csp["VARIABLE"] >= variable1) & (self.csp["VARIABLE"] <= variable2)]["VARIABLE"].values.tolist()
        if len(variables) == 0:
            return
        all_domains = list(set([x for sublist in self.csp[self.csp["VARIABLE"].isin(variables)]['DOMAINS'] .values.tolist() for x in sublist]))
        actor_dict = {}
        for domain in all_domains:
            role_actor = self.mapping_df.iloc[domain]['role_actor']
            for role in role_actor:
                if not role_actor[role] in actor_dict:
                    actor_dict[role_actor[role]] = {}
                if not role in actor_dict[role_actor[role]]:
                    actor_dict[role_actor[role]][role] = []
                actor_dict[role_actor[role]][role].append(domain)
        for actor in actor_dict:
            for current_role in actor_dict[actor]:
                current_domains = actor_dict[actor][current_role]
                other_roles = [role for role in actor_dict[actor] if role is not current_role]
                other_domains = [domains for role in other_roles for domains in actor_dict[actor][role]]
                self.addConstraint(lambda *dom, cur=current_domains, othr=other_domains:
                                    not all([set(dom).intersection(cur), set(dom).intersection(othr)]), variables)
      
    def set_role_rotation_constraints(self, variable1, minutes=120):       
        variable2 = dt.datetime.strptime(variable1, '%H:%M') + dt.timedelta(minutes=minutes)
        diff = dt.datetime.strptime(self.csp["VARIABLE"].max(), '%H:%M') - variable2
        incr = dt.timedelta(minutes=0)
        if diff < incr:
            return
        variable2 = dt.datetime.strftime(variable2, '%H:%M')
        variables = self.csp[(self.csp["VARIABLE"] > variable1) & (self.csp["VARIABLE"] <= variable2)]["VARIABLE"].values.tolist()
        if len(variables) == 0:
            return
        all_domains = list(set([x for sublist in self.csp[self.csp["VARIABLE"].isin(variables)]['DOMAINS'] .values.tolist() for x in sublist]))
        role_dict = {}
        for domain in all_domains:
            role_actor = self.mapping_df.iloc[domain]['role_actor']
            for role in role_actor:
                if not role in role_dict:
                    role_dict[role] = {}
                if not role_actor[role] in role_dict[role]:
                    role_dict[role][role_actor[role]] = []
                role_dict[role][role_actor[role]].append(domain)
        for role in role_dict:
            for current_actor in role_dict[role]:
                current_domains = role_dict[role][current_actor]
                other_actors = [actor for actor in role_dict[role] if actor is not current_actor]
                other_domains = [domains for actor in other_actors for domains in role_dict[role][actor]]
                self.addConstraint(lambda *dom, cur=current_domains, othr=other_domains:
                                    not all([set(dom).intersection(cur), set(dom).intersection(othr)]), variables) 
    
    def set_scene_rotation_constraints(self, variable1, minutes=120):
        variable2 = dt.datetime.strptime(variable1, '%H:%M') + dt.timedelta(minutes=minutes)
        diff = dt.datetime.strptime(self.csp["VARIABLE"].max(), '%H:%M') - variable2
        incr = dt.timedelta(minutes=0)
        if diff < incr:
            return
        variable2 = dt.datetime.strftime(variable2, '%H:%M')
        variables = self.csp[(self.csp["VARIABLE"] > variable1) & (self.csp["VARIABLE"] <= variable2)]["VARIABLE"].values.tolist()
        if len(variables) == 0:
            return
        all_domains = list(set([x for sublist in self.csp[self.csp["VARIABLE"].isin(variables)]['DOMAINS'] .values.tolist() for x in sublist]))
        scene_dict = {}

        for domain in all_domains:
            scene = self.mapping_df.iloc[domain]['scene_id']
            if not scene in scene_dict:
                scene_dict[scene] = []
            scene_dict[scene].append(domain)
        for scene in scene_dict:
            domains = scene_dict[scene]        
            self.addConstraint(lambda *dom, cur=domains: sum([1 if x in cur else 0 for x in dom]) <= 1 and len(set(dom)) == len(dom), variables)


        #BUILD ME
        var1 = dt.datetime.strptime(variable1, '%H:%M')
        var2 = dt.datetime.strptime(variable2, '%H:%M')
        time_difference = abs(var1 - var2)
        if time_difference < dt.timedelta(minutes=minutes):
            all_domains = self.csp[self.csp["VARIABLE"] == variable1]['DOMAINS'].values[0]
            scene_dict = {}
            for domain in all_domains:
                scenes = self.mapping_df.iloc[domain]['scene_id']
                #for scene in scenes:
                #    print(scene)
                    #if not scene in scene_dict:
                        #scene_dict[role] = {}
                    #if not role_actor[role] in role_dict[role]:
                    #    role_dict[role][role_actor[role]] = []
                    #role_dict[role][role_actor[role]].append(domain)
                    #print(scene_dict)
            #for role in role_dict:
            #    for current_actor in role_dict[role]:
            #        current_domains = role_dict[role][current_actor]
            #        other_actors = [actor for actor in role_dict[role] if actor is not current_actor]
            #        other_domains = [domains for actor in other_actors for domains in role_dict[role]#[actor]]
            #        self.addConstraint(lambda domain1, domain2, cur=current_domains, #othr=other_domains:
            #                            not all([domain1 in cur, domain2 in othr]), (variable1, variable2))

if __name__ == '__main__':
    from constraint_input import ShiftInput
    from constraint_output import combine_solution, format_output
    from constraint_testing import timeout
    import time
    
    test_shift = {
    "increment": "00:15",
    "tours": ["14:30", "15:30", "16:30"],
    "break_time": { 
        "start": "16:00",
        "end": "16:25"
        },
    "bookings": {   
        1: ["14:00"],
        #2: ["14:00"],
        3: ["12:00", "18:30"],
        4: ["16:00"]
        },
    "shifts": { 
        "TK": { 
            "start": "12:15",
            "end": "20:00"
            },
        "PP": { 
            "start": "12:15",
            "end": "20:00"
            },
        "PA": {
            "start": "12:15",
            "end": "20:00"
            },
        "SS": {
            "start": "12:15",            
            "end":"20:00"
            },
        #"AU": { 
        #   "start": "12:15",
        #   "end": "20:00"
        #   },
        #"DS": { 
        #   "start": "12:15",
        #   "end": "20:00"
        #   },       
        }
    }
    print("BEGIN CSP TESTING...")
    Shift = ShiftInput(test_shift)
    print("INPUT CREATED")
    problem_class = ConstraintProblem(Shift)
    print("PROBLEM DEFINED")
    

    for test in problem_class._constraints:
        #print(test)
        pass
    t = time.process_time()
    @timeout(60)
    def solver(problem):
        try:
            return problem.getSolution()
        except Exception as e:
            raise e
    i = 0
    max_iter = 10
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

    #constraint_solution = problem_class.getSolution()
    if constraint_solution is not None:
        print("SOLUTION FOUND")
        output_df = combine_solution(constraint_solution, Shift.input_df)
        print(output_df)
        output_json = format_output(output_df, Shift)
        for key in output_json:
            print(key, output_json[key])
        
    else:
        print("No solution found")
    
    print("time elapsed: %f seconds" % (time.process_time() - t))