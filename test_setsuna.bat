@echo off

:: Change the path of features, packet, model in order to test the program in batch
:: Only run the program under Windows
:: If you wish to run the program in Linux, remove '@echo off' located in the first line

:: python .\setsuna_cli.py -r train -f ..\zDataset\benign\CIC2017_Benign_merged.npy -m .\CIC2017_Benign_merged_5000_10000.pkl -ae 9 -fg 10000 -ag 50000

:: python .\setsuna_cli.py -r exec -f ..\zDataset\cap\20220124_0017.npy -m .\CIC2017_Benign_merged_5000_10000.pkl -ae 9

python .\setsuna_cli.py -r hybrid -p ..\zDataset\cap\20220124_0017.pcapng -m .\CIC2017_Benign_merged_5000_10000.pkl -ae 9

:: python .\setsuna_toolbox.py --pcapIn ..\zDataset\cap

:: python .\setsuna_toolbox.py --tsvIn ..\zDataset\cap

:: python .\setsuna_toolbox.py --npyIn ..\zDataset\cap