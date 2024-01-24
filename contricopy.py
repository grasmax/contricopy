import os
import fileinput
import json
import datetime
import base64
import sys
import logging
from logging.handlers import RotatingFileHandler
import time
import shutil

   # synctoy-Alternative, weil dieses Tool 2021 abgekündigt wurde, dotnet 2.0 braucht und nicht mehr unter Windows11 funktioniert...
   # Außerdem war in synctoy keine Batch-Abarbeitung möglich
   # Es wurde hier nur der "Contribute"-Mode nachgebaut
   # cfg wird im aktuellen Verzeichnis gesucht, log wird ins aktuelle Verzeichnis geschrieben
   # Aufruf: 
   #    E:\dev_priv\python_svn\contricopy\contricopy\contricopy>python contricopy.py   
   # getestet unter Windows 10 mit python 3.10.11:
   # Zeitstempel und Schreibschutz bleiben soweit möglich erhalten
   # hidden-Eigenschaft geht verloren

class CContriCopy:

   ###### __init__(self) ##############################################################################
   def __init__(self):
      print("Programmstart")

      self.iFileNew = 0;
      self.iFileRepl = 0;
      self.iDir = 0;
      
      self.tNow = datetime.datetime.now()
      self.sNow = self.tNow.strftime("%Y-%m-%d-%H-%M")

      try:
         logging.basicConfig(encoding='utf-8', level=logging.INFO, # absteigend: DEBUG, INFO, WARNING,ERROR, CRITICAL
                             # DEBUG führt dazu, dass der HTTP-Request samt Passwörtern und APIKeys geloggt wird!
                             style='{', datefmt='%Y-%m-%d %H:%M:%S', format='{asctime} {levelname} {filename}:{lineno}: {message}',
#                            handlers=[RotatingFileHandler(f'./contricopy_{self.sNow}.log', maxBytes=100000, backupCount=10, encoding='utf-8')],)
                             handlers=[RotatingFileHandler(f'./contricopy.log',             maxBytes=100000, backupCount=10, encoding='utf-8')],)
      except Exception as e:
         print(f'Fehler in logging.basicConfig: {e}')
         quit()



      self.Info(f'Programmstart: {self.tNow}')

      sCfgFile = "contricopy.cfg" # sFile = "E:\\dev_priv\\python_svn\\contricopy\\contricopy\\contricopy\\contricopy\\.cfg"
      try:
         f = open(sCfgFile, "r", encoding="utf-8")
      except Exception as e:
         self.Fehler(f'Fehler in open({sCfgFile}): {e}')
         quit()

      try:
         Settings = json.load(f)
         f.close()
      except Exception as e:
         self.Fehler(f'Fehler in json.load(): {e}')
         quit()
      
      try:
         self.Cfg = Settings['Paare']

      except Exception as e:
         self.Fehler(f'Fehler beim Einlesen von: {sCfgFile}: {e}')
         quit()

   ###### Info(self, sText) ##############################################################################
   def Info(self, sText):
      sOut = "Info: " + sText
      logging.info( sOut)
      print( sOut)


   ###### Fehler(self, sText) ##############################################################################
   def Fehler(self, sText):
      sOut = "Fehler: " + sText
      logging.error( sOut)
      print( sOut)



   ###### Kopieren(self)  ##############################################################################
   def Kopieren(self):
      try:
         
         for paar in self.Cfg:
            try:
               pp = self.Cfg[paar]
               quelle = pp['q']
               ziel = pp['z']

               # Ziel-Hauptverzeichnis ggf auch erst erstellen
               if not os.path.exists(ziel):
                  try:
                     os.makedirs(ziel)
                  except Exception as e:
                     self.Fehler(f'Ausnahme in Kopieren(): {ziel} kann nicht erstellt werden: {e}')
                     continue;
                           
                  if not os.path.exists(ziel):
                     self.Fehler(f'Fehler in Kopieren(): {ziel} kann nicht erstellt werden: {e}')
                  else:
                     self.iDir += 1
                     self.Info(f'{ziel} erstellt')

               # Verzeichnisse im Zielverzeichnis erstellen
               self.Info( f"Verzeichnisse: {paar}: {pp['q']} --> {pp['z']}")
               for root, dirs, files in os.walk(quelle, topdown=False):
                  for name in dirs:
                     qdir = os.path.join(root, name)
                     zdir = qdir.replace(quelle, ziel)
                     
                     self.Info(f'{zdir}')
                     
                     if not os.path.exists(zdir):
                        try:
                           os.makedirs(zdir)
                        except Exception as e:
                           self.Fehler(f'Ausnahme in Kopieren(): {zdir} kann nicht erstellt werden: {e}')
                           continue;
                           
                        if not os.path.exists(zdir):
                           self.Fehler(f'Fehler in Kopieren(): {zdir} kann nicht erstellt werden: {e}')
                        else:
                           self.iDir += 1
                           self.Info(f'{zdir} erstellt')

               # Dateien im Zielverzeichnis erstellen oder neue Version dorthin kopieren
               self.Info( f"Dateien: {paar}: {pp['q']} --> {pp['z']}")
               for root, dirs, files in os.walk(quelle, topdown=False):
                  for name in files:
                     qfile = os.path.join(root, name)
                     zfile = qfile.replace(quelle, ziel)

                     iBytes = os.path.getsize( qfile)
                     if iBytes > 100000000:
                        self.Info(f'Dateigröße: {qfile}: {iBytes}')
                 
                     if not os.path.isfile(zfile):
                        try:
                           shutil.copyfile(qfile, zfile)                     
                        except Exception as e:
                           self.Fehler(f'Ausnahme in Kopieren(): {zfile} kann nicht erstellt werden: {e}')
                           continue;

                        if not os.path.isfile(zfile):
                           self.Fehler(f'Fehler in Kopieren(): {zfile} kann nicht erstellt werden: {e}')
                        else:
                           self.iFileNew += 1
                           self.Info(f'{zfile} erstellt')
                           
                     else:
                        tmq = os.path.getmtime(qfile)
                        tmz = os.path.getmtime(zfile)
                        #stmq =  datetime.datetime.fromtimestamp(tmq)
                        #stmz =  datetime.datetime.fromtimestamp(tmz)
                        if tmq > tmz:

                           try:
                              shutil.copy2(qfile, zfile,follow_symlinks = True) # Zeitstempel mitnehmen                    
                           except Exception as e:
                              self.Fehler(f'Ausnahme in Kopieren(): {zfile} kann nicht aktualisiert werden: {e}')
                              continue;
                        
                           tmz = os.path.getmtime(zfile)
                           if tmq != tmz:
                              self.Fehler(f'Fehler in Kopieren(): {zfile} kann nicht aktualisiert werden: {e}')
                           else:
                              self.iFileRepl += 1
                              self.Info(f'{zfile} aktualisiert ({time.ctime(tmz)})')
                              #tMod = datetime.datetime.fromtimestamp(tM)

            except Exception as e:
               self.Fehler(f'Ausnahme in Kopieren(): {e}')
               quit()


      except Exception as e:
         self.Fehler(f'Fehler in Kopieren(): {e}')
         quit()
      
      

cc = CContriCopy()
cc.Kopieren()
cc.Info(f'{cc.iDir} Verzeichnisse erstellt, {cc.iFileNew} Dateien kopiert, {cc.iFileRepl} Dateien ersetzt')

