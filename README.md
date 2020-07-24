# YOLO v4-v3 CPU Inference API for Windows and Linux

This is a repository for an object detection inference API using the Yolov4 and Yolo v3  Opencv.

The inference REST API works on CPU and doesn't require any GPU usage. It's supported on both Windows and Linux Operating systems.

Models trained using our training Yolov4 or Yolov3  repository can be deployed in this API. Several object detection models can be loaded and used at the same time.

![predict image](./docs/4.gif)

## Prerequisites

- OS:
  - Ubuntu 16.04/18.04
  - Windows 10 pro/enterprise
- Docker

### Check for prerequisites

To check if you have docker-ce installed:

```sh
docker --version
```

### Install prerequisites

#### Ubuntu

Use the following command to install docker on Ubuntu:

```sh
chmod +x install_prerequisites.sh && source install_prerequisites.sh
```

#### Windows 10

To [install Docker on Windows](https://docs.docker.com/docker-for-windows/install/), please follow the link.

**P.S: For Windows users, open the Docker Desktop menu by clicking the Docker Icon in the Notifications area. Select Settings, and then Advanced tab to adjust the resources available to Docker Engine.**

## Build The Docker Image

In order to build the project run the following command from the project's root directory:

```sh
sudo docker build -t yolov4_inference_api_cpu -f ./docker/dockerfile .
```
### Behind a proxy

```sh
sudo docker build --build-arg http_proxy='' --build-arg https_proxy='' -t yolov4_inference_api_cpu -f ./docker/dockerfile .
```

## Run The Docker Container

To run the API, go the to the API's directory and run the following:

#### Using Linux based docker:

```sh
sudo docker run -itv $(pwd)/models:/models -p <docker_host_port>:7770 yolov4_inference_api_cpu
```
#### Using Windows based docker:

```sh
docker run -itv ${PWD}/models:/models -p <docker_host_port>:7770 yolov4_inference_api_cpu
```

The <docker_host_port> can be any unique port of your choice.

The API file will be run automatically, and the service will listen to http requests on the chosen port.

## API Endpoints

To see all available endpoints, open your favorite browser and navigate to:

```
http://<machine_IP>:<docker_host_port>/docs
```
The 'predict_batch' endpoint is not shown on swagger. The list of files input is not yet supported.

**P.S: If you are using custom endpoints like /load, /detect, and /get_labels, you should always use the /load endpoint first and then use /detect or /get_labels**

### Endpoints summary

#### /load (GET)

Loads all available models and returns every model with it's hashed value. Loaded models are stored and aren't loaded again

![load model](./docs/1.gif)

#### /detect (POST)

Performs inference on specified model, image, and returns bounding-boxes

![detect image](./docs/3.gif)

#### /get_labels (POST)

Returns all of the specified model labels with their hashed values

![get model labels](./docs/2.gif)

#### /models/{model_name}/predict_image (POST)

Performs inference on specified model, image, draws bounding boxes on the image, and returns the actual image as response

![predict image](./docs/4.gif)

#### /models (GET)

Lists all available models

#### /models/{model_name}/load (GET)

Loads the specified model. Loaded models are stored and aren't loaded again

#### /models/{model_name}/predict (POST)

Performs inference on specified model, image, and returns bounding boxes.

#### /models/{model_name}/labels (GET)

Returns all of the specified model labels

#### /models/{model_name}/config (GET)

Returns the specified model's configuration

#### /models/{model_name}/predict_batch (POST)

Performs inference on specified model and a list of images, and returns bounding boxes

**P.S: Custom endpoints like /load, /detect, and /get_labels should be used in a chronological order. First you have to call /load, and then call /detect or /get_labels**

## Model structure

The folder "models" contains subfolders of all the models to be loaded.
Inside each subfolder there should be a:

- Cfg file (yolo-obj.cfg): contains the configuration of the model

- Weights file (yolo-obj.weights)

- Names file  (obj.names) : contains the names of the classes

- Config.json (This is a json file containing information about the model)

  ```json
    {
      "inference_engine_name": "yolov4_opencv_cpu_detection",
      "confidence": 60,
      "nms_threshold": 0.6,
      "image": {
        "width": 416,
        "height": 416,
        "scale": 0.00392,
        "swapRB": true,
        "crop": false,
        "mean": {
          "R": 0,
          "G": 0,
          "B": 0
        }
      },
      "framework": "yolo",
      "type": "detection",
      "network": "network_name"
    }
  ```
  P.S
  
  - You can choose **"inference_engine_name"**: between **yolov4_opencv_cpu_detection** and **yolov3_opencv_cpu_detection** depending on the model you have.
  
  - You can change confidence and nms_threshold values while running the API
  - The API will return bounding boxes with a confidence higher than the "confidence" value. A high "confidence" can show you only accurate predictions

## Benchmarking

<table>
    <thead align="center">
        <tr>
            <th></th>
            <th colspan=3>Ubuntu</th>
        </tr>
    </thead>
    <thead align="center">
        <tr>
            <th>Network\Hardware</th>
            <th>Intel Xeon CPU 2.3 GHz</th>
            <th>Intel Core i9-7900 3.3 GHZ</th>
            <th>Tesla V100</th>
        </tr>
    </thead>
    <tbody align="center">
        <tr>
            <td>COCO Dataset</td>
            <td>0.259 seconds/image</td>
            <td>0.281 seconds/image</td>
            <td>0.0691 seconds/image</td>
        </tr>
    </tbody>
</table>

## Acknowledgment

[inmind.ai](https://inmind.ai)

[robotron.de](https://robotron.de)

Antoine Charbel, inmind.ai , Beirut, Lebanon

Daniel Anani, inmind.ai, Beirut, Lebanon

Hadi Koubeissy, Beirut, Lebanon
