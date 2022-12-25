import HW_interface as HW
from simple_pid import PID
import time
import machine_vision as MV
import cv2 as cv
import HW_interface as HW

L_vel, R_vel = int(), int()
max_speed = 600


def load_pid_settings(name):

    import json
    file_name = "PID_settings_" + str(name) + ".json"
    loaded = {
        'P': -1,
        'I': -1,
        'D': -1
    }
    try:
        file = open(file_name, 'r', encoding='utf8')
        loaded = json.load(file).copy()
        P = loaded['P']
        I = loaded['I']
        D = loaded['D']
    except FileNotFoundError:
        print("settings are not found, creating defaulf settings file...")
        file = open(file_name, 'w+', encoding='utf8')
        json.dump(loaded, file)
    finally:
        file.close()
    print("settings are loaded:")
    print(json.dumps(loaded, indent=4, sort_keys=True))
    return P, I, D


def save_pid_settings(name, P, I, D):

    import json
    file_name = "PID_settings_" + str(name) + ".json"
    loaded = {
        'P': P,
        'I': I,
        'D': D
    }
    try:
        file = open(file_name, 'w+', encoding='utf8')
        json.dump(loaded, file)
    except FileNotFoundError:
        print("error")
    finally:
        file.close()


def filter(val, filter_arr, filter_window=10):
    filter_arr.append(val)
    if len(filter_arr) > filter_window:
        filter_arr.pop(0)
    if len(filter_arr) > 1:
        return int(sum(filter_arr) / len(filter_arr))
    else:
        return filter_arr[0]



def control():

    cam = cv.VideoCapture(0)

    if (cam.isOpened() == False):
        print("Error opening video file")
        return False

    time_quantum = 0.5
    t_end = 0    
    t_draw = 0
    
    watch_dog = 0
    execution_dog = 10
    error_cntr = 0

    f_arr_angle = []
    f_arr_point = ([], [])

    P, I, D = load_pid_settings('1')
    pid = PID(P, I, D)
    pid.setpoint = 0
    pid.sample_time = time_quantum
    pid.output_limits = (-max_speed, max_speed)

    # HW.send_drives('start')
    while (cam.isOpened()):
        ret, raw = cam.read()
        if ret == True:
            
            #работа с картинкой
            frame_devided, frame_cny = MV.image_processing(raw)

            #определение всех линий (сортированных). Если не определил -> 
            lines = MV.find_lines(frame_cny)
            t_det = time.monotonic() - t_end
            if lines == False:
                #если не определил, может быть попытаться еще раз, 
                #если время определения (t_det) было меньше половины кванта времени - if - continue
                #прибавить значение вочдога
                watch_dog +=1
                #вочдог при переполнении выходит из цикла
                if watch_dog > execution_dog:
                    break
                if t_det < 0.5 * time_quantum:
                    continue
            
            else:
                #Определил линию - сбрасываем вочдога
                watch_dog = 0
                #определение средней линии. Возвращает линию ((,),(,)) - обязательно что-то возвращает
                mean_line = MV.find_mean_direction(lines)
                #Пересчитываем линию в угол и начальную точку
                angle_raw, point_raw = MV.calc_mean_dir(mean_line)

                #загоняем эти значения в фильтр со скользящим окном
                #ширина окна влияет на скорость определения изменения линии, это важно!

                angle = filter(angle_raw, f_arr_angle)
                anglepoint = map(filter, point_raw, f_arr_point)

                #сделать функцию, пересчитывающую управляющий сигнал из обеих точек
                
                #отправляем управляющий сигнал в пид, получаем значения.
                delta = pid(angle)
                left = max_speed
                right = max_speed
                if delta < 0:
                    right = right + int(delta)
                else:
                    left = left - int(delta)

                #дебаг - в консоль

                R_str = f"R {right}"
                L_str = f"L {left}"
                scrn_data = \
                    '\n' * 10 + \
                    f'angle: {angle} \t\t point: {tuple(anglepoint)}\n' + \
                    f'delta: {delta:.3f} \t left: {left} \t right: {right}\n' + \
                    f'detection time: {t_det:.3f} sec \t draw time: {t_draw:.3f} sec\n' + \
                    f'P, I, D: {P, I, D} \t\t\t\t error counter {error_cntr}'
                print(scrn_data)
                #если хватает времени: (t_draw - предыдущий период отрисовки)
                #отрисовываем все на экране, если нет - ждем окончания кванта времени - отправляем в движки
                t_pre_draw = time.monotonic()
                t_remining = time_quantum - (t_pre_draw - t_end)
                if t_draw < t_remining:

                    # N = ((320, 480), (320 + dir[0], 480 + dir[1]))
                    L = ((10, 240), (10, int(left / 4)))
                    R = ((630, 240), (630, int(right / 4)))
                    MV.draw_lines(raw, lines, 255, 0, 255)
                    MV.draw_lines(raw, [L, R], 0, 200, 100)
                    # MV.draw_lines(raw, [N], 0, 0, 255)

                    raw = MV.show_screen_data(raw, scrn_data)
                    cv.imshow('control', raw)
                    cv.imshow('detector', frame_devided)
                    t_draw =time.monotonic() - (t_pre_draw)
                else:
                    t_draw = 0
                
                t_remining = time_quantum - (time.monotonic() - t_end)

                if t_remining < 0:
                    error_cntr += 1
                    print('\n\n\n time ERROR{error_cntr}')
                    sleeping = 0
                time.sleep(sleeping)

                HW.send_drives(L_str)
                HW.send_drives(R_str)
                
                # сохраняем t_end начала итеррации

            t_end = time.monotonic()

            # всякая хуйня с кнопками, тут досчитывается t_draw
            
            key = cv.waitKey(25) & 0xFF
            if key == ord('q'):
                break
            if key == ord('P'):
                P += 1
            if key == ord('p'):
                P -= 1
            if key == ord('I'):
                I += 0.1
            if key == ord('i'):
                I -= 0.1
            if key == ord('D'):
                D += 1
            if key == ord('d'):
                D -= 1
            if key == ord('s'):
                save_pid_settings(P, I, D)
            if key == ord('w'):
                pid = PID(P, I, D)
                pid.setpoint = 0
                pid.sample_time = time_quantum
                pid.output_limits = (-max_speed, max_speed)

    cam.release()
    cv.destroyAllWindows()
    R_str = f"R {0}"
    L_str = f"L {0}"
    HW.send_drives(R_str)
    HW.send_drives(L_str)

control()
