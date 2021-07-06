from get_bases_inc import region

#############################################################################
# Скрипт скачивает и распаковывает архивы с базами 1С 7 с ftp-сервера, 
# после чего выполняет переиндексацию всех баз, обнаруженных в архивах. 
# 
# Использовать с Python 3.3, только на ОС Windows. 
#############################################################################

#############################################################################
# Пример описания архива бэкапов участка (экземпляр класса):
# example = region(
#    'ftp_login:ftp_pass@server.com',  # параметры ftp-сервера
#    [                                 # список файлов для скачивания,
#       'file1_%Y%m%d.rar',            # шаблоны даты в формате strftime()
#       'file2_%d%m%y.rar',
#       'file3_example.rar'
#    ],
#    [                                 # список баз в архиве, которые
#       'Base',                        # следует исключить из обработки
#       'base_dir\\path\\base',
#    ],
#    day = 0,                          # 0: сегодняшний архив, -1: вчерашний и т.д.
#    base_dir = 'example_dir/'         # локальная рабочая директория, будет ОЧИЩЕНА.
#                                      # т.к. содержимое base_dir удаляется,
#                                      # путь не должен начинаться с точки
#    )
#
# Работа с архивом (методы класса):
#    example.clean()                   # удалить содержимое base_dir
#    example.drop_1c_index()           # удалить индексы dbf-баз
#    example.get()                     # скачать архив с ftp в base_dir
#    example.get_ftp_size()            # получить размеры архивов с ftp-сервера
#    example.rebuild_index(onecparm)   # перестроить индексы dbf-баз
#    example.unpack()                  # распаковать скачанный архив в base_dir
#    example.reg_add_bases()           # прописать базы в реестр
#############################################################################

umba = region(
   'user01:password01@hostname01',
   [
      'varzuga_base_varzuga-%Y_%m_%d.rar',
      'umba_Base_MUP_UMBA-%Y_%m_%d.rar',
      'umba_base-%Y_%m_%d.rar'
   ],
   [ ],
   day = -1,
   base_dir = 'umba'
   )

zelenoborsk = region(
   'user02:password02@hostname02',
   ['1c_zelenoborsk_energo_%y%m%d.rar'],
   [
      'zelenoborsk\\1c_bases\\electro\\TSZ',
      'zelenoborsk\\1c_bases\\electro\\TSZ_sql',
      'zelenoborsk\\1c_bases\\electro\\UKGKS',
   ],
   day = -1,
   base_dir = 'zelenoborsk'
   )

#############################################################################
# Параметры 1С, необходимы для перестроения индексов
#############################################################################

onecparm = {
   'exe_path': 'C:/Program Files (x86)/1Cv77/BIN/1cv7org.exe',
   'user': 'reindex_user',
   'pass': 'reindex_db',
   'max_exec_time' : 900      # максимальное время индексирования базы (сек),
                              # по истечении которого процесс 1сv7 снимается
   }

#############################################################################
# точка входа
#############################################################################

umba.clean()
umba.get()
umba.unpack()
umba.rebuild_index(onecparm)

zelenoborsk.clean()
zelenoborsk.get()
zelenoborsk.unpack()
zelenoborsk.rebuild_index(onecparm)

