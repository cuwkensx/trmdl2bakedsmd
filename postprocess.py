import os
import subprocess

work_dir= 'C:/_download/mc/models/quickbms/'
data_dir = 'C:/_download/mc/models/pokemon/data/'
output = 'bmsout/'
# Texture step 2.3

for i,pm in enumerate(os.listdir(work_dir+output)):
    pm_data_sir = data_dir+pm+'/'
    for pmsub in os.listdir(pm_data_sir):
        cur_data_dir = pm_data_sir+pmsub+'/'
        output_cur = work_dir+output+pm+'/'+pmsub+'/'
        for fname in os.listdir(output_cur):
            if fname.find('.png')>=0:
                if os.path.exists(cur_data_dir+fname):
                    os.remove(cur_data_dir+fname)
                os.rename(output_cur+fname, cur_data_dir+fname)