# -*- coding: utf-8 -*-

import os
import requests
import zipfile
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.font
import threading
import webbrowser
from tkinter import *
from tkinter import filedialog
from datetime import datetime

abs_path = os.path.dirname(os.path.abspath(__file__))  # 절대 경로
adb_folder = os.path.dirname(os.path.abspath(__file__)) + "/platform-tools"  # 필수 요소 절대 경로

log = open(f'{abs_path}/log.txt', 'a')  # 릴리즈 버전에 포함 시키지 않음


# Form ================================================================================================================
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


def ProgressUpdate(percent):
    global progress_value
    global progress_bar
    progress_value.set(percent)
    progress_bar.update()


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
    read_list = open(f"{abs_path}/readed_list.txt", 'w')  # list 변환 후 공백 처리 되는 오류 보완

    if ADBFileChecker("TF") + ADBAuthChecker("TF") == 0:
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
        MessageBox("불러오기 실패", "디바이스 내 설치된 앱 정보를 불러오지 못했습니다.\n필수 요소 및 디바이스 연결 상태를 확인해 주세요.", "error")


def ADBRun():
    global log  # 로그 열기 (지역 변수화)로 인한 글로벌 처리
    i = 0

    if not os.path.isfile(abs_path + "/remove_list.txt"):
        rm_list = open("remove_list.txt", 'w')
        rm_list.close()
    warning_msg = MessageBox("작업 경고", "시스템 앱을 삭제할 경우, 치명적인 문제가 발생할 수 있습니다.\n계속하시겠습니까?", "askyesno")

    if warning_msg == 1:
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
            ProgressUpdate(int(i / remove_list_len * 100))

        else:
            MessageLog(f"[정보] 작업이 완료되었습니다.\n")
            MessageBox("작업 완료", "작업이 완료되었습니다.\n자세한 내용은 로그를 참고해 주세요.")
            ProgressUpdate(0)

        os.system('taskkill /f /im adb.exe')  # adb server-process 충돌 방지
        remove_list.close()
        log.close()
        os.chdir(abs_path)
        return os.system('log.txt')


