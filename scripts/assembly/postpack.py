#!/usr/bin/env python3
"""postpack.py -- mark the Normal style as the document default (python-docx and Word both expect one)."""
import sys, zipfile, shutil, os, re, tempfile
src=sys.argv[1]
tmp=tempfile.mkdtemp()
with zipfile.ZipFile(src) as z: z.extractall(tmp)
p=os.path.join(tmp,'word','styles.xml'); s=open(p,encoding='utf-8').read()
s2=s.replace('<w:style w:type="paragraph" w:styleId="Normal">','<w:style w:type="paragraph" w:default="1" w:styleId="Normal">',1)
assert s2!=s, "Normal style not found"
open(p,'w',encoding='utf-8').write(s2)
out=src+'.tmp'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    # [Content_Types].xml first
    for root,_,files in os.walk(tmp):
        for f in files:
            full=os.path.join(root,f); arc=os.path.relpath(full,tmp)
            z.write(full,arc)
shutil.move(out,src); shutil.rmtree(tmp); print("postpack ok", src)
