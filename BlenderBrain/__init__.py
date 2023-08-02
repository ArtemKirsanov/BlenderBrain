import bpy


bl_info = {
    "name" : "BlenderBrain",
    "author" : "Artem Kirsanov",
    "description" : "Import brain meshes via BrainGlobe atlas API",
    "blender" : (3, 3, 0),
    "version" : (1, 0, 0),
    "location" : "View3D > BlenderBrain",
    "warning" : "",
    "category" : "3D View"
}

import importlib
import subprocess
import sys


# ------------------ Utilities ------------------


def check_and_install_modules():
    '''
        Automatically install required Python modules
    '''
    required_modules_import_names = ["bg_atlasapi", "numpy"]  # Required Python modules
    required_modules_install_names = ["bg-atlasapi", "numpy"]


    missing_modules = []
    for k,module_name in enumerate(required_modules_import_names):
        try:
            print(f"Module {module_name} is already installed. Importing...")
            importlib.import_module(module_name)
            
        except ImportError:
            missing_modules.append(required_modules_install_names[k])
            
    if missing_modules:
        print("Found missing modules: ", missing_modules)
        for module in missing_modules: 
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"{module} installed successfully.")
            except subprocess.CalledProcessError:
                print(f"Failed to install {module}.")


check_and_install_modules()
import bg_atlasapi

def get_downloaded_atlases_enum_items():
    '''
        Get enum items with locally downloaded Brainglobe atlases
    '''
    names = bg_atlasapi.list_atlases.get_downloaded_atlases()
    return [(name, name, name) for name in names]


# def get_available_atlases_enum_items():
#     '''
#         Get enum items with all available Brainglobe atlases that you can install
#     '''
#     available_atlases = bg_atlasapi.list_atlases.get_all_atlases_lastversions()

#     # Get local atlases:
#     atlases = bg_atlasapi.list_atlases.get_atlases_lastversions()
#     available_for_download = []
    
#     # Get atlases not yet downloaded:
#     for atlas in available_atlases.keys():
#         if atlas not in atlases.keys():
#             available_for_download.append(str(atlas))

#     return [(name, name, name) for name in available_for_download]
    


def load_structure_from_obj(filename, object_name="Structure", clamp_size=0.01):
    bpy.ops.wm.obj_import(filepath=str(filename), clamp_size=clamp_size, forward_axis='Z', up_axis="NEGATIVE_Y")
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center="MEDIAN")
    ob = bpy.context.active_object
    ob.name = object_name
    return ob
# ------------------ Property Groups ------------------

# class AtlasDownloaderPropertyGroup(bpy.types.PropertyGroup):
#     ''' Property group for downloading BrainGlode atlases'''
#     atlas_name : bpy.props.EnumProperty(
#         name = "Atlas",
#         items = get_available_atlases_enum_items()
#     )

class RegionLoaderPropertyGroup(bpy.types.PropertyGroup):
    ''' Property group for loading brain region'''

    atlas_name : bpy.props.EnumProperty(
        name = "Atlas",
        items = get_downloaded_atlases_enum_items()
    )

    region_name: bpy.props.StringProperty(
        name = "Region name"
    )


# ------------------ Operators ------------------


# class BLENDERBRAIN_OT_AtlasDownloader(bpy.types.Operator):
#     '''
#        Operator to automatically download BrainGlobe Atlases
#     '''

#     bl_idname = 'blenderbrain.download_atlas'
#     bl_label =  'Download Atlas'

#     def execute(self, context):
#         atlas_name = context.scene.blenderbrain_download_atlas_props.atlas_name
#         print("Atlas to download: ",atlas_name)
#         return {"FINISHED"}


class BLENDERBRAIN_OT_RegionLoader(bpy.types.Operator):
    '''
       Operator to load a brain region mesh from brainglobe atlas
    '''

    bl_idname = 'blenderbrain.load_region'
    bl_label =  'Load brain region'
    active_atlas = None

    def execute(self, context):
        atlas_name = context.scene.blenderbrain_load_region_props.atlas_name
        region_name = context.scene.blenderbrain_load_region_props.region_name
        atlas = bg_atlasapi.BrainGlobeAtlas(atlas_name,check_latest=False)
        load_structure_from_obj(atlas.meshfile_from_structure(region_name),object_name=region_name)

        return {"FINISHED"}

# ------------------ UI Panels ------------------

# class BLENDERBRAIN_PT_AtlasDownloader(bpy.types.Panel):
#     '''
#         UI panel for downloading BrainGlobe atlases
#     '''
#     bl_label =  'Download Atlas'
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "BlenderBrain"
    
#     def draw(self, context):
#         layout = self.layout
#         props = context.scene.blenderbrain_download_atlas_props
#         col = layout.column()
#         col.prop(props, "atlas_name")
        
#         row = layout.row()
#         row.operator("blenderbrain.download_atlas", icon="SCRIPT")


class BLENDERBRAIN_PT_RegionLoader(bpy.types.Panel):
    '''
        UI panel for loading a brain region
    '''
    bl_label =  'Load brain region'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBrain"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.blenderbrain_load_region_props
        col = layout.column()
        col.prop(props, "atlas_name")
        col.prop(props, "region_name")
        
        row = layout.row()
        row.operator("blenderbrain.load_region")


ordered_classes = [
    # Property Groups
    RegionLoaderPropertyGroup,

    # Operators
  #  BLENDERBRAIN_OT_AtlasDownloader,
    BLENDERBRAIN_OT_RegionLoader,


    # UI Panels
   # BLENDERBRAIN_PT_AtlasDownloader,
    BLENDERBRAIN_PT_RegionLoader
]


def register():
    for cl in ordered_classes:
        bpy.utils.register_class(cl)
  #  bpy.types.Scene.blenderbrain_download_atlas_props = bpy.props.PointerProperty(type = AtlasDownloaderPropertyGroup)
    bpy.types.Scene.blenderbrain_load_region_props = bpy.props.PointerProperty(type = RegionLoaderPropertyGroup)


def unregister():
    for cl in reversed(ordered_classes):
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.blenderbrain_load_region_props
  #  del bpy.types.Scene.blenderbrain_download_atlas_props

if __name__ == "__main__":
    register()
    
    
