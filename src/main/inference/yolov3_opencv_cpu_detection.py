import os
import cv2
import jsonschema
import asyncio
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from inference.base_inference_engine import AbstractInferenceEngine
from inference.exceptions import InvalidModelConfiguration, InvalidInputData, ApplicationError


class InferenceEngine(AbstractInferenceEngine):

	def __init__(self, model_path):
		self.net = None
		self.scale = None
		self.image_width = None
		self.image_height = None
		self.swapRB = None
		self.crop = None
		self.R_mean = None
		self.G_mean = None
		self.B_mean = None
		self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
		super().__init__(model_path)

	def load(self):
		with open(os.path.join(self.model_path, 'config.json')) as f:
			data = json.load(f)
		try:
			self.validate_json_configuration(data)
			self.set_model_configuration(data)
		except ApplicationError as e:
			raise e

		with open(os.path.join(self.model_path, 'obj.names'), 'r') as f:
			self.labels = [line.strip() for line in f.readlines()]
		self.net = cv2.dnn.readNet(os.path.join(self.model_path, 'yolo-obj.cfg'),
								   os.path.join(self.model_path, 'yolo-obj.weights'))

	async def infer(self, input_data, draw, predict_batch):
		await asyncio.sleep(0.00001)
		try:
			pillow_image = Image.open(input_data.file).convert('RGB')
			np_image = np.array(pillow_image)
		except Exception as e:
			raise InvalidInputData('corrupted image')
		try:
			with open(self.model_path + '/config.json') as f:
				data = json.load(f)
		except Exception as e:
			raise InvalidModelConfiguration('config.json not found or corrupted')
		conf_threshold = data['confidence']
		nms_threshold = data['nms_threshold']
		height, width, depth = np_image.shape
		# create input blob
		blob = cv2.dnn.blobFromImage(
			np_image, self.scale, (self.image_width, self.image_height), (self.R_mean, self.G_mean, self.B_mean),
			self.swapRB, self.crop)
		# feed the blob to the network
		self.net.setInput(blob)
		# get the output layers
		output_layers = self.net.forward(self.__get_output_layers__())
		# for each detection from each output layer
		# get the confidence, class id, bounding box params
		# and ignore detections below threshold
		boxes = []
		class_ids = []
		confidences = []
		for layer in output_layers:
			for detection in layer:
				scores = detection[5:]
				class_id = np.argmax(scores)
				confidence = scores[class_id]
				if confidence * 100 > conf_threshold:
					center_x = int(detection[0] * width)
					center_y = int(detection[1] * height)
					w = int(detection[2] * width)
					h = int(detection[3] * height)
					x = center_x - w / 2
					y = center_y - h / 2
					class_ids.append(int(class_id))
					confidences.append(float(confidence * 100))
					boxes.append([x, y, w, h])

		# apply non-max suppression to remove duplicate bounding boxes for same object
		remaining_indices = cv2.dnn.NMSBoxes(
			boxes, confidences, conf_threshold, nms_threshold)

		for i in range(len(boxes)):
			# i = i[0]
			box = boxes[i]
			x = box[0]
			y = box[1]
			w = box[2]
			h = box[3]

		# release resources
		cv2.destroyAllWindows()

		# return the remaining boxes
		output_bboxes = []
		for i in remaining_indices:
			box = boxes[i[0]]
			output_bboxes.append(
				{
					'ObjectClassName': self.labels[class_ids[i[0]]],
					'ObjectClassId': class_ids[i[0]],
					'confidence': confidences[i[0]],
					'coordinates': {
						'left': int(box[0]),
						'right': int(box[0]) + int(box[2]),
						'top': int(box[1]),
						'bottom': int(box[1]) + int(box[3])
					}
				}
			)
		if predict_batch:
			response = dict([('bounding-boxes', output_bboxes), ('ImageName', input_data.filename)])
		else:
			response = dict([('bounding-boxes', output_bboxes)])
		if not draw:
			return response
		else:
			try:
				self.draw_image(pillow_image, response)
			except ApplicationError as e:
				raise e
			except Exception as e:
				raise e

	async def run_batch(self, input_data, draw, predict_batch):
		result_list = []
		for image in input_data:
			post_process = await self.infer(image, draw, predict_batch)
			if post_process is not None:
				result_list.append(post_process)
		return result_list

	def draw_image(self, image, response):
		"""
		Draws on image and saves it.
		:param image: image of type pillow image
		:param response: inference response
		:return:
		"""
		draw = ImageDraw.Draw(image)
		for bbox in response['bounding-boxes']:
			draw.rectangle([bbox['coordinates']['left'], bbox['coordinates']['top'], bbox['coordinates']['right'],
							bbox['coordinates']['bottom']], outline="red")
			left = bbox['coordinates']['left']
			top = bbox['coordinates']['top']
			conf = "{0:.2f}".format(bbox['confidence'])
			draw.text((int(left), int(top) - 20), str(conf) + "% " + str(bbox['ObjectClassName']), 'red', self.font)
		image.save('/main/result.jpg', 'PNG')

	def __get_output_layers__(self):
		layer_names = self.net.getLayerNames()
		output_layers = [layer_names[i[0] - 1]
						 for i in self.net.getUnconnectedOutLayers()]
		return output_layers

	def free(self):
		pass

	def validate_configuration(self):
		# check if network architecture file exists
		if not os.path.exists(os.path.join(self.model_path, 'yolo-obj.cfg')):
			raise InvalidModelConfiguration('yolo-obj.cfg not found')
		# check if weights file exists
		if not os.path.exists(os.path.join(self.model_path, 'yolo-obj.weights')):
			raise InvalidModelConfiguration('yolo-obj.weights not found')
		# check if labels file exists
		if not os.path.exists(os.path.join(self.model_path, 'obj.names')):
			raise InvalidModelConfiguration('obj.names not found')
		return True

	def set_model_configuration(self, data):
		self.configuration['framework'] = data['framework']
		self.configuration['type'] = data['type']
		self.configuration['network'] = data['network']
		self.image_width = data['image']['width']
		self.image_height = data['image']['height']
		self.scale = data['image']['scale']
		self.swapRB = data['image']['swapRB']
		self.crop = data['image']['crop']
		self.R_mean = data['image']['mean']['R']
		self.G_mean = data['image']['mean']['G']
		self.B_mean = data['image']['mean']['B']

	def validate_json_configuration(self, data):
		with open(os.path.join('inference', 'ConfigurationSchema.json')) as f:
			schema = json.load(f)
		try:
			jsonschema.validate(data, schema)
		except Exception as e:
			raise InvalidModelConfiguration(e)
