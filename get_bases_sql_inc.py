from datetime import date, timedelta
from ftplib import FTP
from os import path, remove, chmod, stat 
from subprocess import call
from stat import S_IWRITE
from subprocess import call, TimeoutExpired
from threading import Thread
from glob import glob
from re import search
from tempfile import NamedTemporaryFile

class sqldb:
   def __init__(self, ftp, arc_name, day, dump_mask, dbname, dbmove, sqlcmd_param, options):
      self.dt = date.today() + timedelta(day)  
      self.basename = self.dt.strftime(arc_name)
      self.ftp = ftp
      self.dump = dump_mask
      self.dbname = dbname
      self.move = dbmove
      self.sqlcmd = options['sqlcmd_path'] + ' ' + sqlcmd_param 
      self.base_dir = options['temp_dir']
      self.db_owner = options['sql_user']

   def get(self):
      file = self.basename
      tmpfl = NamedTemporaryFile(delete=False)
      print('Downloading file ' + file + ' to ' + tmpfl.name + '...')
      r = search('(.*):(.*)@(.*)', self.ftp)
      ftp = FTP(r.group(3), r.group(1), r.group(2))
      ftp.retrbinary('RETR ' + file, tmpfl.write) 
      fname = tmpfl.name
      tmpfl.close()

      print('Unpacking file ' + tmpfl.name + '...')
      ext = path.splitext(file)[1]
      if ext == '.rar': call('Rar.exe x -df ' + fname + ' ' + self.base_dir)
      if ext == '.7z':  call('7z.exe x ' + fname + ' -y -o' + self.base_dir)
      else: print('Unsupported file type', ext)
      set_writable(fname)
      remove(fname)
      ftp.quit() 

   def restore(self):
      mask = self.dump
      file_lst = glob(path.join(self.base_dir, mask))
      if len(file_lst) != 1: 
         print('Wrong \'dump_mask\' given:', mask)
         return
      file = file_lst[0]
      sqlstr = '\"RESTORE DATABASE ' + self.dbname + ' FROM DISK=\'' + file + '\''
      sqlstr = self.sqlcmd + ' -Q ' + sqlstr + ' WITH REPLACE, '
      for key in self.move:
         sqlstr += ' MOVE \'' + key + '\' to \'' + self.move[key] + '\',' 
      sqlstr = sqlstr[:-1] + ';'
      sqlstr += 'use ' + self.dbname + '; exec sp_changedbowner \'' + self.db_owner + '\'' + '\"'
      print(sqlstr)
      call(sqlstr)
      set_writable(file)
      remove(file)

def set_writable(path):
   mode = stat(path)[0]
   if (not mode & S_IWRITE):
      chmod(path, S_IWRITE)
