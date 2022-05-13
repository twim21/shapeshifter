import json
from shapely.geometry import Point, Polygon
from shapely import affinity
from PIL import Image, ImageDraw
import random
import numpy as np
import glob
import matplotlib

colorlist = list(matplotlib.colors.CSS4_COLORS.keys())
# print(matplotlib.colors.CSS4_COLORS)
# exit()

#backgrounds
background_path = ".\\backgrounds"
defect_path = ".\\defects"
shrink_ratio = 2
grow_ratio = 5
num_images = 10000
min_defect_per_image = 2
max_defect_per_image = 5
defects_names = ['crack', 'random', 'hole', 'moe', 'trash', 'Moe']
save_location = ".\\output_images"
defect_color_scheme = {}



for num, value in enumerate(defects_names):
    defect_color_scheme[value] = colorlist[num*3]

# colors = {'crack':, 'random':, 'hole':, 'moe':, 'trash':, 'Moe':}



def find_filenames():
    background_filenames = []
    defect_filenames = []
    for element in glob.glob(background_path + "\\*.json"):
        background_filenames.append(element.split(".json")[0])

    for element in glob.glob(defect_path + "\\*.json"):
        defect_filenames.append(element.split(".json")[0])


    return background_filenames, defect_filenames

def parse_file(file, areas, defects):
    with open(file + ".json", "r") as f:
        reader = json.load(f)
        polygons_dict = {}
        counter = 0
        shapes_arr = reader["shapes"]
        imagepath = reader["imagePath"]


        for polygon in shapes_arr:
            label = polygon["label"]
            points = polygon["points"]
            shape = Polygon(points)



            if len(label.split("_")) < 2:
                #background
                if label in areas.keys():
                    areas[label].append(shape)
                    areas["imagePath"] = imagepath
                else:
                    areas[label] = [shape]
            else:
                if label in defects.keys():
                    defects[label].append(shape)
                else:
                    defects[label] = [shape]

        return areas, defects


def go_fetch():
    areas, defects = find_filenames()
    defect_dict = {}
    area_dict = {}


    for file in defects:
        area_dict, defect_dict = parse_file(file, area_dict, defect_dict)



    for file in areas:
        one_background = {}
        one_background, defect_dict = parse_file(file, one_background, defect_dict)
        area_dict[file] = one_background

    return area_dict, defect_dict

area_dict, defect_dict = go_fetch()

# print(area_dict.keys())
# print(area_dict.values())
#
print("------------")
print(defect_dict.keys())
print(defect_dict.values())


