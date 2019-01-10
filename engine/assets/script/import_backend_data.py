import pandas as pd
import os


def main(filename):
    excel = pd.read_excel(filename, sheet_name=['Actors', 'Characters', 'Restaurants', 'Scenes'])
    actor_df = excel['Actors']
    character_df = excel['Characters']
    restaurant_df = excel['Restaurants']
    scene_df = excel['Scenes']
    return actor_df, character_df, restaurant_df, scene_df


if __name__ == '__main__':
    os.chdir('..')
    print(os.getcwd())
    files = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    ACT, CHR, RES, SCE = main(files)
    print(ACT)
