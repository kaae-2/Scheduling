import os
import pandas as pd
from itertools import product


def main(actor_df, list_of_actors_on_shift, scene_df, restaurant_df):
    actor_df = actor_df[actor_df['ID'].isin(list_of_actors_on_shift)]
    actor_df = actor_df.drop('NOTES', axis=1)
    role_list = list(set(scene_df) - (set(scene_df) - set(actor_df)))
    restaurant_list = list(set(scene_df) - (set(scene_df) - set(restaurant_df['RES_NAME'].values)))
    all_actor_roles = get_all_actor_roles(actor_df)
    all_actor_combinations = get_all_actor_combinations(all_actor_roles)
    all_possible_scenes = get_all_possible_scenes(scene_df, restaurant_list, role_list)
    all_playable_scenes = get_all_playable_scenes(all_actor_combinations, all_possible_scenes)
    possible_scenes_df = pd.DataFrame(all_playable_scenes, columns=['SCENE_NAME', 'RES_NAME', 'CHAR'])
    return possible_scenes_df


def get_all_actor_roles(actor_df):
    all_actor_roles = []
    for unique_id in actor_df['ID'].values:
        actor_roles = actor_df[actor_df['ID'] == unique_id]
        actor_roles = [[unique_id, x] for x in list(actor_roles[actor_roles.isin([1])].dropna(axis=1))]
        all_actor_roles.append(actor_roles)
    return all_actor_roles


def get_all_actor_combinations(all_actor_roles):
    actor_all_combinations = product(*all_actor_roles)
    actor_valid_combinations = []
    for combination in actor_all_combinations:
        all_roles = [x[1] for x in combination]
        if len(all_roles) != len(set(all_roles)):
            continue
        actor_valid_combinations.append(combination)
    return actor_valid_combinations


def get_all_possible_scenes(scene_df, list_of_restaurants, list_of_roles):
    all_possible_scenes = []
    for unique_id in list(set(scene_df['SCENE_NAME'].values)):
        possible_scene = scene_df[scene_df['SCENE_NAME'] == unique_id]
        possible_place = list(possible_scene[possible_scene[list_of_restaurants].isin([1])].dropna(axis=1))
        all_needed_roles = list(possible_scene[possible_scene[list_of_roles].isin([1])].dropna(axis=1))
        playable_scene = [[unique_id, x, all_needed_roles] for x in possible_place]
        for scene in playable_scene:
            all_possible_scenes.append(scene)
    return all_possible_scenes


def get_all_playable_scenes(all_actor_combinations, all_possible_scenes):
    all_playable_scenes = []
    for combination in all_actor_combinations:
        all_roles = [x[1] for x in combination]
        for possible_scene in all_possible_scenes:
            if not all(x in all_roles for x in possible_scene[2]):
                continue
            elif possible_scene in all_playable_scenes:
                continue
            all_playable_scenes.append(possible_scene)
    all_playable_scenes = get_all_actor_and_scene_combinations(all_playable_scenes, all_actor_combinations)
    return all_playable_scenes


def get_all_actor_and_scene_combinations(all_playable_scenes, combination_of_actors_on_shift):
    all_actor_and_scene_combinations = []
    for combination in combination_of_actors_on_shift:
        all_roles = [x[1] for x in combination]
        combination = list(combination)
        for playable_scene in all_playable_scenes:
            if all([x in all_roles for x in playable_scene[2]]):
                actor_and_scene_combination = playable_scene[:]
                substitution_roles = [x in playable_scene[2] for x in all_roles]
                substitution_roles = [i for i, x in enumerate(substitution_roles) if x]
                actor_and_scene_combination[2] = [combination[i] for i in substitution_roles]
                if actor_and_scene_combination in all_actor_and_scene_combinations:
                    continue
                all_actor_and_scene_combinations.append(actor_and_scene_combination)
    return all_actor_and_scene_combinations


if __name__ == '__main__':
    os.chdir('..')
    files = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    actor_list = ['PA', 'LE', 'TK', 'DS']

    from script import import_backend_data
    ACT, CHR, RES, SCE = import_backend_data.main(files)
    COM = main(ACT, actor_list, SCE, RES)
    print(COM.head())
    print(RES)
