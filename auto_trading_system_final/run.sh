
#!/bin/bash
cd ~/자동매매봇  # 실제 위치로 변경 필요
source ~/.bashrc
python3 run_strategy.py >> strategy_log.txt 2>&1