# Preset ==============================================================================================================
def PresetSave():
    new_remove_list = filedialog.asksaveasfilename(title="프리셋 내보내기", filetypes=[("텍스트 파일", ".txt")],
                                                   initialfile=f"Preset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    if new_remove_list != '':
        remove_list = open(f"{abs_path}/remove_list.txt", 'r')
        new_remove_list = open(new_remove_list, 'w')

        for remove_app in remove_list:
            new_remove_list.write(f"{remove_app}")
        remove_list.close()
        new_remove_list.close()

        MessageLog("[정보] 프리셋이 저장되었습니다.\n")
        return MessageBox("내보내기 완료", "프리셋이 저장되었습니다.")


def PresetRead():
    new_remove_list = filedialog.askopenfilename(title="프리셋 가져오기", filetypes=[("텍스트 파일", ".txt")],
                                                 initialdir=abs_path)
    if new_remove_list != '':
        warning_msg = MessageBox("가져오기 경고", "기존 제거 목록에 선택한 프리셋으로 덮어씁니다.\n계속하시겠습니까?", "askyesno")

        if warning_msg == 1:
            remove_list = open(f"{abs_path}/remove_list.txt", 'w')
            new_remove_list = open(new_remove_list, 'r')

            for remove_app in new_remove_list:
                remove_list.write(f"{remove_app}")
            remove_list.close()
            new_remove_list.close()

            MessageLog("[정보] 기존 제거 목록에서 새로운 프리셋으로 변경되었습니다.\n")
            return MessageBox("가져오기 완료", "기존 제거 목록에서 새로운 프리셋으로 변경되었습니다.")


# Menu - Function =====================================================================================================
def OpenRemovelist():
    return os.system(f"{abs_path}/remove_list.txt")


def OpenLog():
    global log  # 로그 열기 (지역 변수화)로 인한 글로벌 처리
    log.close()
    os.system(f"{abs_path}/log.txt")
    log = open(f"{abs_path}/log.txt", 'a')


def OpenURL():
    return webbrowser.open("https://github.com/HanSatCode/rmAppAuto")


# Thread ==============================================================================================================
def OpenRemovelistThread():
    th = threading.Thread(target=OpenRemovelist)
    # th.setDaemon(True)
    th.start()


def OpenLogThread():
    th = threading.Thread(target=OpenLog)
    # th.setDaemon(True)
    th.start()


def ADBListReaderThread():
    th = threading.Thread(target=ADBListReader)
    # th.setDaemon(True)
    th.start()


# GUI - Core ==========================================================================================================
window = tkinter.Tk()
window_x = 450
window_y = 325

window.title("rmAppAuto")
window.geometry(f"{window_x}x{window_y}+{int((1920 - window_x) / 2)}+{int((1080 - window_y) / 2)}")
window.resizable(False, False)
window.wm_iconphoto(False, PhotoImage(file="icon.png"))
window.configure(bg="#ffffff")

# GUI - Font ===
font7 = tkinter.font.Font(family="나눔고딕OTF", size=7)
font12 = tkinter.font.Font(family="나눔고딕OTF", size=12)
font12Bold = tkinter.font.Font(family="나눔고딕OTF", size=12, weight="bold")

# GUI - Display ======================================================================================================
progress_value = DoubleVar()

label_list = tkinter.LabelFrame(window, text=" 리스트 ", bd=1, relief="solid", bg="#ffffff", fg="#313131", font=font12Bold)
button_remove = tkinter.Button(label_list, text="제거 목록 목록 확인", overrelief="solid", width=18, height=2,
                               command=OpenRemovelistThread, bd=0, bg="#ffffff", fg="#313131",
                               activebackground="#294dff",
                               activeforeground="#ffffff", font=font12)
button_device = tkinter.Button(label_list, text="디바이스 설치 목록 확인", overrelief="solid", width=18, height=2,
                               command=ADBListReaderThread, bd=0, bg="#ffffff", fg="#313131",
                               activebackground="#294dff",
                               activeforeground="#ffffff", font=font12)

label_preset = tkinter.LabelFrame(window, text=" 프리셋 ", bd=1, relief="solid", bg="#ffffff", fg="#313131",
                                  font=font12Bold)
button_save = tkinter.Button(label_preset, text="가져오기", overrelief="solid", width=7, height=1, command=PresetRead,
                             bd=0, bg="#ffffff", fg="#313131", activebackground="#294dff", activeforeground="#ffffff",
                             font=font12)
button_read = tkinter.Button(label_preset, text="내보내기", relief="solid", overrelief="solid", width=7, height=1,
                             command=PresetSave, bd=0, bg="#ffffff", fg="#313131", activebackground="#294dff",
                             activeforeground="#ffffff", font=font12)

label_progress = tkinter.LabelFrame(window, text=" 작업 진행도 ", bd=1, relief="solid", bg="#ffffff", fg="#313131",
                                    font=font12Bold)
progress_bar = tkinter.ttk.Progressbar(label_progress, maximum=100, length=window_x, variable=progress_value)

label_debug = tkinter.LabelFrame(window, text=" 디버그 ", bd=1, relief="solid", bg="#ffffff", fg="#313131",
                                 font=font12Bold)
button_debug = tkinter.Button(label_debug, text="재설치", overrelief="solid", width=8, height=1,
                              command=ADBFileDownloader,
                              bd=0, bg="#ffffff", fg="#313131", activebackground="#294dff", activeforeground="#ffffff",
                              font=font12)
button_log = tkinter.Button(label_debug, text=" 로그 ", overrelief="solid", width=8, height=1, command=OpenLogThread,
                            bd=0,
                            bg="#ffffff", fg="#313131", activebackground="#294dff", activeforeground="#ffffff",
                            font=font12)

button_start = tkinter.Button(window, text="시작", overrelief="solid", width=10, height=2, command=ADBRun, bd=0,
                              bg="#ffffff", fg="#313131", activebackground="#294dff", activeforeground="#ffffff",
                              font=font12Bold)

label_url = tkinter.Button(window, text="https://github.com/HanSatCode/rmAppAuto", width=50, command=OpenURL,
                           anchor="e", bd=0, bg="#ffffff", fg="#313131", activebackground="#ffffff",
                           activeforeground="#294dff", font=font7)

# GUI - Layout ======================================================================================================
label_url.pack(side="bottom", anchor='e', padx=5, pady=5)
button_start.pack(side="bottom", anchor='s', pady=10)

label_progress.pack(side="bottom", anchor='n', padx=10)
progress_bar.pack(side="top", anchor="center", fill='x', padx=10, pady=10)

label_list.pack(side="left", anchor="nw", padx=10, pady=10, fill='y')
button_remove.pack(side="top", anchor='n', padx=10, pady=10)
button_device.pack(side="bottom", anchor='s', padx=10, pady=10)

label_preset.pack(side="top", anchor='n', padx=10, pady=10, fill='x')
button_save.pack(side="left", anchor='w', padx=10, pady=10)
button_read.pack(side="right", anchor='e', padx=10, pady=10)

label_debug.pack(side="right", anchor='s', padx=10, pady=10, fill='x')
button_debug.pack(side="left", anchor='s', padx=10, pady=10)
button_log.pack(side="right", anchor='s', padx=10, pady=10)

# Start ====================================================================================================
window.mainloop()
