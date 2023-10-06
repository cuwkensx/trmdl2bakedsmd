import os
import subprocess

work_dir= 'C:/_download/mc/models/quickbms/'
data_dir = 'C:/_download/mc/models/pokemon/data/'
cmd_temp = work_dir+'quickbms.exe Switch_BNTX.bms {}bntx ' #pm0000/pm0000
output = 'bmsout/'

# # rename animation files to .gfbanm format, which can be processed by Switch ToolBox
# anim_dir = work_dir+'anim/'
# for i,pm in enumerate(os.listdir(data_dir)):
#     pm_data_sir = data_dir+pm+'/'
#     for pmsub in os.listdir(pm_data_sir):
#         cur_data_dir = pm_data_sir+pmsub+'/'
#         output_cur = anim_dir+pm+'/'+pmsub+'/'
#         os.makedirs(output_cur, exist_ok=True)
#         for fname in os.listdir(cur_data_dir):
#             if fname.find('.tranm')>0:
#                 os.rename(cur_data_dir+fname, output_cur+fname[:-5]+'gfbanm')

# Texture step 1
# calling quickbms cli to convert bntx (pokemon SV texture format) to dds
subs = []
for i,pm in enumerate(os.listdir(data_dir)):
    pm_data_sir = data_dir+pm+'/'
    for pmsub in os.listdir(pm_data_sir):
        cur_data_dir = pm_data_sir+pmsub+'/'
        os.makedirs(cur_data_dir+'bntx', exist_ok=True)
        for fname in os.listdir(cur_data_dir+''):
            if fname.find('.bntx')>=0:
                os.rename(cur_data_dir+fname, cur_data_dir+'bntx/'+fname)
        output_cur = output+pm+'/'+pmsub
        os.makedirs(work_dir+output_cur, exist_ok=True)
        subs.append(subprocess.Popen(cmd_temp.format(cur_data_dir)+output_cur
                        ,cwd=work_dir))

[sub.wait() for sub in subs]

# Texture step 2.1
# moving dds images to directories like 'bmsout/pm0000/pm0000_00/', which will be used in the next step
for i,pm in enumerate(os.listdir(data_dir)):
    output_base = output+pm+'/'
    for pmsub in os.listdir(work_dir+output_base):
        output_cur = output_base+pmsub
        if not os.path.isdir(work_dir+output_cur):
            os.remove(work_dir+output_cur)
        else:
            for dirname in os.listdir(work_dir+output_cur):
                cur_dir = work_dir+output_cur+'/'+dirname+'/'
                if os.path.isdir(cur_dir):
                    for fname in os.listdir(cur_dir):
                        if not os.path.exists(work_dir+output_cur+'/'+fname):
                            os.rename(cur_dir+fname, work_dir+output_cur+'/'+fname)
                        else:
                            os.remove(cur_dir+fname)
                    os.rmdir(cur_dir)


# Texture step 2.2
# Note: currently we do not find command line (or script) tools to convert dds to png. (I have tried wand, a python lib based on ImageMaigick, which can only parse some dds image)
# manually convert dds to png: open noesis, goto Tools->Batch Process, \
# set input and output extension, click 'Folder batch' button aand select your 'bmsout' folder,\
# click 'Recursive',
# set 'Output Path' to $inpath$\$inname$.$outext$
# click 'Export' in the lower-right button
# wait for Noesis to finish (it will pop a message box when finishing)
