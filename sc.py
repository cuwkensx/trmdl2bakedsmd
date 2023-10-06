import bpy
from math import radians
import PokemonSwitch
import io_scene_valvesource.export_smd
import addon_utils
import os
import time
import json
import sys

def refresh_panels():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


addon_utils.enable('UV-Packer')
addon_utils.enable('PokemonSwitch')
addon_utils.enable('io_scene_valvesource')

def convert_prepare(resolution = 512):
    bpy.context.scene.render.engine='CYCLES'
    bpy.context.scene.cycles.device='GPU'
    bpy.context.scene.render.bake.use_pass_direct=False
    bpy.context.scene.render.bake.use_pass_indirect=False
    # UV-Packer config
    uv_padding = resolution//500
    bpy.context.scene.UVPackerProps.uvp_height=resolution
    bpy.context.scene.UVPackerProps.uvp_width=resolution
    bpy.context.scene.UVPackerProps.uvp_padding=uv_padding
    bpy.context.scene.UVPackerProps.uvp_rotate='1' # default value provided by addon
    refresh_panels()


def clearpm(col_name):
    # clear model
    collection = bpy.data.collections[col_name]
    for ob in collection.objects:
        bpy.data.objects.remove(ob)
    bpy.data.collections.remove(collection)


def loadpm(pm, resolution=512):
    bpy.context.scene.render.engine='BLENDER_EEVEE'
    pm_dex = int(pm[2:])
    pm_name = namedex[f'{pm_dex}'] if f'{pm_dex}' in namedex else ''
    if pm_dex<1000:
        pm_dex = '{:03d}'.format(pm_dex)
    else:
        pm_dex = f'{pm_dex}'
    modeldir_smd_base = modeldir+f"{resolution}/{pm_dex}_{pm_name}/all/base/"
    if len(pm_name)>0 and os.path.exists(modeldir_smd_base):
        forms = os.listdir(modeldir_smd_base)
        for form_name in forms:
            if form_name=='none':
                modeldir_smd = modeldir_smd_base+form_name+'/'
                # load model
                model_name = pm_name+'.smd'
                bpy.ops.import_scene.smd(filepath=modeldir_smd+pm_name+'.smd')
                obj=bpy.data.objects[pm_name]
                # load baked image texture
                filepath = modeldir_smd+'texture.png'
                img = bpy.data.images.load(filepath)
                bpy.context.view_layer.objects.active = obj
                # Set as active texture image on material
                # node_tree = obj.active_material.node_tree
                mat=obj.data.materials[0]
                mat.use_nodes = True 
                node_tree=mat.node_tree
                nodes = node_tree.nodes
                tex = nodes.new('ShaderNodeTexImage')
                tex.image = img
                nodes.active=tex
                bsdf = nodes.get('Principled BSDF')
                # Link image texture to base color  
                links = node_tree.links
                links.new(tex.outputs[0], bsdf.inputs[0])


