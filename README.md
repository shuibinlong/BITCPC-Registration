# BIT校赛报名系统

## 环境

* Django == 2.1.7
* django_froala_editor == 2.9.3
* django_richtextfield == 1.4.0
* django_tinymce == 2.8.0

## Build

Install dependencies command:
```
$ pip install -r requirements.txt
```
Generate admin user command:
```
$ python manage.py createsuperuser
```
Serve with hot reload at `localhost:<port>` by the following command:
```
$ python manage.py runserver <port>
```

## Docker
This project has been dockerized. To build a docker image from source, execute the following command at the root directory of this project:
```
$ docker build .
```
The docker image built can be started by the following command:
```
$ docker run -d -p 80:<port> <image-id>
```
