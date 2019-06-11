import json
from PIL import Image, ImageDraw,ImageFilter
import cv2 as cv
import math
import copy
import numpy as np
import hashlib
import time

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

def draw(model, model_width, model_height, width, height):
  scale_factor = [float(width) / float(model_width), float(height) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)

  # print(scale_factor)
  # print(scaled_model[0]['points'])

  blank_img = Image.new('RGB', (width, height), (255, 255, 255))
  draw = ImageDraw.Draw(blank_img)

  for polygon in scaled_model:
    points = map(lambda x: (x['x'], x['y']), polygon['points'])
    color = (255, 255, 255) if polygon['transparent'] else (0, 0, 0)

    draw.polygon(points, color)


  blank_img.save('./tmp.png', 'png')

def filter(im):
  im = im.convert("L")
  im2 = Image.new("L",im.size,255)

  im = im.convert("L")

  temp = {}

  for x in range(im.size[1]):
    for y in range(im.size[0]):
      pix = im.getpixel((y,x))
      temp[pix] = pix
      if pix < 180:
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
  count = 0
  for letter in letters:
    print(letter[0],letter[1])
    im2 = img.crop(( 0 , letter[0], img.size[0],letter[1] ))
    count += 1
  return im2

model, width, height = load_model('./models/3.json')
draw(model, width, height, 100, 100)
original_im = Image.open('./example/3.png')
im=filter(original_im)
letters_x = find_edge_x(im)
crop_x(im,letters_x)
