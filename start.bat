@echo off

pip install ifaddr
pip install psutil
pip install subprocess

cls

python %~dp0\zmianaip.py

pause