def convertpm(pm, bounces=4, samples=32, resolution=512):
    pmbase = data_dir+f"{pm}/"
    pmsubs = {}
    for pmsub in os.listdir(pmbase):
        flag=False # shiny flag
        if os.path.isdir(pmbase+pmsub):
            sub_idx = int(pmsub.split('_')[-1])+100*int(pmsub.split('_')[-2])
            for fname in os.listdir(pmbase+pmsub):
                if '.trmdl' in fname:
                    pmsubs[sub_idx]=[pmsub, fname, pmbase+pmsub+'/'+fname]
                if '.png' in fname and 'rare' in fname:
                    flag=True
            if sub_idx in pmsubs:
                pmsubs[sub_idx].append(flag)
    for i,sub_idx in enumerate(sorted(pmsubs.keys())):
        pmsub, model_name, pmpath, flag = pmsubs[sub_idx]
        form_name = 'none' if i==0 else f'sub{sub_idx}'
        pm_dex = int(pm[2:])
        pm_name = namedex[f'{pm_dex}'] if f'{pm_dex}' in namedex else ''
        if pm_dex<1000:
            pm_dex = '{:03d}'.format(pm_dex)
        else:
            pm_dex = f'{pm_dex}'
        modeldir_smd_base = modeldir+f"{resolution}/{pm_dex}_{pm_name}/all/base/"
        forms = [form_name, form_name+'_shiny'] if flag else [form_name]
        if form_name=='none' and len(forms)>1:
            forms[1]='shiny'
        for fidx, form_name in enumerate(forms[:1]):
            convert_prepare(resolution)
            bpy.context.scene.cycles.samples=samples
            bpy.context.scene.cycles.diffuse_bounces=bounces
            if len(pmsubs)>0:
                with open(work_dir+'log.txt', 'a+') as fp:
                    fp.write(f'load {model_name} {pm_name} {form_name}\n')
            modeldir_smd = modeldir_smd_base+form_name+'/'
            os.makedirs(modeldir_smd, exist_ok=True)
            # load model
            bpy.ops.custom_import_scene.pokemonscarletviolet(filepath=pmpath, rare=(fidx==1))
            obj=bpy.data.objects[model_name]
            obj.rotation_euler=(radians(90),0,0)
            # merge object
            mesh_names = [meh.name for meh in bpy.data.objects if meh.type=='MESH']
            main_mesh_name = mesh_names[0]
            for mesh_name in mesh_names:
                if 'mesh_shape' in mesh_name and 'body' in mesh_name:
                    main_mesh_name=mesh_name
                    break
            main_mesh = bpy.data.objects[main_mesh_name]
            bpy.context.view_layer.objects.active=main_mesh
            collection = bpy.data.collections[model_name.split('.')[0]]
            [obj.select_set(True) for obj in collection.objects if obj.type=='MESH']
            bpy.ops.object.join()
            # unwrap to new uv, only do this to normal model, since the shiny one reuse the UV map of it
            uv_layer = main_mesh.data.uv_layers.new()
            main_mesh.data.uv_layers.active = uv_layer
            bpy.ops.uvpackeroperator.packbtn()
            time.sleep(1)
            bpy.ops.object.editmode_toggle()
            # Create image to bake to
            imgname = 'texture'
            img = bpy.data.images.new(imgname, resolution, resolution) 
            img.filepath = modeldir_smd+imgname+'.png'
            # Set as active texture image on material
            mat = bpy.context.active_object.active_material
            node_tree = mat.node_tree
            tex = node_tree.nodes.new('ShaderNodeTexImage')
            tex.image = img
            node_tree.nodes.active=tex
            bpy.context.view_layer.objects.active=main_mesh
            [obj.select_set(True) for obj in collection.objects if obj.type=='MESH']
            bpy.ops.object.bake(type='DIFFUSE')  # Bake to the set image texture
            while True:
                time.sleep(0.5)
                if img.is_dirty:
                    break
            time.sleep(4)
            img.save() # Save image
            time.sleep(0.2)
            # merge material
            bpy.context.view_layer.objects.active=main_mesh
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.material_slot_assign()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.material_slot_remove_unused()
            bpy.context.active_object.material_slots[0].material.name='Material'
            bpy.context.active_object.material_slots[0].material.name='Material'
            time.sleep(0.1)
            # exprot fbx
            bpy.context.view_layer.objects.active=obj
            fbx_path = fbxdir+pmsub+'.fbx'
            if not os.path.exists(fbx_path):
                bpy.ops.export_scene.fbx(filepath=fbx_path, object_types={'ARMATURE'})
            # exprot smd
            smd_paths = [modeldir_smd+model_name.split('.')[0]+'.smd', modeldir_smd+pm_name+'.smd']
            for smd_path in smd_paths:
                if os.path.exists(smd_path):
                    os.remove(smd_path)
            bpy.context.scene.vs.export_path=modeldir_smd
            bpy.context.scene.vs.export_format='SMD'
            bpy.ops.export_scene.smd()
            os.rename(smd_paths[0], smd_paths[1])
            clearpm(model_name.split('.')[0]) # clear model
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            time.sleep(0.5)


pmf = 'pm{:04d}'
pdex = int(sys.argv[-3]) 
pm=pmf.format(pdex)
work_dir = sys.argv[-2]
data_dir = sys.argv[-1]

modeldir = work_dir+'modelsmd/'
fbxdir = work_dir+'fbx/'
tmpdir = work_dir+'tmp/'
os.makedirs(fbxdir, exist_ok=True)
os.makedirs(tmpdir, exist_ok=True)
with open(work_dir+'dex.json') as fp:
    namedex = json.load(fp)

convertpm(pm)