import os
import subprocess
import json
import time

blender_path = "C:/_download/blender-3.3.2-windows-x64/blender.exe"
work_dir= 'C:/_download/mc/models/quickbms/'
data_dir = 'C:/_download/mc/models/pokemon/data/'
blender_cmd = blender_path+" --background --render-frame 1 df.blend -P sc.py -- {} "+f'{work_dir} {data_dir}'
parallel=8

with open(work_dir+'dex.json') as fp:
    namedex = json.load(fp)

pmf = 'pm{:04d}'
start_idx = 0
pmall = os.listdir(data_dir)
pmlist = []
for pdex in range(start_idx, 1200):
    pm = pmf.format(pdex)
    if pm in pmall:
        pmlist.append(pdex)

renders = []
for i,pdex in enumerate(pmlist):
    print(pdex)
    renders.append(subprocess.Popen(blender_cmd.format(pdex), cwd=work_dir))
    if (i+1)%parallel==0:
        [render.wait() for render in renders]
    time.sleep(3)
