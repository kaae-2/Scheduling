import os
import pandas as pd
import datetime as dt
from script import input_data, problem_generator


def main(cleaned_input_df, time_delta, restaurant_df, tours, break_time):
    print('Time for scenes: %s' % time_delta)
    if type(tours) == list:
        scene_variables = get_custom_play_deltas(cleaned_input_df, time_delta, tours, break_time)
    else:
        scene_variables = get_play_deltas(cleaned_input_df, time_delta)
    constraint_satisfaction_input_df = create_constraint_satisfaction_input(scene_variables, cleaned_input_df)
    constraint_satisfaction_input_df, cleaned_input_df = add_null_value(constraint_satisfaction_input_df, cleaned_input_df)
    problem_class = problem_generator.ConstraintProblem(constraint_satisfaction_input_df,
                                                        cleaned_input_df, restaurant_df, tours)
    constraint_solution = problem_class.getSolution()
    return constraint_solution, cleaned_input_df


def get_play_deltas(cleaned_input_df, time_delta):
    total_shift_start = cleaned_input_df['SHIFT_START'].min()
    total_shift_end = cleaned_input_df['SHIFT_END'].max()
    print('Calculating shifts from %s to %s' % (total_shift_start, total_shift_end))
    total_time_deltas = []
    shift_start = total_shift_start
    while shift_start < total_shift_end:
        total_time_deltas.append(shift_start)
        shift_start = (dt.datetime.combine(dt.date(1, 1, 1), shift_start) + time_delta).time()
    return total_time_deltas


def get_custom_play_deltas(cleaned_input_df, time_delta, tours, time_off):
    total_shift_start = cleaned_input_df['SHIFT_START'].min()
    total_shift_end = cleaned_input_df['SHIFT_END'].max()
    print('Calculating shifts from %s to %s' % (total_shift_start, total_shift_end))
    total_time_deltas = []
    shift_start = total_shift_start
    while shift_start < total_shift_end:
        if not (time_off[0] <= shift_start < time_off[1]):
            total_time_deltas.append(shift_start)
        if shift_start <= dt.time(12, 15):
            shift_start = dt.time(12, 20)
            continue
        shift_start = (dt.datetime.combine(dt.date(1, 1, 1), shift_start) + time_delta).time()
    for tour in tours:
        if tour in total_time_deltas:
            # total_time_deltas.append(tour)
            total_time_deltas.remove(tour)
        tour_prep_time = (dt.datetime.combine(dt.date(1, 1, 1), tour) - dt.timedelta(minutes=5)).time()
        if tour_prep_time  in total_time_deltas:
            # total_time_deltas.append(tour_prep_time)
            total_time_deltas.remove(tour_prep_time)
    total_time_deltas = sorted(total_time_deltas)
    return total_time_deltas


def create_constraint_satisfaction_input(scene_variables, cleaned_input_df):
    all_domains = []
    for variable in scene_variables:
        valid_domains = cleaned_input_df.index[(cleaned_input_df['SHIFT_START'] <= variable)
                                               & (cleaned_input_df['SHIFT_END'] > variable)]
        valid_domains = list(valid_domains)
        all_domains.append([variable, valid_domains])
    constraint_satisfaction_input = pd.DataFrame(all_domains, columns=['VARIABLE', 'DOMAINS'])
    return constraint_satisfaction_input


def add_null_value(constraint_input_df, cleaned_input_df):
    print(list(cleaned_input_df))

    null_value = pd.DataFrame([['NO SCENE', None, None,
                               cleaned_input_df['SHIFT_START'].min(), cleaned_input_df['SHIFT_END'].max()]],
                              columns=list(cleaned_input_df))

    if len(cleaned_input_df[cleaned_input_df['SCENE_NAME'] == 'ALTAN'].values.tolist()) == 0:
        altan = pd.DataFrame([['ALTAN NB: FIND SPILLERE', 'ALG', None,
                             dt.time(16, 25), dt.time(16, 35)]],
                             columns=list(cleaned_input_df))
        null_value = null_value.append(altan, ignore_index=True)
    cleaned_input_df = cleaned_input_df.append(null_value, ignore_index=True)
    null_index = cleaned_input_df.index[(cleaned_input_df['SCENE_NAME'] == 'NO SCENE') |
                                        (cleaned_input_df['SCENE_NAME'] == 'ALTAN NB: FIND SPILLERE')].tolist()[:]
    if type(null_index) is not list:
        null_index = [null_index]
    domains = []
    for i in constraint_input_df.index.values.tolist():
        domain = constraint_input_df.iloc[[i]]['DOMAINS'].tolist()[0]
        domain = domain + null_index
        domains.append(domain)

    constraint_input_df['DOMAINS'] = domains
    return constraint_input_df, cleaned_input_df


if __name__ == '__main__':
    os.chdir('..')
    print(os.getcwd())
    backend_file = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    shift_file = 'SHIFT_INPUT.xlsx'
    scene_play_delta = dt.timedelta(minutes=10)
    tour_times = [dt.time(14, 30), dt.time(15, 30), dt.time(16, 30)]
    time_off = [dt.time(16, 00), dt.time(16, 25)]
    RDY, ACT, CHR, RES, SCE = input_data.main(shift_file, backend_file)
    print(list(RDY))
    solution, RDY = main(RDY, scene_play_delta, RES, tours=tour_times, break_time=time_off)
    if solution is not None:
        print("Solution found")
        for key in solution:
            print(key, solution[key], RDY.iloc[solution[key]].values.tolist())

