import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import time
import random
import carla
import random
import cv2
import numpy as np

#camera parameters
IM_WIDTH = 640
IM_HEIGHT = 480

def process_img(image):
        i = np.array(image.raw_data)                #raw data is a flat array
        i2 = i.reshape((IM_HEIGHT,IM_WIDTH, 4))     #we reshape into an 2D image
        i3 = i2[:, :, :3]                           #get the x, y, and first 3 channels (RGB)
        cv2.imshow('', i3)                          #display image using opencv
        cv2.waitKey(1)
        return i3 / 255.0                           #value returned as normalized

class CarlaTemp():

    #class responsable for:
    #    -spawning 1 vehicle
    #    -destroy the created objects
    #    -execute manuvers

    def __init__(self):
        #construct object CarlaTemp with server connection
        client = carla.Client('localhost', 2000)
        client.set_timeout(6)
        self.world = client.get_world()
        self.actor_list = []
        blueprint_library = self.world.get_blueprint_library()

        #retrieve our vehicle, set spawn point
        bp = blueprint_library.filter('model3')[0]
        spawn_point = random.choice(self.world.get_map().get_spawn_points())

        #spawn vehicle
        self.vehicle = self.world.spawn_actor(bp, spawn_point)
        self.actor_list.append(self.vehicle)

        #setup a camera
        self.cam_bp = blueprint_library.find('sensor.camera.rgb')
        self.cam_bp.set_attribute('image_size_x', f'{IM_WIDTH}')
        self.cam_bp.set_attribute('image_size_y', f'{IM_HEIGHT}')
        self.cam_bp.set_attribute('fov', '110')

        #spawn camera, spawn_point based on relative positioning
        spawn_point = carla.Transform(carla.Location(x=-5, y=0, z=2)) #orientation relative to car: x=forward/back, y=left/right z=up/down
        self.sensor = self.world.spawn_actor(self.cam_bp, spawn_point, attach_to=self.vehicle)
        self.actor_list.append(self.sensor)

        #the following command actually can be used to gather sensor data:
        self.sensor.listen(lambda data: process_img(data))

    def movement(self):
        #always perform this -> while condition is true
        while True:
            self.vehicle.apply_control(carla.VehicleControl(throttle=.5, steer=0.6, brake=0.0))
            time.sleep(2)
            #break if we randomly choose 0 out of numbers 0, 1, 2, 3
            if (random.randint(0,3) == 0):
                break

        #peform this conditionally -> while condition is true
        while (random.randint(0,3) != 0):
            self.vehicle.apply_control(carla.VehicleControl(throttle=.5, steer=0, brake=0.0, reverse=True))
            time.sleep(2)
        
        #always perform this, but only once
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
        time.sleep(0.5)
        return

    def destroy(self):
        #destroy all the actors
        print('destroying actors')
        for actor in self.actor_list:
            actor.destroy()
        print('done.')


    def run(self):
        #run movement block 5 times
        for i in range(5):
            self.movement()

# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    #Main function

    #create an instance of our simulation object
    simulation = CarlaTemp()
    try:
        simulation.run()

    finally:
        if simulation is not None:
            simulation.destroy()


if __name__ == '__main__':
    #try:
    main()
    #except:
        #pass