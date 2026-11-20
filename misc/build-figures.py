#!/usr/bin/env python3
from pathlib import Path
import subprocess,argparse
root=Path(__file__).resolve().parents[1]
cases=['05-hlf/cluster-selection','06-logicfilter/input-size','06-logicfilter/parallel-rate']
cases += ['05-hlf/flat-or-run000400-input-rate', '05-hlf/flat-or-run000400-multiplicity', '05-hlf/flat-or-run000400-tof', '05-hlf/flat-or-run000400-track', '05-hlf/flat-or-run000400-trigger', '05-hlf/flat-or-run000668-input-rate', '05-hlf/flat-or-run000668-multiplicity', '05-hlf/flat-or-run000668-tof', '05-hlf/flat-or-run000668-track', '05-hlf/flat-or-run000668-trigger', '10-appendix/ltof-readout-diagnosis', '10-appendix/physical-lr-run000400-input-rate', '10-appendix/physical-lr-run000400-multiplicity', '10-appendix/physical-lr-run000400-tof', '10-appendix/physical-lr-run000400-track', '10-appendix/physical-lr-run000400-trigger', '10-appendix/physical-lr-run000668-input-rate', '10-appendix/physical-lr-run000668-multiplicity', '10-appendix/physical-lr-run000668-tof', '10-appendix/physical-lr-run000668-track', '10-appendix/physical-lr-run000668-trigger']
p=argparse.ArgumentParser(description='ROOT batch: figure PDFs only; no thesis build')
p.add_argument('--include-pending-tof',action='store_true');a=p.parse_args()
if a.include_pending_tof:cases.append('05-hlf/tof-selection')
for case in cases:
 subprocess.run(['root','-l','-b','-q','plot.C'],cwd=root/'figure'/case,check=True)
