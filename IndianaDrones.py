import math
import os
import mathutils

import bpy

def getLocalFolder():
    path = str(os.path.dirname(os.path.abspath(__file__))).split(os.sep)
    return (os.sep).join(path[:len(path)-1])

import sys
sys.path.append(getLocalFolder())

import mybpy

from importlib import reload  # Python 3.4+
mybpy = reload(mybpy)

import json


class IndianaDrones:
    
    def __init__(self):
        
        self.local_folder = 'C:\\Users\\Shadow\\Documents\\Blender Indiana Drones\\'
        self.trees_filepath = self.local_folder + '\\Trees\\trees9.obj'
        
        self.robot_filepath = self.local_folder + 'DRON 001.fbx'
        self.robot_name = 'Robot'
        self.robot_high = 3.2
        self.robot_frames_rotation = 3
        self.robot_frames_translation = 10
        self.robot_frames_total = self.robot_frames_rotation + self.robot_frames_translation
        
        self.camera_name = 'Camera'
        self.camera_rotation_euler = (0, 0, 0)
        self.camera_location = (35, -10, 250)
#        self.camera_rotation_euler = (0.3, 0, 0.3)
#        self.camera_location = (50, -80, 250)
#        self.camera_rotation_euler = (mybpy.degree2radians(83), 0, mybpy.degree2radians(75))
#        self.camera_location = (150, -39.5, 21)
        
        self.sun_name = 'Sun'
        self.sun_energy = 1
        self.sun_location = (0, 0, 5000)
        self.sun_rotation_euler = (0,.9,.9)
        
        self.diffuselight_name = 'Diffuse'
        self.diffuselight_energy = 1000000
        self.diffuselight_location = self.camera_location
        
        self.floor_name = 'Floor'
        self.floor_size = 250
        
        self.path_name = 'Path'
        self.path_wide = 3.
        self.path_thick = .1
        self.path_color = (0.8, 0.04, 0.04, 1)
        
        self.tree_letter_to_name = {
            'A': 'Bark___S',
            'C': 'Bottom_T',
            'D': 'Bark___0',
            'E': 'Sonnerat',
            'F': 'Bark___1',
            'G': 'Bark___0',
            'H': 'Walnut_L',
            'J': 'Sonnerat',
            'K': 'Sonnerat',
            'L': 'Oak_Leav',
            'M': 'Bottom_T',
            'N': 'Mossy_Tr',
            'O': 'Bark___S',
            'P': 'Bark___1',
            'Q': 'Bark___1',
            'R': 'Bark___0',
            'S': 'Mossy_Tr',
            'T': 'Bark___S',
            'U': 'Mossy_Tr',
            'V': 'Mossy_Tr',
        }        
        self.trees_origins = {
            'Bottom_T': ( 40,0,0),
            'Bark___1': ( 20,0,0),
            'Mossy_Tr': (  0,0,0),
            'Bark___0': (-10,0,0),
            'Walnut_L': (-20,0,0),
            'Bark___S': (-30,0,0),
            'Sonnerat': (-40,0,0),
            'Oak_Leav': (-50,0,0),
        }
        self.imported_trees_names = set()
        self.are_trees_imported()
        
        self.sim_filepath = self.local_folder + 'coordinates.json'
        self.sim_scale = 10.
        self.sim_fps = 10
        self.sim_data = None
        
        
    def create_camera(self):
        if not mybpy.is_object_in_scene(self.camera_name):
            self.camera_name = mybpy.create_camera(location=self.camera_location,
                rotation_euler=self.camera_rotation_euler, object_name=self.camera_name)
            
            
    def are_trees_imported(self):
        are_imported = False
        objects_in_scene = mybpy.get_all_objects_names()
        for o in objects_in_scene:
            if mybpy.get_object(o).hide_render == True:
                self.imported_trees_names.add(o)
                are_imported = True
            
        return are_imported
        

    def import_trees(self, force_import=False):
        
        if (force_import) or (not self.are_trees_imported()):
            
            self.imported_trees_names = set(mybpy.import_obj(self.trees_filepath))
                
            # hide all imported trees
            for imported_tree in self.imported_trees_names:
                mybpy.set_attribute(imported_tree, 'hide_viewport', True)
                mybpy.set_attribute(imported_tree, 'hide_render', True)
            
            # set every tree origin to zero location
            for tree_name, new_origin in self.trees_origins.items():
                tree_fullname = self.get_tree_fullname(tree_name)
                mybpy.get_object(tree_fullname).data.transform(
                    mathutils.Matrix.Translation(new_origin))
    
    
    def coords_to_location(self, coords, z=0):
        return [c for c in coords] + [z]
    
    
    def robot_coords_to_location(self, coords):
        return self.coords_to_location(coords, self.robot_high)


    def import_robot(self):
        if not mybpy.is_object_in_scene(self.robot_name):
            location = self.robot_coords_to_location([20, -10])
            heading = -30 * math.pi / 180
            self.robot_name = mybpy.import_fbx(self.robot_filepath, object_name=self.robot_name,
                location=location, rotation_euler=(0, math.pi/2, heading))
            
            
    def set_robot_position(self, coords, heading):
        location = self.robot_coords_to_location(coords)
        mybpy.set_attribute(self.robot_name, 'location', location)        
        mybpy.set_attribute(self.robot_name, 'rotation_euler', (0, math.pi/2, heading))
        
        
    def create_sun(self):
        if not mybpy.is_object_in_scene(self.sun_name):
            self.sun_name = mybpy.create_sun(energy=self.sun_energy, location=self.sun_location,
                rotation_euler=self.sun_rotation_euler, object_name=self.sun_name)
    
    
    def create_light(self):
        if not mybpy.is_object_in_scene(self.diffuselight_name):
            self.diffuselight_name = mybpy.create_light(energy=self.diffuselight_energy,
                location=self.diffuselight_location, object_name=self.diffuselight_name)
            print('self.diffuselight_name:', self.diffuselight_name)


    def create_floor(self):
        if not mybpy.is_object_in_scene(self.floor_name):
            self.floor_name = mybpy.add_plane(self.floor_size, object_name=self.floor_name)
        
        
    def load_objects(self, clear_objects=False):
        if clear_objects: mybpy.delete_all_objects()
        self.create_camera()
        self.create_floor()
        self.import_robot()
        self.create_sun()
        self.create_light()
        self.import_trees()
        
        
    def create_robot_translation(self, from_coords, to_coords):
        from_location = self.robot_coords_to_location(from_coords)
        to_location = self.robot_coords_to_location(to_coords)
        frames_locations = {self.robot_frames_rotation: from_location, 
            self.robot_frames_rotation + self.robot_frames_translation: to_location}
        mybpy.add_keyframe_sequence(self.robot_name, 'location', frames_locations)
        
        
    def create_robot_rotation(self, from_heading, to_heading):
        frames_rotations = {0: (0, math.pi/2, from_heading),
                            self.robot_frames_rotation:(0, math.pi/2, to_heading)}
        mybpy.add_keyframe_sequence(self.robot_name, 'rotation_euler', frames_rotations)
        

    def create_tree_appearance(self, tree_name):
        frames_locations = {0: True, 2: False}
        mybpy.add_keyframe_sequence(tree_name, 'hide_viewport', frames_locations)
        mybpy.add_keyframe_sequence(tree_name, 'hide_render', frames_locations)


    def create_path(self, coords2D = ((0, 0), (4, 0), (4, -4), (10, -10), (20, -10))):
        self.delete_path()
        return mybpy.create_lane_on_floor(coords2D, wide=self.path_wide,
            thick=self.path_thick, color=self.path_color, object_name=self.path_name)
            
            
    def delete_path(self):
        objects_in_scene = bpy.context.scene.objects.keys()
        for o in objects_in_scene:
            if 'Path_' in o: mybpy.delete_objects([o])
            
        
    def load_simulation(self):
        self.sim_data = []
        for line in open(self.sim_filepath, 'r'):
            new_sim_data = json.loads(line)
            
            # scale values from simulation to Blender scene 
            for sim_obj_name, sim_attrs in new_sim_data.items():
                if sim_obj_name == 'path':
                    for row in range(len(sim_attrs)):
                        new_sim_data['path'][row][0] *= self.sim_scale
                        new_sim_data['path'][row][1] *= self.sim_scale
                        
                else:
                    new_sim_data[sim_obj_name]['coordinates'][0] *= self.sim_scale
                    new_sim_data[sim_obj_name]['coordinates'][1] *= self.sim_scale
                    
                    if sim_obj_name != 'self':
                        new_sim_data[sim_obj_name]['radius'] *= self.sim_scale
                
            self.sim_data.append(new_sim_data)
            
        return len(self.sim_data)
            
            
    def get_tree_fullname(self, tree_partial_name):
        tree_fullname = None
        found_candidates = [t for t in self.imported_trees_names if tree_partial_name in t]
        if len(found_candidates) > 0: tree_fullname = found_candidates[0]
        return tree_fullname
            
            
    def get_tree_fullname_from_type(self, tree_type='A'):
        tree_name = self.tree_letter_to_name[tree_type]
        return self.get_tree_fullname(tree_name)
    
    
    def is_tree(self, object_name):
        is_tree = False
        for t in self.trees_origins.keys():
            if t in object_name:
                is_tree = True
                break
            
        return is_tree
    
    
    def delete_cloned_trees(self):
        for o in mybpy.get_all_objects_names():
            if (self.is_tree(o)) and (not mybpy.get_object(o).hide_render):
                mybpy.delete_objects([o])
            
            
    def set_trees_positions(self, sim_data):
        
        self.delete_cloned_trees()
        
        # create and position new trees
        for id, attrs in sim_data.items():
            is_tree = (id != 'self') and (id != 'path')
            if is_tree:
                coords = attrs['coordinates']
                tree_type = attrs['type']
                tree_fullname = self.get_tree_fullname_from_type(tree_type)
                cloned_tree = mybpy.clone_object(tree_fullname,
                    self.coords_to_location(coords))
                
                mybpy.set_attribute(cloned_tree, 'hide_viewport', False)
                mybpy.set_attribute(cloned_tree, 'hide_render', False)
        
        
    def create_animation(self, take=0):
        
        # load scenario
        if self.sim_data is None: self.load_simulation() # just in case forgot
        sim_data = self.sim_data[take]
        self.create_path(coords2D=sim_data['path'])
        robot_curr_coords = sim_data['self']['coordinates']
        self.set_robot_position(robot_curr_coords, sim_data['self']['heading'])
        self.set_trees_positions(sim_data)
        
        if take + 1 < len(self.sim_data):
            mybpy.setup_animation(frame_end=self.robot_frames_total, fps=self.sim_fps)
                
            # create robot animation
            robot_next_coords = self.sim_data[take + 1]['self']['coordinates']
            
            robot_next_heading = math.atan2(robot_next_coords[1] - robot_curr_coords[1],
                                            robot_next_coords[0] - robot_curr_coords[0])
            self.create_robot_rotation(sim_data['self']['heading'], robot_next_heading)
            
            self.create_robot_translation(robot_curr_coords, robot_next_coords)
        

def set_attribute(object_name, attribute, value):
    setattr(get_object(object_name), attribute, value)
      

id = IndianaDrones()

id.load_objects()
#id.load_objects(clear_objects=True)
#print('Loaded objects in scene')

##mybpy.delete_all_objects()
#id.create_camera()
###id.create_light()
###id.create_sun()
##id.create_floor()
##id.import_robot()
##id.import_trees()
####id.create_path()

number_takes = id.load_simulation()

#bpy.context.scene.render.filepath = os.path.join('C:', 'tmp')

for take in [0]:
#for take in range(1, number_takes):
    take_str = 'take_' + str(take).zfill(2)
    print('Rendering', take_str)
    
    id.create_animation(take)

#    mybpy.render_animation(take_str)


print('Render finished')
## measure, calculate_path, rotate, move
#mybpy.delete_all_objects()
