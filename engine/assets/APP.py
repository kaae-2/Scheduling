import os
from script import input_data, constraint_optimizer, output_solution
import datetime as dt


if __name__ == '__main__':
    os.chdir('.')
    print(os.getcwd())
    backend_file = 'data/KORSBAEK_EXCELTEMPLATE_v2.xlsx'
    shift_file = 'SHIFT_INPUT.xlsx'
    scene_play_delta = dt.timedelta(minutes=10)
    tour = [dt.time(14, 30), dt.time(15, 30), dt.time(16, 30)]
    time_off = [dt.time(16, 00), dt.time(16, 25)]
    RDY, ACT, CHR, RES, SCE = input_data.main(shift_file, backend_file)
    solution, RDY = constraint_optimizer.main(RDY, scene_play_delta, RES, tour, time_off)
    output_solution.main(solution, RDY, ACT, CHR, RES, SCE, shift_file, tour, time_off)
    print('Success!')
