# -*- coding: utf-8 -*-

import os
import requests
import zipfile
import tkinter
import tkinter.ttk
import tkinter.messagebox
import threading
from tkinter import *
from datetime import datetime

abs_path = os.path.dirname(os.path.abspath(__file__))  # 절대 경로
adb_folder = os.path.dirname(os.path.abspath(__file__)) + "/platform-tools"  # 필수 요소 절대 경로

log = open(f'{abs_path}/log.txt', 'a')  # 릴리즈 버전에 포함 시키지 않음


# Alert Message =======================================================================================================
def MessageLog(description):
    now = datetime.now()
    return log.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} : {description}")


def MessageBox(title, description, type="info"):
    if type == "warning":
        return tkinter.messagebox.showwarning(title, description)
    elif type == "error":
        return tkinter.messagebox.showerror(title, description)
    elif type == "askyesno":
        return tkinter.messagebox.askyesno(title, description)
    else:
        return tkinter.messagebox.showinfo(title, description)


# Function - Core =====================================================================================================
def ADBFileDownloader():
    adb_download = requests.get("https://dl.google.com/android/repository/platform-tools-latest-windows.zip?hl=ko",
                                allow_redirects=True)
    open("adb.zip", "wb").write(adb_download.content)
    with zipfile.ZipFile("adb.zip", 'r') as adb_zip:
        adb_zip.extractall(abs_path)
    os.remove("adb.zip")
    MessageLog("[정보] 필수 요소를 정상적으로 재설치하였습니다.\n")
    return MessageBox("재설치 완료", "필수 요소를 정상적으로 재설치하였습니다.")


def ADBFileChecker(mode="message"):  # Mode Message -> Alert / Mode TF -> ADBRun
    if os.path.exists(adb_folder):
        adb_file = ("adb.exe", "AdbWinApi.dll", "AdbWinUsbApi.dll", "dmtracedump.exe", "etc1tool.exe", "fastboot.exe",
                    "hprof-conv.exe", "libwinpthread-1.dll", "make_f2fs.exe", "make_f2fs_casefold.exe", "mke2fs.conf",
                    "mke2fs.exe", "source.properties", "sqlite3.exe")
        for file_name in adb_file:
            if not os.path.isfile(adb_folder + f'/{file_name}'):
                MessageLog("[오류] 필수 요소 중 일부 파일이 누락되어 있습니다.\n")
                if mode == "message":
                    return MessageBox("파일 누락", "필수 요소 중 일부 파일이 누락되어 있습니다.", "warning")
                return 1
        else:
            MessageLog("[정보] 필수 요소의 모든 파일이 정상입니다.\n")
            if mode == "message":
                return MessageBox("파일 정상", "필수 요소의 모든 파일이 정상입니다.")
            return 0
    else:
        MessageLog("[오류] 필수 요소가 실행 환경 내에서 발견되지 않았습니다.\n")
        if mode == "message":
            return MessageBox("폴더 없음", "필수 요소가 실행 환경 내에서 발견되지 않았습니다.", "error")
        return 1


def ADBAuthChecker(mode="message"):  # mode 1 -> ADBRun
    os.system("chcp 65001")  # PyCharm Terminal UTF-8 깨짐 방지
    os.chdir(adb_folder)
    auth_checker = os.popen("adb devices").read()
    os.system("taskkill /f /im adb.exe")  # adb server-process 충돌 방지
    os.chdir(abs_path)
    if auth_checker == "List of devices attached\n\n":
        MessageLog("[오류] 연결된 디바이스가 발견되지 않았습니다.\n")
        if mode == "message":
            return MessageBox("디바이스가 발견되지 않음", "연결된 디바이스가 발견되지 않았습니다.\n디바이스가 정상적으로 연결되어 있는지 확인해 주세요.", "error")
        return 1
    elif "unauthorized" in auth_checker:
        MessageLog("[오류] 연결된 디바이스가 USB 디버깅이 허용되어 있지 않습니다.\n")
        if mode == "message":
            return MessageBox("디바이스가 허용되지 않음", "연결된 디바이스가 디버깅이 허용되지 않았습니다.\n디바이스에서 USB 디버깅을 허용하였는지 확인해 주세요.", "error")
        return 1
    else:
        MessageLog("[정보] 연결된 디바이스가 정상적으로 USB 디버깅이 허용되어 있습니다.\n")
        if mode == "message":
            return MessageBox("디바이스가 허용됨", "연결된 디바이스가 정상적으로 USB 디버깅이 허용되어 있습니다.")
        return 0


