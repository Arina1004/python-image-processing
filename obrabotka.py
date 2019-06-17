import json
from PIL import Image, ImageDraw,ImageFilter
import math
import copy
import numpy as np

def load_model(file):
  with open(file) as model:
    data = json.load(model)

    width, height = normalize(data)

    return data, width, height

def normalize(data):
  min_x = data[0]['points'][0]['x']
  min_y = data[0]['points'][0]['y']
  max_x = data[0]['points'][0]['x']
  max_y = data[0]['points'][0]['y']

  for polygon in data:
    for point in polygon['points']:
      min_x = min(min_x, point['x'])
      max_x = max(max_x, point['x'])

      min_y = min(min_y, point['y'])
      max_y = max(max_y, point['y'])

  for polygon in data:
    for point in polygon['points']:
      point['x'] -= min_x
      point['y'] -= min_y

  return max_x - min_x, max_y - min_y


def scale_model(data, scale_factor):
  scaled_model = copy.deepcopy(data)
  for polygon in scaled_model:
    for point in polygon['points']:
      point['x'] = math.floor(point['x'] * scale_factor[0])
      point['y'] = math.floor(point['y'] * scale_factor[1])

  return scaled_model

def draw(model, model_width, model_height, width, height, angle):
  angle = math.radians(angle)
  scale_factor = [float(width) / float(model_width), float(height) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)

  blank_img = Image.new('RGB', (width, height), (255, 255, 255))
  draw = ImageDraw.Draw(blank_img)
  half_width=width/2
  half_height=height/2
  for polygon in scaled_model:
    points = map(lambda x: ((math.floor((half_width+(x['x']-half_width)*math.cos(angle)+(x['y']-half_height)*math.sin(angle))),
    math.floor((half_height-1*(x['x']-half_width)*math.sin(angle)+(x['y']-half_height)*math.cos(angle))))),
    polygon['points'])
    color = (255, 255, 255) if polygon['transparent'] else (0, 0, 0)

    draw.polygon(points, color)

  blank_img.save('./draw/tmp.png', 'png')

def rotate(model, model_width, model_height, width, height, angle):
  angle = math.radians(angle)
  scale_factor = [float(width) / float(model_width), float(height) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)

  half_width=width/2
  half_height=height/2
  mas = []
  for polygon in scaled_model:
    color = 255 if polygon['transparent'] else 0
    points = map(lambda x: ((math.floor((half_width+(x['x']-half_width)*math.cos(angle)+(x['y']-half_height)*math.sin(angle))),
    math.floor((half_height-1*(x['x']-half_width)*math.sin(angle)+(x['y']-half_height)*math.cos(angle)))),color),
    polygon['points'])
    mas += points
    # mas=[((x,y),color),((x,y),color),((x,y),color),((x,y),color)]
  return mas

def filter(im):
  im = im.convert("L")
  im2 = Image.new("L",im.size,255)
  temp = {}
  for x in range(im.size[1]):
    for y in range(im.size[0]):
      pix = im.getpixel((y,x))
      temp[pix] = pix
      if pix < 195:
        im2.putpixel((y,x),0)
  im2.save("./tmp2.png")
  return im2

def find_edge_x(img):
  inletter = False
  foundletter=False
  start = 0
  end = 0
  letters = []
  for y in range(img.size[0]):
    for x in range(img.size[1]):
      pix = img.getpixel((y,x))
      if pix != 255:
        inletter = True
    if foundletter == False and inletter == True:
      foundletter = True
      start = y

    if foundletter == True and inletter == False:
      foundletter = False
      end = y
      letters.append((start,end))

    inletter=False
  return letters

def find_edge_y(img):
  inletter = False
  foundletter=False
  start = 0
  end = 0
  letters = []
  for x in range(img.size[1]):
    for y in range(img.size[0]):
      pix = img.getpixel((y,x))
      if pix != 255:
        inletter = True
    if foundletter == False and inletter == True:
      foundletter = True
      start = x

    if foundletter == True and inletter == False:
      foundletter = False
      end = x
      letters.append((start,end))

    inletter=False
  return letters

