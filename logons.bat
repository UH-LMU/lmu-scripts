
set computer=DS1-BIOTEK978
set startdate=2015-06-21 00:00:00

set outputdate=%startdate: 00:00:00=%
set output=c:\temp\logons_%computer%_%outputdate%.csv

logparser -stats:OFF -i evt -o csv "SELECT TimeGenerated,EventID,EXTRACT_TOKEN(Strings,5,'|') AS Logon,EXTRACT_TOKEN(Strings,1,'|') AS Logoff FROM \\%computer%\Security WHERE TimeGenerated > '%startdate%' AND (EventID='4648' AND Strings LIKE '%%winlogon.exe%%' OR EventID='4647')" > %output%
