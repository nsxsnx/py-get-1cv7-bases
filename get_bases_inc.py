from datetime import date, timedelta
from ftplib import FTP
from os import path, makedirs, system, remove, rmdir, walk, chmod, stat, getcwd
from stat import S_IWRITE
from subprocess import call, TimeoutExpired
from threading import Thread
from glob import glob
from time import sleep
from winreg import OpenKey, SetValueEx, CloseKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ
from random import randint

class region:
   def __init__(self, pftp, pfiles, exc_bases, day, base_dir):
      self.init_basedir(base_dir)
      self.init_files(pfiles, day)
      self.init_ftp(pftp)
      self.init_exclude(exc_bases)

   def init_exclude(self, exc_bases):
      self.exclude_bases = []
      for exc in exc_bases: 
         if exc[-1] != '\\': exc += '\\'
         self.exclude_bases += [exc]

   def init_basedir(self, base_dir):
      if base_dir[-1:] != '/': base_dir += '/'
      if not path.exists(base_dir): makedirs(base_dir)
      self.base_dir = base_dir

   def init_files(self, pfiles, day):
      self.dt = date.today() + timedelta(day)  
      self.basenames = [self.dt.strftime(file) for file in pfiles]
      self.files = [self.base_dir + file for file in self.basenames]
      
   def init_ftp(self, pftp):
      self.ftp_user = pftp[ : pftp.find(':')]
      self.ftp_pass = pftp[pftp.find(':') + 1 : pftp.find('@')]
      self.ftp_server = pftp[pftp.find('@') + 1 : ]

   def get(self):
      ftp = FTP(self.ftp_server, self.ftp_user, self.ftp_pass)
      for file in self.basenames:
         print('Downloading file ' + file + '...')
         ftp.retrbinary('RETR ' + file, open(self.base_dir + file, 'wb').write) 
      ftp.quit() 

   def unpack(self):
      for file in self.files:
         print('Unpacking file ' + file + '...')
         ext = path.splitext(file)[1]
         if   ext == '.rar': system('Rar.exe x -df ' + file + ' ' + self.base_dir)
         elif ext == '.7z':  system('7z.exe x ' + file + ' -y -o' + self.base_dir)
         else: print('Unsupported file type', ext)
      self.rm_arc()

   def rm_arc(self):
      for file in self.files:
         print('Removing file ' + file + '...')
         if path.exists(file) and path.isfile(file): remove(file)

   def clean(self):
      self._clean_path(self.base_dir)

   def _clean_path(self, p):
      if not p: return 
      if p[1:2] == '/': return 
      if p[1:2] == '.': return 
      print('Cleaning directory ' + p + '...')
      for root, dirs, files in walk(p, topdown=False):
         for name in files:
            fname = path.join(root, name)
            set_writable(fname)
            remove(fname)
         for name in dirs:
            fname = path.join(root, name);
            set_writable(fname)
            rmdir(fname)

   def _rm_path(self, p):
      if not p: return 
      if p[1:2] == '/': return 
      if p[1:2] == '.': return
      self._clean_path(p)
      print('Dropping directory ' + p + '...')
      rmdir(p)

   def get_ftp_size(self):
      self.file_ftp_size = []
      ftp = FTP(self.ftp_server, self.ftp_user, self.ftp_pass)
      ftp.sendcmd('TYPE I')
      for file in self.basenames:
         print('Getting file size from ftp: ' + file + '...')
         self.file_ftp_size += [ftp.size(file)] 
      ftp.quit() 

   def get_bases_list(self):
      if hasattr(self, 'bases_list'): return 
      self.bases_list = []
      print('Searching for bases in ' + self.base_dir + '...')
      for root, dirs, files in walk(self.base_dir, topdown=False):
         for name in dirs:
            if name == 'usrdef':
               bs = path.join(root, name)[:-6].replace('/', '\\')
               bexc = False
               for exc in self.exclude_bases:
                  if bs.endswith(exc):
                     bexc = True
                     self._rm_path(bs)
               if not bexc:
                  print('   ', bs)
                  self.bases_list += [bs]

   def run_1c(self, onec_parm):
      print('Starting bases...')
      cnt = 0
      self.get_bases_list()  
      for base in self.bases_list:
         cnt += 1 
         cmd = onec_parm['exe_path'] + ' enterprise /M'
         cmd += ' /D' + path.join(getcwd(), base).replace('/', '\\')
         cmd += ' /N' + onec_parm['user'] + ' /P' + onec_parm['pass']
         print('Starting thread', cnt, 'with command line:')
         print(cmd)
         Thread(target = run_timed_thread, args = (cmd, onec_parm['max_exec_time'])).start()

   def remove_lock_files(self):
      self.get_bases_list()  
      for base in self.bases_list:
         users_dbf_path = path.join(getcwd(), base, '1SUSERS.DBF')
         if path.exists(users_dbf_path) and path.isfile(users_dbf_path):
            set_writable(users_dbf_path)
            remove(users_dbf_path) 

   def rebuild_index(self, onec_parm):
      self.drop_1c_index()
      self.reg_add_bases()
      self.run_1c(onec_parm)
      sleep(onec_parm['max_exec_time'] + 10) # wait until index has been rebuilt
      self.remove_lock_files()

   def drop_1c_index(self):
      self.get_bases_list()  
      for base in self.bases_list:
         print('Dropping index of base: ', base)
         for file in (glob(path.join(base, '*.cdx'))):
            remove(file)

   def reg_add_bases(self):
      self.get_bases_list()  
      for base_path in self.bases_list:
         base_path = path.join(getcwd(), base_path).replace('/', '\\')
         if base_path[-1] == '\\': base_path = base_path[:-1]
         key = OpenKey(HKEY_CURRENT_USER, 'Software\\1C\\1CV7\\7.7\\Titles', 0, KEY_ALL_ACCESS)
         base_name = 'reindex_' + str(randint(10000, 99999)) + '_' + path.basename(base_path)
         print('Adding database \'' + base_path + '\' to registry as \'' + base_name + '\'')
         SetValueEx(key, base_path, 0, REG_SZ, base_name)
         CloseKey(key)

def run_timed_thread(cmd, max_exec_time):
   try:
      call(cmd, timeout = max_exec_time)
   except TimeoutExpired:
      pass

def set_writable(path):
   mode = stat(path)[0]
   if (not mode & S_IWRITE):
      chmod(path, S_IWRITE)
