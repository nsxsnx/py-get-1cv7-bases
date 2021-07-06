from get_bases_sql_inc import sqldb

#############################################################################
# Скрипт скачивает и распаковывает архивы с dump'ами sql-баз с ftp-сервера, 
# после чего выполняет восстановление базы на указанном sql-сервере. 
# 
# Использовать с Python 3.3+.
# Зависимости:
#    - sqlcmd.exe, входит в поставку MS SQL Server и в SqlCmdLnUtils.msi
#############################################################################

#############################################################################
# Пример описания архива бэкапов участка (экземпляр класса):
# example = sqldb(
#   ftp = 'ftp_login:ftp_pass@server.com',   # параметры ftp-сервера
#   arc_name = 'example_file_%y%m%d.7z',     # файл для скачивания,
#                                            # шаблоны даты в формате strftime()
#   day = 0,                                 # 0: сегодняшний архив, -1: вчерашний и т.д.
#   dump_mask = 'example_db_*.full.bak',     # маска имени файла дампа базы в архиве
#   dbname = 'example_db',                   # имя базы, в которую будет восстановлен дамп
#   dbmove =                                 # логические имена файлов базы и пути, куда они
#      {                                     # будут восстановлены, используя запрос
#      'example_data':r'c:\db\path\file.mdf',# RESTORE ... WITH MOVE
#      'example_log':r'c:\db\path\file.ldf'
#      },
#   sqlcmd_param = '-S examplehost,1433',    # параметры sqlcmd.exe: сервер, порт, логин, пасс
#   base_dir = temp_dir                      # директория для временных файлов
#   )
#
# Работа с архивом (методы класса):
#    example.get()                     # скачать архив с ftp, распаковать в base_dir
#    example.restore()                 # восстановить базу из дампа
#############################################################################

options = {
   'temp_dir': r'N:\Public\1c_bases\region\temp',# пустая директория для временных файлов,
                                                 # должна быть доступна для чтения пользователю, 
                                                 # из под которого запущен sql-сервер, а так же 
                                                 # для записи пользователю, из под которого запущен
                                                 # скрипт

   'sqlcmd_path': r'"C:\Program Files (x86)\Microsoft SQL Server\100\Tools\Binn\sqlcmd.exe"',  # путь к sqlcmd.exe
   'sql_user': 'admin1c',  # владелец sql-базы
}

zelenoborsk_tsz = sqldb(
   ftp = 'user01:password01@hostname',
   arc_name = 'tsz_db_%y%m%d.7z',
   day = -1,
   dump_mask = 'tsz_*.full.bak',
   dbname = 'tsz',
   dbmove = {'tsz':r'c:\db\tsz_data.mdf', 'tsz_log':r'c:\db\tsz_log.ldf'},
   sqlcmd_param = '-S sql01.domain.com,1433',
   options = options
   )

zelenoborsk_energosbit = sqldb(
   ftp = 'user02:password02@hostname',
   arc_name = 'energosbit_db_%y%m%d.7z',
   day = -1,
   dump_mask = 'energosbit_*.full.bak',
   dbname = 'energosbit',
   dbmove = {'energosbit':r'c:\db\energosbit_data.mdf', 'energosbit_log':r'c:\db\energosbit_log.ldf'},
   sqlcmd_param = '-S sql01.domain.com,1433',
   options = options
   )

zelenoborsk_ukgks = sqldb(
   ftp = 'user03:password03@hostname',
   arc_name = 'ukgks_db_%y%m%d.7z',
   day = -1,
   dump_mask = 'ukgks_*.full.bak',
   dbname = 'ukgks',
   dbmove = {'ukgks':r'c:\db\ukgks_data.mdf', 'ukgks_log':r'c:\db\ukgks_log.ldf'},
   sqlcmd_param = '-S sql01.domain.com,1433',
   options = options
   )

#############################################################################
# точка входа
#############################################################################

zelenoborsk_tsz.get()
zelenoborsk_tsz.restore()

zelenoborsk_energosbit.get()
zelenoborsk_energosbit.restore()

zelenoborsk_ukgks.get()
zelenoborsk_ukgks.restore()
