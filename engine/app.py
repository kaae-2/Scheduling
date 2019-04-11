#-*- coding: utf-8 -*-
import pandas as pd
import os
import sys
import sqlite3
import json
import itertools
import datetime as dt
from constraint import *


def run_model(shift):
    actor_df = get_actor_df(shift["shifts"])
    roles_df = get_all_roles()
    scenes_df = get_all_scenes()
    restaurant_df = get_restaurants(shift["bookings"])
    all_playable_scene_df, valid_role_list = get_valid_scenes(scenes_df, roles_df, actor_df)
    playable_scene_dict, time_slices = get_playable_scene_ids(all_playable_scene_df, shift["shifts"], valid_role_list, actor_df, restaurant_df)
    input_df = transform_scene_dict_to_df(playable_scene_dict)
    time_increments = get_time_increments(time_slices, increment=shift['increment'])
    problem_class = ConstraintProblem(input_df, time_increments, shift["bookings"])
    constraint_solution = problem_class.getSolution()
    output_df = combine_solution(constraint_solution, input_df)
    output_json = format_output(output_df, scenes_df, restaurant_df, roles_df, actor_df)
    return output_json
    


class ConstraintProblem(Problem):
    def __init__(self, input_df, time_increments, bookings):
        super(ConstraintProblem, self).__init__()
        self.setSolver(MinConflictsSolver())
        self.mapping_df = input_df
        self.booking_input = self.get_booking_input(bookings)
        self.csp = self.create_constraint_satisfaction_input(input_df, time_increments)
        self.initialize_variables()
        self.set_constraints() 

    def set_constraints(self):
        #Adding all the constraints. 
        self.addConstraint(AllDifferentConstraint())
        self.set_relational_constraints()
        if len(self.booking_input) > 0:
                self.set_booking_constraints()
              
    def initialize_variables(self):
        for _, i in self.csp.iterrows():
            self.addVariable(i['VARIABLE'], i['DOMAINS'])
        
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

    def set_booking_constraints(self, min_visits=2):
        for restaurant in self.booking_input:
            for booking in self.booking_input[restaurant]["booking"]:
                variables = self.csp[(self.csp["VARIABLE"] > booking[0]) & (self.csp["VARIABLE"] <= booking[1])]["VARIABLE"].values.tolist()
                self.addConstraint(lambda *dom: sum([1 if x in self.booking_input[restaurant]["domains"] else 0 for x in dom]) >= min_visits and len(set(dom)) == len(dom), variables)
    
    def set_unique_role_constraints(self, variable1, variable2, minutes=120):
        var1 = dt.datetime.strptime(variable1, '%H:%M')
        var2 = dt.datetime.strptime(variable2, '%H:%M')
        time_difference = abs(var1 - var2)
        if time_difference < dt.timedelta(minutes=minutes):
            all_domains = self.csp[self.csp["VARIABLE"] == variable1]['DOMAINS'].values[0]
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
                    self.addConstraint(lambda domain1, domain2, cur=current_domains, othr=other_domains:
                                        not all([domain1 in cur, domain2 in othr]), (variable1, variable2))


    def remove_domains_outside_booking_small_restaurants(self, time, valid_domains, small_restaurants=[1, 2, 3]):
        small_restaurants_with_booking = [x for x in small_restaurants if x in self.booking_input]
        pruned_domains = valid_domains
        for restaurant in small_restaurants_with_booking:
            if all([time <= booking[0] or time > booking[1] for booking in self.booking_input[restaurant]["booking"]]):
                pruned_domains = [x for x in pruned_domains if x not in self.booking_input[restaurant]["domains"]] 
        return pruned_domains 
    
    def get_booking_input(self, bookings, seating_minutes=120):
        # output format: Dictionary = {
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

    def set_relational_constraints(self):
        # set constraints that are relevant between 2 time points. 
        variables = self.csp['VARIABLE'].values
        for variable1 in variables:
                for variable2 in variables:
                    if variable1 < variable2:
                        self.set_actor_changing_time_constraint(variable1, variable2)
                        self.set_unique_role_constraints(variable1, variable2)
    
    def set_actor_changing_time_constraint(self, variable1, variable2, minutes=30):
        var1 = dt.datetime.strptime(variable1, '%H:%M')
        var2 = dt.datetime.strptime(variable2, '%H:%M')
        time_difference = abs(var1 - var2)
        if time_difference < dt.timedelta(minutes=minutes):
            all_domains = self.csp[self.csp["VARIABLE"] == variable1]['DOMAINS'].values[0]
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
                    self.addConstraint(lambda domain1, domain2, cur=current_domains, othr=other_domains:
                                        not all([domain1 in cur, domain2 in othr]), (variable1, variable2))



