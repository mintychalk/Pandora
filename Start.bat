@Echo off
chcp 65001
:Start

python pandora.py
timeout 3

goto Start
