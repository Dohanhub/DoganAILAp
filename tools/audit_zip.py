import sys, zipfile, os, time
out = sys.argv[-1] if len(sys.argv)>1 else "bundle.zip"
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root,_,files in os.walk('.'):
        for f in files:
            if f.endswith('.yaml') or f.endswith('.json'):
                z.write(os.path.join(root,f))
print("Wrote", out)
