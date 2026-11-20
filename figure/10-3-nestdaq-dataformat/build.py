#!/usr/bin/env python3
"""Rebuild original SVGs, PDF inclusion copies and appendix text, locally only."""
from pathlib import Path
from html import escape
import argparse,json,os,shutil,subprocess,tempfile
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--from-existing-svg',action='store_true',help='Preserve the original display SVG bytes; only convert to PDF and typeset article');args=parser.parse_args()
if not args.from_existing_svg:
 # Preserve the original generator byte-for-byte, including its expected directory layout.
 with tempfile.TemporaryDirectory(prefix='nestdaq-format-svg-') as tmp:
  root=Path(tmp);d=root/'docs/format-study';d.mkdir(parents=True)
  for name in ['schema','fonts']:shutil.copytree(P/name,d/name)
  for name in ['build_format.py','packing-notes.html','pipeline-notes.html','format-notes.html','font-controls.js']:shutil.copy2(P/name,d/name)
  shutil.copytree(P/'reference/source',root/'resources/GitHub/nestdaq-user-impl')
  subprocess.run(['python3',str(d/'build_format.py'),'--verify-cpp'],check=True)
  shutil.copytree(d/'figures',P/'editable-svg',dirs_exist_ok=True)
  shutil.copy2(d/'layout-verification.json',P/'layout-verification.json')
  conf=root/'fonts.conf';conf.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>'+escape(str(P/'fonts'))+'</dir><cachedir>'+escape(str(root/'cache'))+'</cachedir><alias><family>NestDAQ Noto Serif</family><prefer><family>Noto Serif</family></prefer></alias></fontconfig>')
  env=dict(os.environ,FONTCONFIG_FILE=str(conf))
  for dest in sorted((P/'svg').glob('*.svg')):
   subprocess.run(['rsvg-convert','--format=svg','--output',str(dest),str(d/'figures'/dest.name)],env=env,check=True)
(P/'pdf').mkdir(exist_ok=True)
for svg in sorted((P/'svg').glob('*.svg')):
 subprocess.run(['rsvg-convert','--format=pdf','--output',str(P/'pdf'/(svg.stem+'.pdf')),str(svg)],check=True)
subprocess.run(['python3',str(P/'article_to_tex.py')],check=True)
print('21 original SVG diagrams -> vector PDF inclusion copies; HTML explanation -> appendix-body.tex. No thesis build or publication.')