def ADBListChecker(mode="message"):  # mode 1 -> ADBRun
    remove_list = open(f"{abs_path}/remove_list.txt", 'r')
    if not list(remove_list):
        MessageLog(f"[오류] 'remove_list.txt'에 내용이 들어있지 않습니다.\n")
        remove_list.close()
        if mode == "message":
            return MessageBox("내용 없음", "삭제 목록에 내용이 들어있지 않습니다.\n프로그램을 종료합니다.", "error")
        return 1
    else:
        remove_list.close()
        return 0


def ADBListReader():
    read_list = open(f"{abs_path}/readed_list.txt", 'w')  # 62번 list 변환 후 공백 처리 되는 오류 보완

    if ADBAuthChecker("TF") == 0:
        os.system("chcp 65001")  # PyCharm Terminal UTF-8 깨짐 방지
        os.chdir(adb_folder)
        os.system("adb devices")

        read_list.write(os.popen(f"adb shell pm list packages").read())
        os.system("taskkill /f /im adb.exe")  # adb server-process 충돌 방지

        MessageLog("[정보] 디바이스 내 설치된 앱 정보를 불러왔습니다.\n")
        MessageBox("불러오기 완료", "디바이스 내 설치된 앱 정보를 불러왔습니다.")

        read_list.close()
        return os.system(f"{abs_path}/readed_list.txt")
    else:
        MessageLog("[오류] 디바이스 내 설치된 앱 정보를 불러오지 못했습니다.\n")
        MessageBox("불러오기 실패", "디바이스 내 설치된 앱 정보를 불러오지 못했습니다.", "error")


def ADBRun():
    global log  # 로그 열기 (지역 변수화)로 인한 글로벌 처리
    global progress_value
    global progress_bar

    i = 0

    if not os.path.isfile(abs_path + "/remove_list.txt"):
        rm_list = open("remove_list.txt", 'w')
        rm_list.close()
    warning_msg = MessageBox("작업 경고", "시스템 앱을 삭제할 경우, 치명적인 문제가 발생할 수 있습니다.\n계속하시겠습니까?", "askyesno")

    if warning_msg == 0:
        MessageLog("[정보] 사용자가 작업을 중단하였습니다.\n")
        return MessageBox("작업 중단", "작업이 중단되었습니다.")

    if ADBFileChecker("TF") + ADBAuthChecker("TF") + ADBListChecker("TF") > 0:
        return MessageBox("작업 오류", "작업 초기화 작업 중 오류로 인해 작업을 중단했습니다.\n자세한 내용은 로그를 참고해 주세요.", "error")

    os.system("chcp 65001")  # PyCharm Terminal UTF-8 깨짐 방지
    os.chdir(adb_folder)
    os.system("adb devices")

    remove_list = open(f"{abs_path}/remove_list.txt", 'r')
    remove_list_len = len(remove_list.readlines())
    remove_list.close()

    remove_list = open(f"{abs_path}/remove_list.txt", 'r')  # list 변환 후 공백 처리 되는 오류 보완 + 마지막 줄 리드 방지

    for package_name in remove_list:
        i += 1
        package_name = package_name.strip('\n')
        package_name = package_name.replace("package:", '')
        remove_result = os.popen(f"adb shell pm uninstall --user 0 {package_name}").read()
        if "Success" in remove_result:
            MessageLog(f"[성공] {package_name}(이)가 디바이스에서 제거되었습니다.\n")
        else:
            MessageLog(f"[실패] {package_name}(이)가 디바이스에서 제거되지 않았습니다. - {remove_result}")
        progress_value.set(int(i / remove_list_len * 100))
        progress_bar.update()

    else:
        MessageLog(f"[정보] 작업이 완료되었습니다.\n")
        MessageBox("작업 완료", "작업이 완료되었습니다.\n자세한 내용은 로그를 참고해 주세요.")
        progress_value.set(0)
        progress_bar.update()

    os.system('taskkill /f /im adb.exe')  # adb server-process 충돌 방지
    remove_list.close()
    log.close()
    os.chdir(abs_path)
    return os.system('log.txt')


