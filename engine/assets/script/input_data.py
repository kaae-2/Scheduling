import pandas as pd
import os
from script import import_backend_data, get_possible_scenes


def main(filename, backend_filename):
    excel = pd.ExcelFile(filename)
    print('Using data from pane: "%s" to calculate shifts' % excel.sheet_names[0])
    shift_df = pd.read_excel(filename)
    time_slices = get_possible_time_slices(shift_df)
    actor_df, char_df, restaurant_df, scene_df = import_backend_data.main(backend_filename)
    cleaned_input_df = pd.DataFrame()
    for time_slice in time_slices:
        actor_list = time_slice[0]
        compiled_scene_df = get_possible_scenes.main(actor_df, actor_list, scene_df, restaurant_df)
        compiled_scene_df['SHIFT_START'] = time_slice[1][0]
        compiled_scene_df['SHIFT_END'] = time_slice[1][1]
        cleaned_input_df = cleaned_input_df.append(compiled_scene_df, ignore_index=True)
    return cleaned_input_df, actor_df, char_df, restaurant_df, scene_df


def get_possible_time_slices(shift_df):
    shift_times = set(list(shift_df['SHIFT_START'].values) + list(shift_df['SHIFT_END'].values))
    shift_times = [x for x in shift_times if x is not 'nan']
    print(shift_times)
    shift_times = sorted(shift_times)
    different_sub_shifts = []
    for i, _ in enumerate(shift_times[:-1]):
        different_sub_shifts.append([shift_times[i], shift_times[i+1]])
    possible_time_slices = []
    for sub_shift in different_sub_shifts:
        actors_on_sub_shift = shift_df[(shift_df['SHIFT_START'] <= sub_shift[0])
                                       & (shift_df['SHIFT_END'] >= sub_shift[1])]
        actors_on_sub_shift = list(actors_on_sub_shift['ID'].values)
        possible_time_slices.append([actors_on_sub_shift, sub_shift])
    return possible_time_slices


def remove_invalid_time_slices():
    pass


if __name__ == '__main__':
    os.chdir('..')
    print(os.getcwd())
    backend_file = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    shift_file = 'SHIFT_INPUT.xlsx'
    RDY, ACT, CHR, RES, SCE = main(shift_file, backend_file)
    print(RDY)
