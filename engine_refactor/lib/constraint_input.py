import pandas as pd
import os
import sqlite3
import itertools
import datetime as dt
import psycopg2


class ShiftInput():
    def __init__(self, shift):
        self.shift = shift
        self.conn = self.connect_db()
        self.actor_df = self.get_actor_df()
        self.role_df = self.get_all_roles()
        self.scenes_df = self.get_all_scenes()
        self.restaurant_df = self.get_restaurants()
        self.all_playable_scene_df, self.valid_role_list = self.get_valid_scenes()
        self.playable_scene_dict, self.time_slices = self.get_playable_scene_ids()
        self.time_increments = self.get_time_increments(increment=self.shift['increment'])
        self.input_df = self.transform_scene_dict_to_df()

    def connect_db(self):
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            print("TRYING TO CONNECT TO DB URL...")
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            print('Database connected...')
            return conn
        except:
            print('CANNOT FIND URL, CONNECTING TO LOCAL SQLITE DB')
            db = "db.sqlite"
            if os.path.isfile(db):
                conn = sqlite3.connect(db)
                print('Database connected...')
                return conn
            print('SQLITE DB DOES NOT EXIST')
            raise Exception("DATABASE DOES NOT EXIST")
            
    def get_actor_df(self):
        with self.conn:
            actors_on_staff = tuple([x for x in self.shift["shifts"]])
            sqlcmd = "SELECT * from actors where actor_initials in {}".format(str(actors_on_staff).replace(",)", ")"))
            return pd.read_sql(sqlcmd, self.conn)
    
    def get_all_roles(self):
        with self.conn:
            sqlcmd = """SELECT * from roles"""
            return(pd.read_sql(sqlcmd, self.conn))
    
    def get_all_scenes(self):
        with self.conn:
            sqlcmd = """ SELECT * from scenes"""
            return pd.read_sql(sqlcmd, self.conn)    
    
    def get_restaurants(self, small_restaurants=[1, 2, 3]):
        small_restaurants_without_bookings = tuple(x for x in small_restaurants if x not in self.shift["bookings"])
        sqlcmd = """SELECT * from restaurants inner join restaurants_scenes 
                    on restaurants.id = restaurants_scenes.restaurant_id 
                    where restaurants.id not in {}""".format(str(small_restaurants_without_bookings).replace(",)", ")"))
        with self.conn:
            rs = pd.read_sql(sqlcmd, self.conn)
            rs = rs.groupby([
                "restaurant_full_name",
                "restaurant_short_name", 
                "restaurant_seating",
                "restaurant_id"
                ])["scene_id"].apply(tuple).reset_index(name='scenes')
            return rs
    
    def get_valid_scenes(self):
        valid_roles = self.get_valid_roles()
        valid_role_combinations = self.get_valid_role_combinations(valid_roles)
        playable_scene_df = self.find_valid_scenes(valid_role_combinations)
        return playable_scene_df, valid_roles

    def get_valid_role_combinations(self, vr):
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

    def get_valid_roles(self):
        actor_id = tuple(self.actor_df["id"])
        sqlcmd = """SELECT * from actor_roles where actor_id in {}""".format(str(actor_id).replace(",)", ")"))
        with self.conn:
            ar = pd.read_sql(sqlcmd, self.conn)
            return ar.groupby(["actor_id"])["role_id"].apply(tuple)

    def find_valid_scenes(self, vrc):
        scene_id = tuple(self.scenes_df["id"])
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

    def get_time_slices(self):
        slices = []
        for actor in self.shift["shifts"]:
            for time in self.shift["shifts"][actor]:
                slices.append(self.shift["shifts"][actor][time])
        return list(sorted(set(slices)))
    
    def get_combination_of_actors_on_shift(self, time_slices):
        actors_on_shifts = []
        for i, _ in enumerate(time_slices[0:-1]):
                actor_initials_on_shift = [x for x in self.shift["shifts"] if self.shift["shifts"][x]['start']<=time_slices[i] and self.shift["shifts"][x]['end']>=time_slices[i+1]]
                actor_ids_on_shift = self.actor_df[self.actor_df['actor_initials'].isin(actor_initials_on_shift)]
                actors_on_shifts.append(actor_ids_on_shift['id'].values.tolist())
        return actors_on_shifts
    
    def get_valid_role_combinations(self, vr):
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

    def get_role_dict_combinations(self, rdicts):
        keys = rdicts.keys()
        values = (rdicts[key] for key in keys)
        combinations = tuple([dict(zip(keys, combination)) for combination in itertools.product(*values) if len(combination) == len(set(combination))])
        return combinations

    def get_playable_scene_ids(self):
        time_slices = self.get_time_slices()
        combination_of_actors_on_shift = self.get_combination_of_actors_on_shift(time_slices)
        valid_scenes = {}
        for i, combination in enumerate(combination_of_actors_on_shift):
            shift_roles = self.valid_role_list[self.valid_role_list.index.isin(combination)]
            valid_shift_roles = self.get_valid_role_combinations(shift_roles)
            valid_scene_ids = ()
            valid_scene_dict = {}
            for scene_id, row in self.all_playable_scene_df.iteritems():
                res = (x for x in self.restaurant_df['scenes'] if scene_id in x)
                for role_combination in valid_shift_roles:
                    if all(a in role_combination for a in row):
                        valid_scene_ids = valid_scene_ids + (scene_id,)
                        role_dict = {}
                        for role in row:
                            role_dict[role] = tuple([actor_id[0] for actor_id in shift_roles.iteritems() if role in actor_id[1]])
                        role_dict = self.get_role_dict_combinations(role_dict)
                        rest_dict = {}
                        for r in res:
                            a = self.restaurant_df[self.restaurant_df['scenes'] == r]
                            a = a['restaurant_id'].values.tolist()[0]
                            rest_dict[a] = role_dict
                        valid_scene_dict[scene_id] = rest_dict
                        break
            valid_scenes[time_slices[i]] = valid_scene_dict                                  
        return valid_scenes, time_slices
    
    def transform_scene_dict_to_df(self, columns=['time', 'scene_id', 'restaurant_id', 'role_actor']):
        lst = []
        for time in self.playable_scene_dict:
            for scene_id in self.playable_scene_dict[time]:
                for restaurant_id in self.playable_scene_dict[time][scene_id]:
                    for role_actor in self.playable_scene_dict[time][scene_id][restaurant_id]:
                        row = [time, scene_id, restaurant_id, role_actor]
                        lst.append(row)
        df = pd.DataFrame(lst, columns=columns)
        return df

    def get_time_increments(self, increment="00:15"):
        td = dt.datetime.strptime(self.time_slices[0], '%H:%M')
        output = []
        inc = dt.datetime.strptime(increment, "%H:%M")
        inc = dt.timedelta(minutes=inc.minute)
        while td < dt.datetime.strptime(self.time_slices[-1], '%H:%M'):
            output.append(str(td.time())[0:5])
            td += inc          
        return output


if __name__ == "__main__":
    test_shift = {
        "increment": "00:30",
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

    Shift = ShiftInput(test_shift)
    print(Shift.input_df)
    print(Shift.shift)
