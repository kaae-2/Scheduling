import os
import pandas as pd
import string
from openpyxl import load_workbook


def main(example_solution, cleaned_input_df, actor_df, character_df,
         restaurant_df, scene_df, file_name, tours, break_time):
    if example_solution is not None:
        output_df = clean_input_for_main(example_solution, cleaned_input_df,
                                         actor_df, character_df, restaurant_df,
                                         scene_df, tours, break_time)

        generate_excel_output_main(output_df, file_name)
        actors = [x[0] for y in cleaned_input_df['CHAR'].values.tolist() if y is not None for x in y]
        for actor in list(set(actors)):

            actor_output = clean_input_for_actor(example_solution, actor, cleaned_input_df, actor_df,
                                                 character_df, restaurant_df, scene_df, tours, break_time)

            generate_excel_output_actor(actor_output, file_name, sheet_name=actor)


def clean_input_for_actor(example_solution, actor, cleaned_input_df, actor_df,
                          character_df, restaurant_df, scene_df, tours, break_time):
    output_df = []
    for key in sorted(example_solution):
        values_of_interest = cleaned_input_df.iloc[example_solution[key]]
        values_of_interest = values_of_interest[['CHAR', 'RES_NAME', 'SCENE_NAME']].values.tolist()
        values_of_interest = clean_actor_char_data_for_actor(values_of_interest[0], actor, actor_df, character_df) + \
            clean_restaurant_data(values_of_interest[1], restaurant_df) + \
            clean_scene_data(values_of_interest[2], scene_df)
        output_df.append([key] + values_of_interest)

    output_df = add_tours_and_breaks_to_solution_for_actor(output_df, tours, break_time)
    output_df = sorted(output_df)
    output_df = pd.DataFrame(output_df, columns=['TIME', 'WHO', 'WITH WHO', 'WHERE', 'WHAT'])
    return output_df


def clean_input_for_main(example_solution, cleaned_input_df, actor_df, character_df,
                         restaurant_df, scene_df, tours, break_time):
    output_df = []
    for key in sorted(example_solution):
        values_of_interest = cleaned_input_df.iloc[example_solution[key]]
        values_of_interest = values_of_interest[['CHAR', 'RES_NAME', 'SCENE_NAME']].values.tolist()
        values_of_interest = clean_actor_char_data(values_of_interest[0], actor_df, character_df) + \
            clean_restaurant_data(values_of_interest[1], restaurant_df) + \
            clean_scene_data(values_of_interest[2], scene_df)
        output_df.append([key] + values_of_interest)

    output_df = add_tours_and_breaks_to_solution(output_df, tours, break_time)
    output_df = sorted(output_df)
    output_df = pd.DataFrame(output_df, columns=['TIME', 'WHO', 'WHERE', 'WHAT'])
    return output_df


def add_tours_and_breaks_to_solution_for_actor(sol, tours, break_time):
    for _tour in tours:
        sol.append([_tour, '-', '-', 'Varnæs, Laura, Katrine', 'Rundvisning'])
    br = 0
    while br < len(break_time):
        sol.append([break_time[br], 'Alle', 'Alle', '-', 'Pause til %s' % break_time[br+1]])
        br += 2
    return sol


def add_tours_and_breaks_to_solution(sol, tours, break_time):
    for _tour in tours:
        sol.append([_tour, '-', 'Varnæs, Laura, Katrine', 'Rundvisning'])
    br = 0
    while br < len(break_time):
        sol.append([break_time[br], 'Alle', '-', 'Pause til %s' % break_time[br+1]])
        br += 2
    return sol


def generate_excel_output_actor(excel_df, file_name, sheet_name='Timetable'):
    name = pd.ExcelFile(file_name).sheet_names[0]
    book = load_workbook("./output/%s.xlsx" % name)
    writer = pd.ExcelWriter("./output/%s.xlsx" % name, engine='openpyxl')
    writer.book = book
    excel_df.to_excel(writer, sheet_name=sheet_name)
    # asx = list(string.ascii_uppercase)
    # for i, col in enumerate(list(excel_df)):
    #     x = max(excel_df[col].str.len())
    #     if type(x) is not int:
    #         x = 12
    #     writer.sheets[sheet_name].set_column('%s:%s' % (asx[i+1], asx[i+1]), x, None)
    writer.save()


def generate_excel_output_main(excel_df, file_name, sheet_name='Timetable'):
    name = pd.ExcelFile(file_name).sheet_names[0]
    writer = pd.ExcelWriter("./output/%s.xlsx" % name, engine='xlsxwriter')
    excel_df.to_excel(writer, sheet_name=sheet_name)
    asx = list(string.ascii_uppercase)
    for i, col in enumerate(list(excel_df)):
        x = max(excel_df[col].str.len())
        if type(x) is not int:
            x = 12
        writer.sheets[sheet_name].set_column('%s:%s' % (asx[i+1], asx[i+1]), x, None)
    writer.save()


def clean_actor_char_data_for_actor(char, actor, actor_df, character_df):
    cleaned_output = []
    if char is None:
        return [None, None]
    actor_name = actor_df['ACT_NAME'][actor_df['ID'] == actor].values.tolist()
    for ch in char:
        act = actor_df['ACT_NAME'][actor_df['ID'] == ch[0]].values.tolist()
        role = character_df['CHAR_FULLNAME'][character_df['CHAR'] == ch[1]].values.tolist()
        cleaned_output.append(act + role)
    out = [None, None]
    if any([x[0] == actor_name[0] for x in cleaned_output]):
        out = [" - ".join(["%s spiller %s" % (x[0], x[1]) for x in cleaned_output if x[0] == actor_name[0]]),
               " - ".join(["%s spiller %s" % (x[0], x[1]) for x in cleaned_output if x[0] != actor_name[0]])]
    return out


def clean_actor_char_data(char, actor_df, character_df):
    cleaned_output = []
    if char is None:
        return [None]
    for ch in char:
        actor = actor_df['ACT_NAME'][actor_df['ID'] == ch[0]].values.tolist()
        role = character_df['CHAR_FULLNAME'][character_df['CHAR'] == ch[1]].values.tolist()
        cleaned_output.append(actor + role)
    cleaned_output = ["%s spiller %s" % (x[0], x[1])  for x in cleaned_output]
    cleaned_output = [' - '.join(cleaned_output)]
    return cleaned_output


def clean_restaurant_data(restaurant, restaurant_df):
    if restaurant is None:
        return [None]
    return restaurant_df['RES_FULLNAME'][restaurant_df['RES_NAME'] == restaurant].values.tolist()


def clean_scene_data(scene, scene_df):
    if scene is None:
        return [None]
    return scene_df['SCENE_FULLNAME'][scene_df['SCENE_NAME'] == scene].values.tolist()


if __name__ == '__main__':
    os.chdir('..')
    print(os.getcwd())
    backend_file = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    shift_file = 'SHIFT_INPUT.xlsx'
    import datetime as dt
    from script import input_data, constraint_optimizer

    scene_play_delta = dt.timedelta(minutes=10)
    tour = [dt.time(14, 30), dt.time(15, 30), dt.time(16, 30)]
    time_off = [dt.time(16, 00), dt.time(16, 25)]
    RDY, ACT, CHR, RES, SCE = input_data.main(shift_file, backend_file)
    solution, RDY = constraint_optimizer.main(RDY, scene_play_delta, RES, tour, time_off)
    main(solution, RDY, ACT, CHR, RES, SCE, shift_file, tour, time_off)
