import bpy
import math
import os


def degree2radians(degree):
    return degree * math.pi / 180.


def switch_to_mode(mode):
    if mode == 'OBJECT':
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            
    if mode == 'EDIT':
        if bpy.context.object.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
    
    
def get_object(name = 'Cube'):
    """Get the object by its name"""
    return bpy.context.scene.objects[name]
    
    
def get_all_objects_names():
    return bpy.context.scene.objects.keys()
    
    
def is_object_in_scene(object_name):
    return object_name in get_all_objects_names()


def get_active_name():
    """Get the name for the currently active object"""
    return bpy.context.active_object.name


def set_attribute(object_name, attribute, value):
    setattr(get_object(object_name), attribute, value)


def clone_object(object_name, location=(0,0,0)):
    """Create another identical object"""
    old_obj = get_object(object_name)
    new_obj = old_obj.copy()
    new_obj.data = old_obj.data.copy()
    new_obj.location = location
    bpy.context.collection.objects.link(new_obj)
    return new_obj.name


def hide_object(object_name):
    get_object(object_name).hide_viewport = True  


def show_object(object_name):
    get_object(object_name).hide_viewport = False


def delete_all_objects(objs = bpy.context.scene.objects):
    bpy.ops.object.delete({"selected_objects": objs})


def delete_objects(list_object_names):
    for object_name_to_delete in list_object_names:
        object = get_object(object_name_to_delete)
        object.select_set(True)
        bpy.data.objects.remove(object, do_unlink=True)
    
    
def create_camera(location=(0,0,0), rotation_euler=(0,0,0), *, object_name='Camera'):
    camera_data = bpy.data.cameras.new(name=object_name + '-data')
    camera_object = bpy.data.objects.new(object_name, camera_data)
    camera_object.location = location
    camera_object.rotation_euler = rotation_euler
    camera_object.name = object_name
    bpy.context.scene.collection.objects.link(camera_object)
    bpy.context.scene.camera = bpy.data.objects[camera_object.name]
    return camera_object.name
    #object = bpy.ops.object.camera_add(location=location, rotation=rotation_euler)
    #bpy.context.scene.camera = bpy.context.object
    #object.name = object_name
    #return object.name
    
    
def create_light(energy=100000, location=(0,0,0), type='POINT', *, object_name='Light'):
    light_data = bpy.data.lights.new(name=object_name + "-data", type=type)        
    light_data.energy = energy
    object = bpy.data.objects.new(name=object_name, object_data=light_data)
    object.name = object_name
    object.location = location
    bpy.context.collection.objects.link(object) # Link object to collection in context
    return object.name
    
    
def create_sun(energy=100, location=(0,0,500), rotation_euler=(0,0,0), *, object_name='Sun'):
    sun_name = create_light(energy=energy, location=location, type='SUN', object_name=object_name)
    set_attribute(sun_name, 'rotation_euler', rotation_euler)
    return sun_name
        
           
def create_color_material(color, specular_intensity=1, *, material_name='new_colored_material'):

    # Create a material
    material = bpy.data.materials.new(material_name)

    material.specular_intensity = specular_intensity

    # Activate its nodes
    material.use_nodes = True

    # Get the principled BSDF (created by default)
    principled = material.node_tree.nodes['Principled BSDF']

    # Assign the color
    principled.inputs['Base Color'].default_value = color

    return material
    
    
def append_material(object_name, material):
    get_object(object_name).data.materials.append(material)
        

def paint_color(object_name, color, specular_intensity=1):
    material = create_color_material(color, specular_intensity)
    append_material(object_name, material)
    
 
def add_plane(size=1,
        *, location=(0,0,0), object_name='Plane'):
    bpy.ops.mesh.primitive_plane_add(
        enter_editmode=False,
        size=size,
        align='WORLD',
        location=location,
        )
    object = bpy.context.selected_objects[0]
    object.name = object_name
    return object.name
    
    
def create_cylinder(radius=1, depth=1,
        *, object_name='Cylinder', location=(0,0,0),
        color=None, specular_intensity=1):
    bpy.ops.mesh.primitive_cylinder_add(enter_editmode=False,
        align='WORLD', radius=radius, depth=depth)
    object = bpy.context.selected_objects[0]
    object.name = object_name
    object.location = location
    if color: paint_color(object.name, color, specular_intensity)
    return object.name


