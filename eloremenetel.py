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
import carla

import random
import time
import numpy as np
import cv2

import pygame

#IM_WIDTH = 640
#IM_HEIGHT = 480

# Global functions

pygame.init()

display = pygame.display.set_mode(
    (640, 480),
    pygame.HWSURFACE | pygame.DOUBLEBUF)

def process_img(image):
    #image.save_to_disk('output/%06d.png' % image.frame)


    #egy lehetseges feldolgozas lehetne: 

    i = np.array(image.raw_data)
    i2 = i.reshape((480, 640, 4))
    i3 = i2[:, :, :3]


    surface = pygame.surfarray.make_surface(i3)
    display.blit(surface, (0,0))
    pygame.display.flip()


    #cv2.imshow("", i3)
    #cv2.waitKey(1)
    return i3/255


actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]   # Tesla Model3
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())   # random spawn point

    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))   # arra utasítjuk egyelőre, hogy csak menjen előre

    actor_list.append(vehicle)

    # kamera 
    blueprint = blueprint_library.find('sensor.camera.rgb')
    # kamera tulajdonsagainak beallitasa
    blueprint.set_attribute('image_size_x', '640')
    blueprint.set_attribute('image_size_y', '480')
    blueprint.set_attribute('fov', '110')
    # kamera elhelyezes a kocsin
    spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))

    sensor = world.spawn_actor(blueprint, spawn_point, attach_to=vehicle)

    actor_list.append(sensor)

    # kimentjük a képeket png fileokba
    #sensor.listen(lambda data: process_img(data))

    sensor.listen(lambda data: process_img(data))
    
    time.sleep(15)


finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')