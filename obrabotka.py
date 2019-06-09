import json
from PIL import Image, ImageDraw
import math
import copy

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
  print(model_width, width, model_height, height)
  print(float(width) / float(model_width))
  scale_factor = [float(width) / float(model_width), float(height) / float(model_height)]
  scaled_model = scale_model(model, scale_factor)

  print(scale_factor)
  print(scaled_model[0]['points'])

  blank_img = Image.new('RGB', (width, height), (255, 255, 255))
  draw = ImageDraw.Draw(blank_img)

  for polygon in scaled_model:
    points = map(lambda x: (x['x'], x['y']), polygon['points'])
    color = (255, 255, 255) if polygon['transparent'] else (0, 0, 0)

    draw.polygon(points, color)


  blank_img.save('./tmp.png', 'png')

model, width, height = load_model('./models/1.json')
draw(model, width, height, 100, 100)