def format_output(output_df, scenes_df, restaurant_df, roles_df, actor_df):
        output_json = {}
        for row in output_df.iterrows():
                _, data = row
                time = data['time']
                scene = scenes_df[scenes_df['id'] == data['scene_id']]
                scene = scene['scene_full_name'].values[0]
                restaurant = restaurant_df[restaurant_df['restaurant_id'] == data['restaurant_id']]
                restaurant = restaurant['restaurant_full_name'].values[0]
                role_actor = []
                for key in data['role_actor']:
                        role = roles_df[roles_df['id'] == key]
                        role = role['role_full_name'].values[0]
                        actor = actor_df[actor_df['id'] == data['role_actor'][key]]
                        actor = actor['actor_full_name'].values[0]
                        role_actor.append([role, actor])

                output_json[time] = {
                        'scene': scene, 
                        'restaurant': restaurant, 
                        'role_actor': [{
                                'role': x[0],
                                'actor': x[1]
                                } for x in role_actor
                                ]}
        return output_json

def combine_solution(solution, input_df):
        columns=list(input_df)
        output_lst = []
        for time in solution:
                df = input_df.iloc[[solution[time]]]
                lst = df[[x for x in list(df) if x != 'time']].values[0].tolist()
                output_lst.append([time] + lst)
        output_df = pd.DataFrame(output_lst, columns=columns)
        return output_df

def get_time_increments(time_slices, increment="00:15"):
        td = dt.datetime.strptime(time_slices[0], '%H:%M')
        output = []
        inc = dt.datetime.strptime(increment, "%H:%M")
        inc = dt.timedelta(minutes=inc.minute)
        while td < dt.datetime.strptime(time_slices[-1], '%H:%M'):
                output.append(str(td.time())[0:5])
                td += inc          
        return output

def transform_scene_dict_to_df(input_dict, columns=['time', 'scene_id', 'restaurant_id', 'role_actor']):
        lst = []
        for time in input_dict:
                for scene_id in input_dict[time]:
                        for restaurant_id in input_dict[time][scene_id]:
                                for role_actor in input_dict[time][scene_id][restaurant_id]:
                                        row = [time, scene_id, restaurant_id, role_actor]
                                        lst.append(row)
        df = pd.DataFrame(lst, columns=columns)
        return df

def get_playable_scene_ids(vsdf, shift, valid_role_list, actor_df, restaurant_df):
        time_slices = get_time_slices(shift)
        combination_of_actors_on_shift = get_combination_of_actors_on_shift(shift, time_slices, actor_df)
        valid_scenes = {}
        for i, combination in enumerate(combination_of_actors_on_shift):
                shift_roles = valid_role_list[valid_role_list.index.isin(combination)]
                valid_shift_roles = get_valid_role_combinations(shift_roles)
                valid_scene_ids = ()
                valid_scene_dict = {}
                for scene_id, row in vsdf.iteritems():
                        res = (x for x in restaurant_df['scenes'] if scene_id in x)
                        for role_combination in valid_shift_roles:
                                if all(a in role_combination for a in row):
                                        valid_scene_ids = valid_scene_ids + (scene_id,)
                                        role_dict = {}
                                        for role in row:
                                                role_dict[role] = tuple([actor_id[0] for actor_id in shift_roles.iteritems() if role in actor_id[1]])
                                        role_dict = get_role_dict_combinations(role_dict)
                                        rest_dict = {}
                                        for r in res:
                                                a = restaurant_df[restaurant_df['scenes'] == r]
                                                a = a['restaurant_id'].values.tolist()[0]
                                                rest_dict[a] = role_dict
                                        valid_scene_dict[scene_id] = rest_dict
                                        break
                valid_scenes[time_slices[i]] = valid_scene_dict                                                 
        return valid_scenes, time_slices

def get_role_dict_combinations(rdicts):
        keys = rdicts.keys()
        values = (rdicts[key] for key in keys)
        combinations = tuple([dict(zip(keys, combination)) for combination in itertools.product(*values) if len(combination) == len(set(combination))])
        return combinations           

def get_combination_of_actors_on_shift(shift, time_slices, actor_df):
        actors_on_shifts = []
        for i, _ in enumerate(time_slices[0:-1]):
                actor_initials_on_shift = [x for x in shift if shift[x]['start']<=time_slices[i] and shift[x]['end']>=time_slices[i+1]]
                actor_ids_on_shift = actor_df[actor_df['actor_initials'].isin(actor_initials_on_shift)]
                actors_on_shifts.append(actor_ids_on_shift['id'].values.tolist())
        return actors_on_shifts
                
