#!/usr/bin/env python3
from pathlib import Path
import subprocess,argparse
root=Path(__file__).resolve().parents[1]
cases=['05-hlf/cluster-selection','06-logicfilter/input-size','06-logicfilter/parallel-rate']
p=argparse.ArgumentParser(description='ROOT batch: figure PDFs only; no thesis build')
p.add_argument('--include-pending-tof',action='store_true');a=p.parse_args()
if a.include_pending_tof:cases.append('05-hlf/tof-selection')
for case in cases:subprocess.run(['root','-l','-b','-q','plot.C'],cwd=root/'figure'/case,check=True)
