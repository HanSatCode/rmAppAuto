# -*- coding: utf-8 -*-

import os
import requests
import zipfile
import ctypes
from datetime import datetime

abs_path = os.path.dirname(os.path.abspath(__file__))
adb_folder = os.path.dirname(os.path.abspath(__file__)) + '/platform-tools'

log = open(f'{abs_path}/log.txt', 'a')  # NOT include release zip


def MessageLog(description):
    now = datetime.now()
    return log.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} : {description}")


def MessageBox(title, description, style):
    return ctypes.windll.user32.MessageBoxW(None, description, title, style)


def ADBFileChecker():
    if os.path.exists(adb_folder):
        adb_file = ('adb.exe', 'AdbWinApi.dll', 'AdbWinUsbApi.dll', 'dmtracedump.exe', 'etc1tool.exe', 'fastboot.exe',
                    'hprof-conv.exe', 'libwinpthread-1.dll', 'make_f2fs.exe', 'make_f2fs_casefold.exe', 'mke2fs.conf',
                    'mke2fs.exe', 'NOTICE.txt', 'source.properties', 'sqlite3.exe')  # Tuple
        for file_name in adb_file:
            if not os.path.isfile(adb_folder + f'/{file_name}'):
                MessageLog("[경고] 'platform-tools' 폴더의 일부 파일이 누락되어 있습니다.\n")
                MessageBox('파일 누락', "'platform-tools' 폴더의 일부 파일이 누락되어 있습니다.\n새 파일을 자동으로 다운로드 합니다.", 48)
                return ADBFileDownloader()
        else:
            MessageLog("[정보] 'platform-tools' 폴더의 파일이 정상입니다.\n")
            return ADBAuthChecker()
    else:
        MessageLog("[경고] 'platform-tools' 폴더가 실행 환경 내에서 발견되지 않았습니다.\n")
        MessageBox('폴더 없음', "'platform-tools' 폴더가 실행 환경 내에서 발견되지 않았습니다.\n새 파일을 자동으로 다운로드 합니다.", 48)
        return ADBFileDownloader()


def ADBFileDownloader():
    adb_download = requests.get("https://dl.google.com/android/repository/platform-tools-latest-windows.zip?hl=ko",
                                allow_redirects=True)
    open('adb.zip', 'wb').write(adb_download.content)
    with zipfile.ZipFile('adb.zip', 'r') as adb_zip:
        adb_zip.extractall(abs_path)
    MessageLog("[정보] 'platform-tools' 폴더를 정상적으로 다운로드 하였습니다.\n")
    os.remove('adb.zip')
    return ADBAuthChecker()


def ADBAuthChecker():
    os.system('chcp 65001')  # PyCharm Terminal UTF-8 깨짐 방지
    os.chdir(adb_folder)
    auth_checker = os.popen('adb devices').read()
    os.system('taskkill /f /im adb.exe')  # adb server-process 충돌 방지
    os.chdir(abs_path)
    if auth_checker == 'List of devices attached\n\n':
        MessageLog(f"[실패] 연결된 디바이스가 없습니다.\n{'=' * 50}\n")
        return MessageBox('연결된 기기 없음', '연결된 기기가 없습니다.\n디바이스가 정상적으로 연결되어 있는지 확인해 주세요.', 16)
    elif 'unauthorized' in auth_checker:
        MessageLog(f"[실패] 연결된 디바이스가 USB 디버깅이 허용되어 있지 않습니다.\n{'=' * 50}\n")
        return MessageBox('미인증 디바이스', '인증되지 않은 디바이스 입니다.\n연결한 디바이스 화면에서 USB 디버깅을 허용해 주세요.', 16)
    else:
        return ADBRun()


def ADBRun():
    if not os.path.isfile(abs_path + '/remove_list.txt'):
        rm_list = open('remove_list.txt', 'w')
        rm_list.close()
    warning_msg = MessageBox('작업 경고',
                             '선택한 앱이 영구적으로 삭제됩니다.\n시스템 앱을 삭제할 경우, 치명적인 문제가 발생할 수 있습니다.\n[확인]을 눌러 삭제 목록을 확인해 주세요.', 49)
    if warning_msg == 1:
        os.system('remove_list.txt')
    elif warning_msg == 2:
        MessageLog(f"[정보] 사용자가 작업을 중단하였습니다.\n{'=' * 50}\n")
        MessageBox('작업 중단', '작업이 중단되었습니다.', 64)

    os.system('chcp 65001')  # PyCharm Terminal UTF-8 깨짐 방지
    os.chdir(adb_folder)
    os.system('adb devices')
    remove_list = open(f'{abs_path}/remove_list.txt', 'r')
    if not list(remove_list):
        MessageLog(f"[실패] 'remove_list.txt'에 내용이 들어있지 않습니다.\n{'=' * 50}\n")
        MessageBox('내용 없음', '삭제 목록에 내용이 들어있지 않습니다.\n프로그램을 종료합니다.', 16)
    else:
        remove_list = open(f'{abs_path}/remove_list.txt', 'r')  # 62번 list 변환 후 공백 처리 되는 오류 보완
        for package_name in remove_list:
            package_name = package_name.strip('\n')
            remove_result = os.popen(f'adb shell pm uninstall --user 0 {package_name}').read()
            if 'Success' in remove_result:
                MessageLog(f"[성공] {package_name}(이)가 디바이스에서 제거되었습니다.\n")
            else:
                MessageLog(f"[실패] {package_name}(이)가 디바이스에서 제거되지 않았습니다. - {remove_result}")
        else:
            MessageLog(f"[정보] 프로그램이 종료되었습니다.\n{'=' * 50}\n")
            MessageBox('작업 완료', "작업이 완료되었습니다.\n상세한 내역은 'log.txt'(을)를 참고해 주세요.", 64)
    log.close()
    remove_list.close()
    os.system('taskkill /f /im adb.exe')  # adb server-process 충돌 방지
    os.chdir(abs_path)
    return os.system('log.txt')


if __name__ == '__main__':
    ADBFileChecker()