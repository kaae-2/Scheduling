import pandas as pd

def combine_solution(solution, input_df):
    columns=list(input_df)
    output_lst = []
    for time in solution:
        df = input_df.iloc[[solution[time]]]
        lst = df[[x for x in list(df) if x != 'time']].values[0].tolist()
        output_lst.append([time] + lst)
    output_df = pd.DataFrame(output_lst, columns=columns)
    return output_df
    
def format_output(output_df, ShiftClass):
    output_json = {}
    for row in output_df.iterrows():
        _, data = row
        time = data['time']
        scene = ShiftClass.scenes_df[ShiftClass.scenes_df['id'] == data['scene_id']]
        scene = scene['scene_full_name'].values[0]
        restaurant = ShiftClass.restaurant_df[ShiftClass.restaurant_df['restaurant_id'] == data['restaurant_id']]
        restaurant = restaurant['restaurant_full_name'].values[0]
        role_actor = []
        for key in data['role_actor']:
            role = ShiftClass.role_df[ShiftClass.role_df['id'] == key]
            role = role['role_full_name'].values[0]
            actor = ShiftClass.actor_df[ShiftClass.actor_df['id'] == data['role_actor'][key]]
            actor = actor['actor_full_name'].values[0]
            role_actor.append([role, actor])

        output_json[time] = {
                            'scene': scene, 
                            'restaurant': restaurant, 
                            'role_actor': [{
                                            'role': x[0],
                                            'actor': x[1]
                                            } for x in role_actor
                                    ]
                            }
    return output_json
