import imageio
import os
from natsort import natsorted

# filenames = listdir("output")

png_dir = "output/frames"
images = []
for file_name in natsorted(os.listdir(png_dir)):
    if file_name.endswith(".png"):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave("output/keygroups.gif", images)
imageio.mimsave("output/keygroups.mp4", images)

# Remove files
# for filename in set(filenames):
#     os.remove(filename)