def crop_x(img, letters):
  count = 0
  for letter in letters:
    im2 = img.crop(( letter[0] , 0, letter[1],img.size[1] ))
    letters_y = find_edge_y(im2)
    im2 = crop_y(im2,letters_y)
    im2.save("./numbers/"+str(count)+".png")
    count += 1

def crop_y(img, letters):
  im2=img
  for letter in letters:
    im2 = img.crop(( 0 , letter[0], img.size[0],letter[1] ))
  return im2

def alg(img):
  im=filter(img)
  letters_x = find_edge_x(im)
  crop_x(im,letters_x)
  numbers =[]
  for number in range(2):
    image = Image.open('./numbers/'+str(number)+'.png')
    # image = image.resize((200*image.size[0],200*image.size[1]))
    overlap=[]
    for number_model in range(10):
      model, model_width, model_height = load_model('./models/'+str(number_model)+'.json')
      max_count = 0
      for angle  in range(-30,31):
        count = 0
        count_2 = 0
        rotate_image=rotate(model, model_width, model_height, image.size[0], image.size[1],angle)
        # rotate_image=[((x,y),color),((x,y),color),((x,y),color),((x,y),color)]
        for pixel in rotate_image:
          if pixel[0][0] > 0 and pixel[0][0] < image.size[0] and pixel[0][1] > 0 and pixel[0][1] < image.size[1]:
            count = count+1 if image.getpixel(pixel[0]) == pixel[1] and pixel[1] == 0 else count
            count_2 = count_2 + 1 if image.getpixel(pixel[0]) == 0 or pixel[1] == 0 else count_2
        max_count = float(count)/float(count_2) if float(count)/float(count_2) > max_count else max_count
      overlap.append(max_count)
    numbers.append(overlap.index(max(overlap)))
    print(overlap)
  print(numbers)


original_im = Image.open('./tmp.png')
# original_im = original_im.resize((10*original_im.size[0],10*original_im.size[1]))
alg(original_im)
original_im = Image.open('./numbers/1.png')
model, model_width, model_height = load_model('./models/2.json')
draw(model, model_width, model_height, original_im.size[0],original_im.size[1],15)
def draw2(model, model_width, model_height, width, height, angle):
  angle = math.radians(angle)
  scale_factor = [float(10) / float(model_width), float(15) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)

  blank_img = Image.new('RGB', (width, height), (255, 255, 255))
  draw = ImageDraw.Draw(blank_img)

  half_width=40/2
  half_height=15/2
  scale_factor = [float(10) / float(model_width), float(15) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)
  for polygon in scaled_model:
    points = map(lambda x: ((math.floor((half_width+(x['x']-half_width)*math.cos(angle)+(x['y']-half_height)*math.sin(angle))),
    math.floor((half_height-1*(x['x']-half_width)*math.sin(angle)+(x['y']-half_height)*math.cos(angle))))),
    polygon['points'])
    color = (255, 255, 255) if polygon['transparent'] else (0, 0, 0)

    draw.polygon(points, color)
  model, model_width, model_height = load_model('./models/2.json')
  angle = math.radians(15)
  half_width=40/2
  half_height=-160/2
  scale_factor = [float(14) / float(model_width), float(17) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)
  for polygon in scaled_model:
    points = map(lambda x: ((math.floor((half_width+(x['x']-half_width)*math.cos(angle)+(x['y']-half_height)*math.sin(angle))),
    math.floor((half_height-1*(x['x']-half_width)*math.sin(angle)+(x['y']-half_height)*math.cos(angle))))),
    polygon['points'])
    color = (255, 255, 255) if polygon['transparent'] else (0, 0, 0)

    draw.polygon(points, color)

  blank_img.save('./tmp.png', 'png')
model, model_width, model_height = load_model('./models/1.json')
draw2(model, model_width, model_height, 145,26,30)