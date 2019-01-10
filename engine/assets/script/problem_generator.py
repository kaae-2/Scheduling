import os
import random
from constraint import *
from script import constraint_optimizer
import datetime as dt


class ConstraintProblem(Problem):
    def __init__(self, my_input_df, my_dict_df, restaurant_df, tours, print_values=False):
        super(ConstraintProblem, self).__init__()
        self.csp = my_input_df
        self.dic = my_dict_df
        self.res = restaurant_df
        self.tour_times = tours
        self.setSolver(MinConflictsSolver())
        self.print_values = print_values
        self.variables = list(self.csp['VARIABLE'].values)
        self.domains = list(self.csp['DOMAINS'].values)
        self.char_values = list(self.dic['CHAR'].values)
        self.time_slices = self.get_time_slices()
        self.unique_scenes = self.get_unique_scenes()
        self.unique_chars = self.get_unique_chars()
        self.unique_actors = self.get_unique_actors()
        self.unique_restaurants = self.get_unique_restaurants()
        self.unique_actor_char_pairs = self.get_unique_actor_char_pairs()
        self.scene_res_pairs = self.get_unique_scene_res_pairs()
        self.meal_time = self.get_meal_times()
        self.null = self.dic[self.dic['SCENE_NAME'] == 'NO SCENE'].index.tolist()[0]
        self.initialize_variables(randomize=False)
        self.set_constraints()

    def initialize_variables(self, randomize=False, _if_special=True):
        index_list = list(range(len(self.variables)))
        if randomize:
            random.shuffle(index_list)
            if self.print_values:
                print("shuffled: ", index_list)
        self.remove_invalid_options()
        if _if_special:
            self.initialize_special_variables(index_list)
        else:
            for index in index_list:
                self.addVariable(self.variables[index], self.domains[index])

    def initialize_special_variables(self, index_list):
        if 'ALTAN' in self.unique_scenes:
            spec = ['FANEN', '3MUSIK', 'ALTAN']
            special_scenes = self.unique_scenes['ALTAN'] + self.unique_scenes['FANEN'] + self.unique_scenes['3MUSIK']
        else:
            if self.print_values:
                print('ALTAN NOT IN LIST')
            spec = ['FANEN', '3MUSIK', 'ALTAN NB: FIND SPILLERE']
            special_scenes = self.unique_scenes['FANEN'] + self.unique_scenes['3MUSIK'] + self.unique_scenes[
                'ALTAN NB: FIND SPILLERE']
        _tours = []
        for i, _tour in enumerate(self.tour_times):
            valid_special_scenes = self.dic[(self.dic['SHIFT_START'] <= _tour) & (self.dic['SHIFT_END'] >= _tour)]
            valid_special_scenes = valid_special_scenes[valid_special_scenes['SCENE_NAME'] == spec[i]].index.tolist()
            valid_special_scenes = [x for x in valid_special_scenes if x in special_scenes]
            tour_prep_time = (dt.datetime.combine(dt.date(1, 1, 1), _tour) - dt.timedelta(minutes=5)).time()
            if self.print_values:
                print(tour_prep_time, valid_special_scenes)
            self.addVariable(tour_prep_time, valid_special_scenes)
            _tours.append(tour_prep_time)
        self.addConstraint(lambda *dom: len(set(dom)) == len(dom), _tours)
        for index in index_list:
            self.addVariable(self.variables[index], [x for x in self.domains[index] if x not in special_scenes])

    def remove_invalid_options(self, rest=['KAT', 'LAU', 'VAR']):
        for res in rest:
            meals = self.meal_time[res]
            for i, _ in enumerate(meals[:-1]):
                variables = [j for j in self.variables if (meals[i][1] < j < meals[i+1][0])]
                var_indices = [self.variables.index(j) for j in variables]
                for index in var_indices:
                    self.domains[index] = [k for k in self.domains[index] if k not in self.unique_restaurants[res]]

    def set_constraints(self):
        self.set_relational_constraints()
        self.set_meal_time_constraints()
        # self.set_sequential_constraints(increment=3)
        print('CONSTRAINTS ADDED')

    def set_sequential_constraints(self, increment=5):
        i = increment
        while i < len(self.variables):
            self.sequence_constraint(i - increment, i)
            # i += 1
            i += increment
        else:
            self.sequence_constraint(i-increment, len(self.variables))

    def sequence_constraint(self, begin, end, max_iter=1):
        for restaurant in self.unique_restaurants:
            self.addConstraint(lambda *dom, res=restaurant:
                               sum([el in self.unique_restaurants[res] for el in dom]) <= max_iter,
                               (self.variables[begin:end]))

    def set_meal_time_constraints(self, min_visit=2):
        for res in self.meal_time:
            restaurant = self.unique_restaurants[res]
            if restaurant is None:
                continue
            for meal in self.meal_time[res]:
                if meal[0] is None:
                    continue
                variables = [x for x in self.variables if meal[0] <= x < meal[1]]
                self.addConstraint(lambda *dom, r=restaurant:
                                   sum([1 if el in r else 0 for el in dom]) >= min_visit
                                   and len(set(dom)) == len(dom), variables)

    def set_relational_constraints(self):
        # self.addConstraint(lambda *dom, d=self.null: len(set([x for x in dom if x is not d])) ==
        #                    len([x for x in dom if x is not d]), self.variables)
        for variable1 in self.variables:
            for variable2 in self.variables:
                if variable1 < variable2:
                    self.set_actor_changing_time_constraint(variable1, variable2)

    def set_actor_changing_time_constraint(self, variable1, variable2, minutes=30):
        today = dt.date.today()
        time_difference = abs(dt.datetime.combine(today, variable1) - dt.datetime.combine(today, variable2))
        if time_difference < dt.timedelta(minutes=minutes):
            if self.print_values:
                pass
            for actor_char_pair in self.unique_actor_char_pairs:
                for actor in self.unique_actors:
                    if actor_char_pair[0] != actor:
                        continue
                    curr_role = self.unique_actor_char_pairs[actor_char_pair]
                    other_roles = [x for x in self.unique_actors[actor] if x not in curr_role]
                    self.addConstraint(lambda domain1, domain2, cur=curr_role, othr=other_roles:
                                       not all([domain1 in cur, domain2 in othr]),
                                       (variable1, variable2))

    def set_slice_independent_constraints(self, variable1, variable2):
        for scene_res_pair in self.scene_res_pairs:
            self.addConstraint(lambda domain1, domain2, sc_res_pair=scene_res_pair:
                               not all([(domain1 in self.scene_res_pairs[sc_res_pair]),
                                        (domain2 in self.scene_res_pairs[sc_res_pair])]),
                               (variable1, variable2))

    def get_meal_times(self):
        meal_times = []
        for restaurant in self.unique_restaurants:
            meal_df = self.res[self.res['RES_NAME'] == restaurant]
            meals = meal_df[['LUNCH_START', 'LUNCH_END']].values.tolist() + meal_df[['DINNER_START', 'DINNER_END']].values.tolist()  # + meal_df[['LATE_START', 'LATE_END']].values.tolist()
            meals = [[None, None] if type(x[0]) is not dt.time else x for x in meals]
            meal_times.append([restaurant, meals])
        meal_times = {a[0]: a[1] for a in meal_times}
        return meal_times

    def get_time_slices(self):
        time_slice = zip(self.dic[['SHIFT_START', 'SHIFT_END']].values.tolist())
        time_slice = sorted(set([tuple(x[0]) for x in time_slice]))
        time_slice = [list(x) for x in time_slice]
        if self.print_values:
            print(time_slice)
        return time_slice

    def get_unique_restaurants(self):
        all_restaurants = self.dic['RES_NAME'].values
        all_restaurants = [x for x in all_restaurants if x is not None]
        all_unique_restaurants = [x for x in sorted(set(all_restaurants))]
        unique_restaurants = []
        for unique_res in all_unique_restaurants:
            res_indices = []
            for i, res in enumerate(all_restaurants):
                if res == unique_res:
                    res_indices.append(i)
            if self.print_values:
                print('Restaurant %s is performed at in: %s' % (unique_res, str(res_indices)))
            unique_restaurants.append([unique_res, res_indices])
        unique_restaurants = {a[0]: a[1] for a in unique_restaurants}
        return unique_restaurants

    def get_unique_chars(self):
        all_char_indices = [tuple(j)[1] for i in list(self.dic['CHAR'].values) if i is not None for j in i]
        all_char_indices = [x for x in sorted(set(all_char_indices))]
        unique_chars = []
        for unique_char in all_char_indices:
            char_indices = []
            for i, chars in enumerate(self.char_values):
                if chars is None:
                    continue
                for char in chars:
                    if char[1] == unique_char:
                        char_indices.append(i)
            if self.print_values:
                print('Char %s is played in scenes: %s' % (unique_char, str(char_indices)))
            unique_chars.append([unique_char, char_indices])
        unique_chars = {a[0]: a[1] for a in unique_chars}
        return unique_chars

    def get_unique_actors(self):
        all_unique_actors = [tuple(j)[0] for i in list(self.dic['CHAR'].values) if i is not None for j in i]
        all_unique_actors = [x for x in sorted(set(all_unique_actors))]
        unique_actors = []
        for actors in all_unique_actors:
            actor_indices = []
            for i, chars in enumerate(self.char_values):
                if chars is None:
                    continue
                for char in chars:
                    if char[0] == actors:
                        actor_indices.append(i)
            if self.print_values:
                print('Actor %s is playing in scenes: %s' % (actors, str(actor_indices)))
            unique_actors.append([actors, actor_indices])
        unique_actors = {a[0]: a[1] for a in unique_actors}
        return unique_actors

    def get_unique_scenes(self):
        unique_scenes = []
        all_scenes = list(set(self.dic['SCENE_NAME'].values))
        for scene in all_scenes:
            scene_indices = list(self.dic.index[self.dic['SCENE_NAME'] == scene])
            if self.print_values:
                print("Scene %s can be played at: %s" % (scene, scene_indices))
            unique_scenes.append([scene, scene_indices])
        unique_scenes = {a[0]: a[1] for a in unique_scenes}
        return unique_scenes

    def get_unique_actor_char_pairs(self):
        all_actor_char_pairs = self.dic['CHAR'].values
        all_actor_char_pairs = sorted(set([tuple(x) for y in all_actor_char_pairs if y is not None for x in y]))
        all_actor_char_pairs = [list(x) for x in all_actor_char_pairs]
        actor_char_pairs = []
        for unique_actor_char in all_actor_char_pairs:
            actor_char_indices = []
            for i, chars in enumerate(self.char_values):
                if chars is None:
                    continue
                for char in chars:
                    # print(i, char)
                    if char == unique_actor_char:
                        actor_char_indices.append(i)
            if self.print_values:
                print('Actor %s is playing %s in scenes: %s'
                      % (unique_actor_char[0], unique_actor_char[1], str(actor_char_indices)))
            actor_char_pairs.append([tuple(unique_actor_char), actor_char_indices])
        actor_char_pairs = {a[0]: a[1] for a in actor_char_pairs}
        return actor_char_pairs

    def get_unique_scene_res_pairs(self):
        all_scene_res_pairs = zip(self.dic[['SCENE_NAME', 'RES_NAME']].values.tolist())
        all_scene_res_pairs = sorted(set([tuple(x[0]) for x in all_scene_res_pairs]))
        all_scene_res_pairs = [list(x) for x in all_scene_res_pairs]
        scene_res_pairs = []
        for pair in all_scene_res_pairs:
            pair_indices = list(self.dic.index[(self.dic['SCENE_NAME'] == pair[0])
                                               & (self.dic['RES_NAME'] == pair[1])])
            if self.print_values:
                print("Scene %s can be played at restaurant %s at:  %s" % (pair[0], pair[1], pair_indices))
            scene_res_pairs.append([pair, pair_indices])
        scene_res_pairs = {tuple(a[0]): a[1] for a in scene_res_pairs}
        return scene_res_pairs


def main(cleaned_input_df, time_delta, restaurant_df, tour_times, break_time, _print=True):
    example_solution, cleaned_input_df = constraint_optimizer.main(cleaned_input_df, time_delta, restaurant_df, tour_times, break_time)
    print(type(example_solution))
    if _print:
        if example_solution is not None:
            print("Printing a sample solution:")
            for key in sorted(example_solution):
                print(key, example_solution[key], cleaned_input_df.iloc[example_solution[key]].values.tolist())
        else:
            print("No solution found!")
    return example_solution


if __name__ == '__main__':
    os.chdir('..')
    print(os.getcwd())
    backend_file = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    shift_file = 'SHIFT_INPUT.xlsx'
    from script import input_data
    scene_play_delta = dt.timedelta(minutes=10)
    tour = [dt.time(14, 30), dt.time(15, 30), dt.time(16, 30)]
    time_off = [dt.time(16, 00), dt.time(16, 25)]
    RDY, ACT, CHR, RES, SCE = input_data.main(shift_file, backend_file)
    solution = main(RDY, scene_play_delta, RES, tour, time_off)
