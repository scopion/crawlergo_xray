httpx -l domain.txt  -title -tech-detect -status-code -title -follow-redirects
./xray_linux_amd64 webscan --listen 127.0.0.1:7777 --html-output proxy.html
python3 launcher_new.py


7 1  * * * cd /opt/crawlergo_x_XRAY && /usr/bin/python3 /opt/crawlergo_x_XRAY/launcher_new.py > /opt/crawlergo_x_XRAY/log.log & 
