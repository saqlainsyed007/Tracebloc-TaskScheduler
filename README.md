# Tracebloc-TaskScheduler

*[Problem Statement](https://docs.google.com/document/d/1QH8LCmbIkL00HuyYvbkU8R2vJi8vM1jzVikQMhjLrIo/edit?usp=sharing)
(Restricted as this is an interview exercise)*


## Setup Instructions

### Step 1

Install Docker: https://docs.docker.com/engine/install/

### Step 2

Clone this repository and `cd` into the `Tracebloc-TaskScheduler` folder in a terminal

### Step 3

Run the containers
```
docker-compose up -d
```


**Running the application has the follwing effect**

- An admin user is created. Refer to **Admin Dashboard** section below.
- 2 Users with usernames `user1` and `user2` are created with password `password`.
- 100 tasks are created between the two users that are scheduled to run at different intervals spread over the next 60 min.
- A service `tasks-scheduler-django-trigger-tasks-command` is running that would pick eligible tasks and schedule them for execution.
- A local server is running and is available at port 8000 `http://localhost:8000/`.

You may view the scheduled tasks in the admin dashboard

http://localhost:8000/admin/schedule_tasks/scheduledtask/


## View Executed Tasks

Tasks executed are logged in the docker logs of the `tasks-scheduler-celery` container

```
docker logs tasks-scheduler-celery
```

## Admin Dashboard

You may enter the admin dashboard using the following information

**URL:** `http://localhost:8000/admin/`

**Username:** `admin`

**Password:** `admin`


## Postman collection

Download and install Postman: https://www.postman.com/downloads/

This repository also contains a postman collection JSON file for the APIs supported by the app

`Tracebloc-TaskScheduler.postman_collection.json`
