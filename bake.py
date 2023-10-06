import os
import subprocess
import json
import time

with open('config.json') as fp:
    tool_config = json.load(fp)

blender_path = tool_config['blender_path']
work_dir= tool_config['work_dir']
data_dir = tool_config['data_dir']
parallel=tool_config['parallel']
resolution=tool_config['resolution']
samples=tool_config['samples']
lag=tool_config['lag']

blender_cmd = blender_path+" --background --render-frame 1 df.blend -P sc.py -- {} "+f'{work_dir} {data_dir} {resolution} {samples} {lag}'

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