# Thread ==============================================================================================================
def ADBRunThread():  # Menu 접근 가능
    th = threading.Thread(target=ADBRun)
    #th.setDaemon(True)
    th.start()


# Preset ==============================================================================================================
def PresetSave():
    return 0


def PresetRead():
    return 0


def PresetT800():
    warning_msg = MessageBox("덮어쓰기 경고", "기존 제거 목록을 덮어씁니다. 계속하시겠습니까?", "askyesno")

    if warning_msg == 1:
        remove_list = open(f"{abs_path}/remove_list.txt", 'w')
        new_remove_list = open(f"{abs_path}/preset/Marshmello.txt", 'r')

        for remove_app in new_remove_list:
            remove_list.write(f"{remove_app}")
        remove_list.close()
        new_remove_list.close()

        MessageLog("[정보] 기존 제거 목록에서 새로운 프리셋으로 변경되었습니다.\n")
        return MessageBox("덮어쓰기 완료", "기존 프리셋에서 새로운 프리셋으로 변경되었습니다.")


# Menu - Function =====================================================================================================
def OPENRemovelist():
    return os.system('remove_list.txt')


def OPENLog():
    global log  # 로그 열기 (지역 변수화)로 인한 글로벌 처리
    log.close()
    os.system('log.txt')
    log = open(f'{abs_path}/log.txt', 'a')


# GUI - Core ==========================================================================================================
window = tkinter.Tk()
window_x = 450
window_y = 200

window.title("rmAppAuto - GUI Version")
window.geometry(f"{window_x}x{window_y}+{int((1920 - window_x) / 2)}+{int((1080 - window_y) / 2)}")
window.resizable(False, False)
window.wm_iconphoto(False, PhotoImage(file="icon.png"))

# Menu - Core =========================================================================================================
menu = tkinter.Menu(window)

menu_set = tkinter.Menu(menu, tearoff=0)
menu_debug = tkinter.Menu(menu, tearoff=0)
menu_preset = tkinter.Menu(menu, tearoff=0)

menu_set.add_command(label="제거 목록 열기", command=OPENRemovelist)
menu_set.add_command(label="디바이스 설치 목록 확인", command=ADBListReader)
menu_set.add_separator()
menu_set.add_command(label="필수 요소 확인", command=ADBFileChecker)
menu_set.add_command(label="디바이스 연결 확인", command=ADBAuthChecker)
menu_set.add_separator()
menu_set.add_command(label="필수 요소 재설치", command=ADBFileDownloader)
menu_set.add_separator()
menu_set.add_command(label="종료", command=exit)

menu_preset.add_command(label="프리셋 내보내기", command=PresetSave, state="disabled")
menu_preset.add_command(label="프리셋 가져오기", command=PresetRead, state="disabled")
menu_preset.add_separator()
menu_preset.add_command(label="Marshmello 6.0", command=PresetT800)

menu_debug.add_command(label="로그 열기", command=OPENLog)

menu.add_cascade(label="옵션", menu=menu_set)
menu.add_cascade(label="프리셋", menu=menu_preset)
menu.add_cascade(label="디버그", menu=menu_debug)

window.config(menu=menu)

# GUI - Display ====================================================================================================
progress_value = DoubleVar()

label_progress = tkinter.LabelFrame(window, text="작업 진행도")
progress_bar = tkinter.ttk.Progressbar(label_progress, maximum=100, length=window_x, variable=progress_value)

button_start = tkinter.Button(window, text="시작", overrelief="solid", width=10, height=2, command=ADBRun)
button_quit = tkinter.Button(window, text="종료", overrelief="solid", width=10, height=2, command=quit)

label_progress.pack(side="top", padx=10, pady=25)
progress_bar.pack(side="top", fill="x", padx=10, pady=10)

button_start.pack(side="left", anchor="center", padx=75)
button_quit.pack(side="right", anchor="center", padx=75)
# Start ====================================================================================================
window.mainloop()