def image_factory(area_dict, defect_dict, num_images):
    # counter = num_images
    while num_images != 0:
        print("hi")
        random_background = area_dict[random.choice(list(area_dict))].copy()
        base_shape = random_background.pop("product")[0]
        imagePath = random_background.pop("imagePath")
        # random_background
        current_areas = random_background.keys()
        print(current_areas)
        print(base_shape)
        print(imagePath)
        # exit()

        pool = set()
        for key in defect_dict.keys():
            splitlist = key.split("_")
            for element in splitlist:
                if element in current_areas:
                    print(element)
                    pool.add(key)



        defects_counter = random.randint(min_defect_per_image, max_defect_per_image + 1)
        img = Image.open(background_path + "\\" + imagePath)
        dimensions = img.size
        canvas = Image.new("RGB", size=dimensions)
        tempcanvas = ImageDraw.Draw(canvas)
        shipping_main = list(zip(*base_shape.exterior.coords.xy))
        tempcanvas.polygon(shipping_main, fill="green")

        while defects_counter > 0:
            defect_name = random.choice(list(pool))
            defect_shape = random.choice(defect_dict[defect_name])

            flag = False
            while not flag:
                try:
                    defect_location_name = random.choice(defect_name.split("_")[:-1])
                    defect_location = random.choice(random_background[defect_location_name])
                    flag = True
                except Exception:
                    pass


            area_center = defect_location.centroid
            scaled_x = random.uniform(shrink_ratio, grow_ratio)
            scaled_y = random.uniform(shrink_ratio, grow_ratio)

            scaled_shape = affinity.scale(defect_shape, xfact=scaled_x, yfact=scaled_y)
            rotated_and_scaled = affinity.rotate(scaled_shape, random.randint(0,360))

            x_distance = random.randint(-1*dimensions[0], dimensions[0])
            y_distance = random.randint(-1*dimensions[1], dimensions[1])

            random_movement = affinity.translate(rotated_and_scaled, x_distance, y_distance)
            counter = 0
            while defect_location.contains(random_movement) == False:
                if counter == 10:
                    counter = 0

                    scaled_x = random.uniform(0, 1)
                    scaled_y = random.uniform(0, 1)
                    print("resizing...", scaled_x, scaled_y)
                    x_distance = random.randint(-1 * dimensions[0], dimensions[0])
                    y_distance = random.randint(-1 * dimensions[1], dimensions[1])

                    scaled_shape = affinity.scale(defect_shape, xfact=scaled_x, yfact=scaled_y)
                    random_movement = affinity.translate(scaled_shape, x_distance, y_distance)
                main_center = np.array(area_center)
                object_center = np.array(random_movement.centroid)

                x_offset = main_center[0] - object_center[0]
                y_offset = main_center[1] - object_center[1]
                if x_offset < 0:
                    x_distance = -1 * random.randint(0, int(-1 * x_offset))
                else:
                    x_distance = random.randint(0, int(x_offset))

                if y_offset < 0:
                    y_distance = -1 * random.randint(0, int(-1 * y_offset))
                else:
                    y_distance = random.randint(0, int(y_offset))

                random_movement = affinity.translate(random_movement, x_distance, y_distance)
                counter +=1
            random_movement = random_movement.intersection(defect_location)


            defects_counter -=1
            # print(defect_name)
            print(defect_color_scheme[defect_name.split("_")[-1]])
            tempcanvas.polygon(list(zip(*random_movement.exterior.coords.xy)), defect_color_scheme[defect_name.split("_")[-1]])
        canvas.save(save_location + "\\segmentation_%s.png" %num_images)
        canvas.close()
        # canvas.show()
        num_images -=1
            # print("------------------")
            # print(defect_name)
            # print(defect_location_name)
            # print(defect_shape)
            # print(defect_location)
            # exit()






        # print(pool)
        # exit()

image_factory(area_dict, defect_dict, num_images)




        # tempcanvas = ImageDraw.Draw(canvas)
        # shipping_main = list(zip(*main_product.exterior.coords.xy))
        # tempcanvas.polygon(shipping_main, fill="green")
        # # canvas.show()
        # # exit()
        # main_center = main_product.centroid
        # for key in polygons_dict.keys():
        #     center = polygons_dict[key].centroid
        #     scaled_x = random.uniform(shrink_ratio, grow_ratio)
        #     scaled_y = random.uniform(shrink_ratio, grow_ratio)
        #
        #     scaled_shape = affinity.scale(polygons_dict[key], xfact=scaled_x, yfact=scaled_y)
        #     rotated_and_scaled = affinity.rotate(scaled_shape, random.randint(0, 360))
        #
        #     x_distance = random.randint(-1 * dimensions[0], dimensions[0])
        #     y_distance = random.randint(-1 * dimensions[1], dimensions[1])
        #     # print(x_distance)
        #     random_movement = affinity.translate(rotated_and_scaled, x_distance, y_distance)
        #
        #     while main_product.contains(random_movement) == False:
        #
        #         # for x,y in main_center:
        #         #     print(x)
        #         #     print(y)
        #         main_center = np.array(main_center)
        #         object_center = np.array(random_movement.centroid)
        #
        #         x_offset = main_center[0] - object_center[0]
        #         y_offset = main_center[1] - object_center[1]
        #         print(x_offset)
        #         print(y_offset)
        #         if x_offset < 0:
        #             x_distance = -1 * random.randint(0, int(-1 * x_offset))
        #         else:
        #             x_distance = random.randint(0, int(x_offset))
        #
        #         if y_offset < 0:
        #             y_distance = -1 * random.randint(0, int(-1 * y_offset))
        #         else:
        #             y_distance = random.randint(0, int(y_offset))
        #
        #         random_movement = affinity.translate(random_movement, x_distance, y_distance)
        #
        #         # center_distances = main_center.distance(random_movement)
        #         # print(center_distances)
        #         # canvas.show()
        #     # if main_product.contains(random_movement):
        #     #     defect_drawing = list(zip(*rotated_and_scaled.exterior.coords.xy))
        #     #     tempcanvas.polygon(defect_drawing, fill="red")
        #     tempcanvas.polygon(list(zip(*random_movement.exterior.coords.xy)), "red")
        #     canvas.show()










# quit()




with open("30__0__.json", "r") as f:


        exit()