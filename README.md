# contricopy
Alternative zu synctoy/contribute

Microsoft synctoy wurde abgekündigt (soll dotnet 2.0 brauchen und nicht mehr unter Windows 11 funktionieren).

In synctoy war keine Batch-Abarbeitung mehrere Verzeichnispaare möglich.

contricopy implementiert nur den "Contribute"-Mode, d.h. es werden nur Dateien von links nach rechts kopiert, gelöscht wird nichts.
contricopy arbeitet im *batch*-Betrieb alle Verzeichnispaar ab, die in der Konfigurationsdatei eingetragen sind.

Voraussetzungen für den Aufruf:
- python installieren.
- contricopy-Dateien in ein Verzeichnis kopieren.
- Alle Verzeichnisse in contricopy.cfg eintragen.
  
Aufrufbeispiel: 
```
    E:\dev_priv\python_svn\contricopy>python contricopy.py
```
Die Konfigurationsdatei contricopy.cfg wird im aktuellen Verzeichnis gesucht.
Die Logdatei contricopy*.log wird ins aktuelle Verzeichnis geschrieben.

contricopy wurde unter Windows 10 mit python 3.10.11 getestet:
- Zeitstempel und Schreibschutz bleiben soweit möglich erhalten.
- Die Eigenschaft *hidden* geht verloren.
