# airflow-model-trainer

This project was created for learning purpose, without any futher intentions of increasing/developing further functionality.

# Motivation
- Explore how Airflow will work using only one thread, with the help of async built-in API provided by Python (using Python 3.8.5)
- Learn Taskflow API provided by Apache Airflow framework
- Learn Kafka communication with other task in asynchronous manner
- Have fun :grin:

# Workflow
## This project contains only three dags
- First dag is responsible for fetching video frames from OpenCV camera and publish its content to specified kafka topic (by default topic name is `testing`). **NOTE:** Please don't use images as messages in any kafka-related production based environments as images are not well suit to be streamed as source to be provided to kafka broker (large bytes stream).
- Second dag is only responsible for subscribing to kafka topic and sending message content to minio object storage
- Last dag is simply responsible for fetching images from pre-defined buckets (by default `sample-train-data` `sample-val-data`) and training our DL/ML model


# How to run
- Clone the repository with command `https://github.com/Latterlig96/airflow-model-trainer.git `
- Go to repo with command `cd <repo_name>`, and build the project with command `make build`
- Create virtualenv with command `virtualenv env` and then execute command `source ./env/bin/activate`.After that you can install python dependencies with      command `make requirements`
- After that, type command `make db`, this command will setup airflow dependencies for you and create default admin user that have access to UI inferface. After that you should change default `dags_folder` path to `<pwd>/core/dags/`.
- Invoke Airflow scheduler with command `make scheduler`
- Open another bash terminal inside repository and tyle command `make webserver`, this should invoke Airflow webserver that listens on port 8080.
# Frameworks
- Apache Airflow <img src="./idea/../.idea/airflow.svg" width="50" height="50">
- Kafka <img src="./idea/../.idea/kafka.svg" width="50" height="50">
- Minio <img src="./idea/../.idea/minio.svg" width="50" height="50">
- PyTorch <img src="./idea/../.idea/pytorch.svg" width="50" height="50">
- Pytorch Lightning
- OpenCV <img src="./idea/../.idea/opencv.svg" width="50" height="50">
- Docker <img src="./idea/../.idea/docker.svg" width="50" height="50">
- Prometheus <img src="./idea/../.idea/prometheus.svg" width="50" height="50">
- Grafana <img src="./idea/../.idea/grafana.svg" width="50" height="50">
- MLFlow
  
# INFO
- AsyncCamera will resize all kind of images to shape (width:1366, height: 768) as it was default stream size that I was using during this project.
- Model that is used to train is EfficientNetB1 provided by fantastic `timm` library (Refer to: https://github.com/rwightman/pytorch-image-models), that expects to receive image of shape (256,256), so futher resizing will be provided during training.