def get_valid_scenes(scenes_df, roles_df, actor_df):
        valid_roles = get_valid_roles(roles_df, actor_df)
        valid_role_combinations = get_valid_role_combinations(valid_roles)
        playable_scene_df = find_valid_scenes(valid_role_combinations, scenes_df)
        return playable_scene_df, valid_roles
        
def get_valid_roles(rdf, adf):
        actor_id = tuple(adf["id"])
        sqlcmd = """SELECT * from actor_roles where actor_id in {}""".format(str(actor_id).replace(",)", ")"))
        with sqlite3.connect("db.sqlite") as conn:
                ar = pd.read_sql(sqlcmd, conn)
        return ar.groupby(["actor_id"])["role_id"].apply(tuple)

def get_valid_role_combinations(vr):
        valid_role_list = []
        for roles in vr:
                index = vr[vr == roles].index[0]
                valid_role_list.append({i:index for i in roles})
        all_role_combinations = itertools.product(*valid_role_list)
        valid_role_combinations = []
        for combination in all_role_combinations:
                if len(combination) != len(set(combination)):
                        continue
                valid_role_combinations.append(combination)
        return valid_role_combinations

def get_restaurants(bookings, small_restaurants=[1, 2, 3]):
    small_restaurants_without_bookings = tuple(x for x in small_restaurants if x not in bookings)
    sqlcmd = """SELECT * from restaurants inner join restaurants_scenes 
                on restaurants.id = restaurants_scenes.restaurant_id 
                where restaurants.id not in {}""".format(str(small_restaurants_without_bookings).replace(",)", ")"))
    with sqlite3.connect("db.sqlite") as conn:
        rs = pd.read_sql(sqlcmd, conn)
    rs = rs.groupby([
        "restaurant_full_name",
        "restaurant_short_name", 
        "restaurant_seating",
        "restaurant_id"
        ])["scene_id"].apply(tuple).reset_index(name='scenes')
    return rs            

def find_valid_scenes(vrc, sdf):
        scene_id = tuple(sdf["id"])
        sqlcmd = """SELECT * from roles_scenes where scene_id in {}""".format(str(scene_id).replace(",)", ")"))
        with sqlite3.connect("db.sqlite") as conn:
                rs = pd.read_sql(sqlcmd, conn)
        rs = rs.groupby(["scene_id"])["role_id"].apply(tuple)
        playable_scene_ids = []
        
        ### Is this bit necessary?
        for scene in rs:
                index = rs[rs == scene].index[0]
                for combination in vrc:
                        if all(x in combination for x in scene):
                                if not index in playable_scene_ids:
                                        playable_scene_ids.append(index)
                                        break
        playable_scene_df = rs[rs.index.isin(playable_scene_ids)]
        return playable_scene_df
        
def get_all_scenes():
    with sqlite3.connect("db.sqlite") as conn:
        sqlcmd = """ SELECT * from scenes"""
        return pd.read_sql(sqlcmd, conn)           

def get_all_roles():
        with sqlite3.connect("db.sqlite") as conn:
                sqlcmd = """SELECT * from roles"""
                return(pd.read_sql(sqlcmd, conn))

def get_time_slices(shift):
    slices = []
    for actor in shift:
        for time in shift[actor]:
            slices.append(shift[actor][time])
    return list(sorted(set(slices)))

def get_actor_df(shift):
    with sqlite3.connect("db.sqlite") as conn:
        actors_on_staff = tuple([x for x in shift])
        sqlcmd = "SELECT * from actors where actor_initials in {}".format(str(actors_on_staff).replace(",)", ")"))
        return pd.read_sql(sqlcmd, conn)

if __name__ == '__main__':
        os.chdir(os.path.dirname(sys.argv[0]))
        
        test_shift = {
        "increment": "00:15",
        "tours": ["14:30", "15:30", "16:30"],
        "break_time": { "start": "16:00",
                        "end": "16:25"},
        "bookings": {   #1: ["14:00"],
                        #2: ["14:00"],
                        #3: ["12:00", "18:30"]
                    },
        "shifts": { "TK": { "start":"12:30",
                            "end":"19:00"},
                    "AH": { "start":"12:30",
                            "end":"19:00"},
                    "PA": { "start":"12:30",
                            "end":"19:00"},
                    "SS": { "start":"12:30",
                            "end":"19:00"},
                    "AU": { "start":"12:30",
                            "end":"19:00"},
                    "DS": { "start":"12:30",
                            "end":"19:00"},
                }
        }

        if len(sys.argv) > 1:
                test_shift = json.loads(sys.argv[1])
                
        output = run_model(test_shift)

        if len(sys.argv) > 1:
            print(json.dumps(output))
        else:
            for key in output:
                print(key, output[key])
            #print(json.dumps(output, ensure_ascii=False))

        #print(str(output))