def create_rectangle(dimensions=(1,1,1),
        *, object_name='Rectangle', location=(0,0,0), rotation_euler=(0,0,0),
        color=None, specular_intensity=1):
    length_infinitesimal = 0.01
    bpy.ops.mesh.primitive_cube_add(
        enter_editmode=False,
        size=length_infinitesimal,
        align='WORLD',
        scale=[d / length_infinitesimal for d in dimensions],
        )
    object = bpy.context.selected_objects[0]
    object.name = object_name
    object.rotation_euler = rotation_euler
    object.location = location
    if color: paint_color(object.name, color, specular_intensity)
    return object.name
    
    
def group_objects(object_names):
    ctx = bpy.context.copy()
    object = get_object(object_names[0])
    ctx['active_object'] = object
    ctx['selected_editable_objects'] = [get_object(n) for n in object_names]
    bpy.ops.object.join(ctx)
    return object.name


def create_lane_on_floor(coords2D,
        *, wide=1., thick=.1, color=None, specular_intensity=1, object_name='Lane'):
    
    circle_radius = float(wide) / 2
    
    path_object_names = []
    
    material_lane = create_color_material(color, specular_intensity)
            
    for p, (point1, point2) in enumerate(zip(coords2D[:-1], coords2D[1:])):
        
        point1 = [float(p) for p in point1]
        point2 = [float(p) for p in point2]
        
        if p > 0:
            cylinder_name = create_cylinder(
                object_name = 'Path_Circle.' + str(p).zfill(3),
                radius = circle_radius, depth = thick,
                location = (point1[0], point1[1], 0))
                
            append_material(cylinder_name, material_lane)
                        
            path_object_names.append(cylinder_name)
            
        
        line_length = math.dist(point1, point2)
        
        # create rectangle object
        heading = math.atan2(point2[1] - point1[1], point2[0] - point1[0])
        rect_center = [(float(c1) + float(c2)) / 2. for c1, c2 in zip(point1, point2)]
        
        rectangle_name = create_rectangle(
            object_name = 'Path_Rect.' + str(p).zfill(3),
            dimensions = (line_length, wide , thick * 1.5),
            location = (rect_center[0], rect_center[1], 0),
            rotation_euler = (0, 0, heading))
                
        append_material(rectangle_name, material_lane)
        
        if p > 0:
            # remove undesired dark artifacts created at rectangle intersections
            bpy.ops.object.modifier_add(type='BOOLEAN')
            previous_rectangle_name = path_object_names[-2]
            bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[previous_rectangle_name]
            bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
            
        path_object_names.append(rectangle_name)


    return path_object_names
        
    #group_objects(path_object_names) #BUG: grouping removes Boolean, so dark artifacts reappear
    
    #object.name = object_name
        
    #return object.name
        
        
def setup_animation(frame_end=3, fps=10, *, frame_start=0):
    bpy.context.scene.render.fps = fps    
    bpy.data.scenes['Scene'].frame_start = frame_start
    bpy.data.scenes['Scene'].frame_end = frame_end
    bpy.data.scenes['Scene'].frame_current = bpy.data.scenes['Scene'].frame_start
    
    
def add_keyframe_sequence(object_name, attribute, frames_values):
    """Add sequence of keyframes to an object"""
    object = get_object(object_name)
    for f, v in frames_values.items():
        setattr(object, attribute, v)
        object.keyframe_insert(data_path=attribute, frame=f)


def import_fbx(filepath,
        *, object_name='MyNewObject', location=(0,0,0), rotation_euler=(0,0,0), scale=(1,1,1)):
    bpy.ops.import_scene.fbx(filepath=filepath)
    bpy.ops.transform.resize(value=scale)
    object = bpy.context.selected_objects[0]  
    object.animation_data_clear() #delete animations
    object.rotation_euler = rotation_euler
    object.location = location
    object.name = object_name
    return object.name


def import_obj(filepath):  
    status = bpy.ops.import_scene.obj(filepath=filepath)
    object_names = [o.name for o in bpy.context.selected_objects]
    return object_names
    
    
def render_animation(filename):
    output_path = bpy.context.scene.render.filepath
    output_filename = os.path.join(output_path, filename + ".mp4")
    bpy.context.scene.render.filepath = output_filename
    try:
        bpy.ops.render.render(animation=True, write_still=True )
    except:
        print('Failed rendering', output_filename)        
    
    bpy.context.scene.render.filepath = output_path
    