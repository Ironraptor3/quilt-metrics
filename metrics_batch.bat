@echo off
IF [%1]==[] GOTO Bad_Args
IF [%2]==[] GOTO Bad_Args
GOTO Start
:Bad_Args
echo "Arguments: <input_dir> <output_dir>"
GOTO End
:Start
call \anaconda3\Scripts\activate.bat
python python\get_files.py %~f1 > %~f2\files.txt
python python\metrics.py %~f2\files.txt > %~f2\metrics_py.csv
mpeg7fex_win32_v2\MPEG7Fex.exe DCD 0 1 1 %~f2\files.txt %~f2\dcd_mpeg.txt
python python\extract_dcd.py %~f2\dcd_mpeg.txt %~f2\files.txt False > %~f2\metrics_mpeg.csv
java -jar Vizweb_Metrics.jar %~f2\files.txt > %~f2\metrics_vizweb.csv
python python\merge_results.py %~f2\metrics_py.csv %~f2\metrics_mpeg.csv %~f2\metrics_py_mpeg.csv
python python\merge_results.py %~f2\metrics_vizweb.csv %~f2\metrics_py_mpeg.csv %~f2\metrics_all.csv
python python\heatmaps.py %~f2\metrics_all.csv %~f2\metrics_all_norm.csv %~f2\metrics_all_hist.png
python python\check_linearity.py %~f2\metrics_all.csv > %~f2\metrics_linearity.csv
python python\greatest.py %~f2\metrics_all_norm.csv %~f2\metrics_all_examples.png
:End