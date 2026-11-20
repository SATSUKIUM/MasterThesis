#!/usr/bin/env python3
from pathlib import Path
import subprocess,argparse
root=Path(__file__).resolve().parents[1]
cases=['05-hlf/cluster-selection','06-logicfilter/input-size','06-logicfilter/parallel-rate']
cases += ['05-hlf/common-benchmark-'+k for k in ['tof','multiplicity','track','summary','offline','input-rate']]
cases += ['05-hlf/merged-run000668-'+k for k in ['tof','multiplicity','track','input-rate']]
cases += ['10-appendix/merged-run000400-'+k for k in ['tof','multiplicity','track','input-rate']]
cases += ['05-hlf/flat-or-run000668-'+k for k in ['tof','multiplicity','track','input-rate']]
cases += ['10-appendix/flat-or-run000400-'+k for k in ['tof','multiplicity','track','input-rate']]
cases += ['05-hlf/trigger-logic-run000668','10-appendix/trigger-logic-run000400']
p=argparse.ArgumentParser(description='ROOT batch: figure PDFs only; no thesis build')
p.add_argument('--include-pending-tof',action='store_true');a=p.parse_args()
if a.include_pending_tof:cases.append('05-hlf/tof-selection')
for case in cases:
 if case=='05-hlf/common-benchmark-summary':subprocess.run(['python3','make_tables.py'],cwd=root/'figure'/case,check=True)
 subprocess.run(['root','-l','-b','-q','plot.C'],cwd=root/'figure'/case,check=True)
