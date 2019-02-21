import pandas as pd
import os
import sys
import sqlite3
import json
import itertools

test_shift = {
    "TK": {"start":"12:00",
            "end":"21:00"},
    "AH": {"start":"13:00",
            "end":"21:00"},
    "PA": {"start":"13:00",
            "end":"19:00"},
    "SS": {"start":"13:00",
            "end":"21:00"},
    "AU": {"start":"12:00",
            "end":"21:00"},
    "DS": {"start":"12:00",
            "end":"19:00"},
    }


def prepare_input_for_model(shift):
    actor_df = get_actor_df(shift)
    roles_df = get_all_roles()
    scenes_df = get_all_scenes()
    all_valid_scene_ids, valid_role_list, scenes_with_roles_df = get_valid_scenes(scenes_df, roles_df, actor_df)
    playable_scene_ids = get_playable_scene_ids(scenes_with_roles_df, shift, valid_role_list, actor_df)
    #print(playable_scene_ids)


def get_playable_scene_ids(scene_ids, shift, valid_role_list, actor_df):
        time_slices = get_time_slices(shift)
        combination_of_actors_on_shift = get_combination_of_actors_on_shift(shift, time_slices, actor_df)
        # print(valid_role_list)
        for combination in combination_of_actors_on_shift:
                #print(combination)
                shift_roles = valid_role_list[valid_role_list.index.isin(combination)]
                valid_shift_roles = get_valid_role_combinations(shift_roles)
                print(scene_ids)
                for id, roles in enumerate(scene_ids):
                        scene_id = id + 1
                        print(scene_id, roles)
                        for i in valid_shift_roles:
                                print(i)

        return __name__
                

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
        valid_scenes, scenes_with_roles_df = find_valid_scenes(valid_role_combinations, scenes_df)
        return valid_scenes, valid_roles, scenes_with_roles_df
        
def get_valid_roles(rdf, adf):
        actor_id = tuple(adf["id"])
        sqlcmd = """SELECT * from actor_roles where actor_id in {}""".format(str(actor_id))
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
        

def find_valid_scenes(vrc, sdf):
        scene_id = tuple(sdf["id"])
        sqlcmd = """SELECT * from roles_scenes where scene_id in {}""".format(str(scene_id))
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
        
        return playable_scene_ids, rs
        

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
        sqlcmd = "SELECT * from actors where actor_initials in {}".format(str(actors_on_staff))
        return pd.read_sql(sqlcmd, conn)

if __name__ == '__main__':
    prepare_input_for_model(test_shift)