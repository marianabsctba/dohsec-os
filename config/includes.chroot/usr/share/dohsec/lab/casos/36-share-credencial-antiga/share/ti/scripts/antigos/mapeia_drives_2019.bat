@echo off
REM script antigo do logon - nao usar mais
net use S: \\usina-fs01\setores /user:USINA\svc_impressao D0nut$2019! /persistent:no
net use P: \\usina-fs01\publico /persistent:no
