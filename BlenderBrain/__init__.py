import bpy

import importlib
import subprocess
import sys


# ------------------ Utilities ------------------
import bg_atlasapi

def get_downloaded_atlases_enum_items():
    '''
        Get enum items with locally downloaded Brainglobe atlases
    '''
    names = bg_atlasapi.list_atlases.get_downloaded_atlases()
    return [(name, name, name) for name in names]


def load_structure_from_obj(filename, object_name="Structure", scale=1e-4, set_origin=False):
    '''
        Load a structure from an obj file
    '''
    bpy.ops.wm.obj_import(filepath=str(filename), forward_axis='Z', up_axis="NEGATIVE_Y")

    ob = bpy.context.active_object
    ob.name = object_name

    # Scale the object in all directions
    ob.scale = (scale, scale, scale)

    if set_origin:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center="MEDIAN")

    return ob


# ------------------ Property Groups ------------------

class RegionLoaderPropertyGroup(bpy.types.PropertyGroup):
    ''' Property group for loading brain region'''

    atlas_name : bpy.props.EnumProperty(
        name = "Atlas",
        items = get_downloaded_atlases_enum_items()
    )

    region_name: bpy.props.StringProperty(
        name = "Region name"
    )
    
    scale_factor: bpy.props.FloatProperty(
        name = "Scale",
        description = "Scaling factor for the imported mesh",
        default = 1e-4,
        min = 1e-6,
        max = 1.0
    )

    set_origin: bpy.props.BoolProperty(
        name = "Set origin to geometry",
        description = "Set the origin of the object to the geometry",
        default = True
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
        scale_factor = context.scene.blenderbrain_load_region_props.scale_factor
        set_origin = context.scene.blenderbrain_load_region_props.set_origin

        atlas = bg_atlasapi.BrainGlobeAtlas(atlas_name,check_latest=False)
        load_structure_from_obj(atlas.meshfile_from_structure(region_name),object_name=region_name,scale=scale_factor, set_origin=set_origin)

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
        col.prop(props, "scale_factor")
        col.prop(props, "set_origin")
        
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
    
    
