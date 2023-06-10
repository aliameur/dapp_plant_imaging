import gphoto2 as gp
camera = gp.Camera()
camera.init()
text = camera.get_summary()

t = camera.get_config()
print('Summary')
print('=======')
print(str(text))
camera.exit()

gp.gp_camera_get_config
