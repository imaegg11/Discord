class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

import time

class Log:
    def __init__(self, log_file):
        self.log_file = log_file
        self.cc=bcolors()
        self.log_file_handle = open(self.log_file, 'a', encoding='utf-8')
        self.time=lambda:time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.open_new_session()
        
    def open_new_session(self):
        self.log_file_handle.write("NEW SESSION STARTED ["+self.time()+"]\n")
    def info(self, message):
        self.log_file_handle.write("INFO ["+self.time()+"] "+message + '\n')
        # print(self.cc.OKGREEN + "INFO ["+self.time()+"] "+message + self.cc.ENDC)
        self.log_file_handle.flush()
    def warning(self, message):
        self.log_file_handle.write("WARNING ["+self.time()+"] "+message + '\n')
        # print(self.cc.WARNING + "WARNING ["+self.time()+"] "+message + self.cc.ENDC)
        self.log_file_handle.flush()
    def error(self, message):
        self.log_file_handle.write("ERROR ["+self.time()+"] "+message + '\n')
        # print(self.cc.FAIL + "ERROR ["+self.time()+"] "+message + self.cc.ENDC)
        self.log_file_handle.flush()
    def panic(self, message):
        self.log_file_handle.write("PANIC ["+self.time()+"] "+message + '\n')
        # print(self.cc.FAIL + "PANIC ["+self.time()+"] "+message + self.cc.ENDC)
        self.log_file_handle.flush()
        self.close()
        exit(1)
    def debug(self, message):
        self.log_file_handle.write("DEBUG ["+self.time()+"] "+message + '\n')
        # print(self.cc.OKCYAN + "DEBUG ["+self.time()+"] "+message + self.cc.ENDC)
        self.log_file_handle.flush()
    def clear(self):
        self.log_file_handle.truncate(0)
        self.log_file_handle.seek(0)
        self.log_file_handle.write('\n')
        self.log_file_handle.flush()
    def close(self):
        self.log_file_handle.write('\n')
        self.log_file_handle.close()