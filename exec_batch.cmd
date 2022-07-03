@echo off
for /R D:\Dokodemo\capStoneProject\_code\zDataset\malicious\KITSUNE_TRAIN %%i in (*.npy) do (
 python .\setsuna_cli.py -r exec -f %%i -m .\CIC2017_Benign_merged_5000_10000.pkl -ae 9
)
pause