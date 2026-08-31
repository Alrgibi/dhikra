import json, fitz, numpy as np, sys
pdf=fitz.open("thesis.pdf"); d=json.load(open("pages2.json"))
starts=[(k,int(v)) for k,v in d.items() if (k.startswith("ch_") or k.startswith("app_") or k=="references")]
starts.sort(key=lambda kv: kv[1])
def blank_tail(pno):
    p=pdf[pno]; pix=p.get_pixmap(dpi=36)
    a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3]
    ink=(a.sum(axis=2)<700).any(axis=1)
    y0=int(0.09*pix.height); y1=int(0.90*pix.height); rows=ink[y0:y1]
    idx=np.where(rows)[0]
    return 1.0 if len(idx)==0 else 1-(idx[-1]+1)/len(rows)
N=pdf.page_count
for i,(k,s) in enumerate(starts):
    e=(starts[i+1][1]-1) if i+1<len(starts) else N
    print(f"{k:12s} {s:4d}–{e:4d} = {e-s+1:3d}  last-page blank {blank_tail(e-1):4.2f}")
fm=starts[0][1]-1
print("front matter 1–%d:"%fm, [round(float(blank_tail(i)),2) for i in range(fm)])
print("total pages", N)
