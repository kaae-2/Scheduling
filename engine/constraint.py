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
            "end":"21:00"}
    }


def prepare_input_for_model(shift):
    actor_df = get_actor_df(shift)
    roles_df = get_all_roles()
    scenes_df = get_all_scenes()
    all_valid_scene_ids, valid_role_list = get_valid_scenes(scenes_df, roles_df, actor_df)
    playable_scene_ids = get_playable_scene_ids(all_valid_scene_ids, shift, valid_role_list, actor_df)


def get_playable_scene_ids(scene_ids, shift, valid_role_list, actor_df):
        time_slices = get_time_slices(shift)
        combination_of_actors_on_shift = get_combination_of_actors_on_shift(shift, time_slices)
        for combination in combination_of_actors_on_shift:
                
        


def get_combination_of_actors_on_shift(shift, time_slices):
        actors_on_shifts = []
        for i, _ in enumerate(time_slices[0:-1]):
                actors_on_shifts.append([x for x in shift if shift[x]['start']<=time_slices[i] and shift[x]['end']>=time_slices[i+1]])
        return actors_on_shifts
                

def get_valid_scenes(scenes_df, roles_df, actor_df):
        valid_roles = get_valid_roles(roles_df, actor_df)
        valid_role_combinations, valid_role_list = get_valid_role_combinations(valid_roles)
        return find_valid_scenes(valid_role_combinations, scenes_df), valid_role_list
        
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
        return valid_role_combinations, vr
        

def find_valid_scenes(vrc, sdf):
        scene_id = tuple(sdf["id"])
        sqlcmd = """SELECT * from roles_scenes where scene_id in {}""".format(str(scene_id))
        with sqlite3.connect("db.sqlite") as conn:
                rs = pd.read_sql(sqlcmd, conn)
        rs = rs.groupby(["scene_id"])["role_id"].apply(tuple)
        playable_scene_ids = []
        for scene in rs:
                index = rs[rs == scene].index[0]
                for combination in vrc:
                        if all(x in combination for x in scene):
                                if not index in playable_scene_ids:
                                        playable_scene_ids.append(index)
                                        break
        return playable_scene_ids
        

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