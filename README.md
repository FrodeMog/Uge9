# Cereal Opgave

# Installation

## Python environment

1. Create environment:
    ```
    python -m venv .venv
    ```

2. Activate environment:
    ```
    .venv\Scripts\activate
    ```

3. Install requirements:
    ```
    pip install -r requirements.txt
    ```

## Specificaftions
In this assignment I will create a basic CRUD API using RESTful architecture. In python using SQLAlchemy ORMs in a MySQL database with FastAPI for the endpoints.

##### Technologies
Status | Technologies |
:---:| --- |
-| Python
-| FastAPI
-| SQLAlchemy
-| MySQL 

##### Featurelist
Status | Feature |
:---:| --- |
-| Database of Cereal
-| GET endpoints with exact filtering
-| GET endpoints with Less/More than filtering
-| POST endpoints for Update + Add
-| DELETE endpoints
-| Users: Username/Password checks for POST/DELETE
-| GET endpoint for Pictures

##### Basic requirements - Time estimates
Status | Requirement | Time | Comment
:---:| --- | --- | ---
Day 1|  | 6h | Up to 2h extra
✅| Create Database from cereal.csv | 30m | Day 1
✅| Setup ORM | 1h | Day 1
✅| Setup Database Connector | 10m | Day 1
✅| Setup Database Handler | 1h | Day 1
✅| GET request for all objects | 1h | Day 1
✅| GET with filtering of parameters | 30m | Day 1
✅| GET with advanced filtering  | 1h | Day 1
✅| Debugging + Cleanup  | 1h | Day 1
Day 2|  | 6h | Up to 2h extra
✅| POST update object ID or add new object  | 2h | Day 2
✅| DELETE endpoint  | 2h | Day 2
✅| Add users to database  | 30m | Day 2
✅| User rights for POST/DELETE  | 1h | Day 2
Day 3|  | 6h | Up to 2h extra
-| GET for pictures tied to IDs | 3h | Day 3
-| Debug / Cleanup / Documentation | 3h | Day 3
Total |  | 20h | 3 Days

##### Extra Advanced requirements
Status | Requirement | Time | Comment
:---:| --- | --- | ---
✅| (JWT) JSON Web Token authentication | 4h | Day x
-| React Front-end for login + endpoints | 4h | Day x
-| React Front-end for displaying picturs of cereal | 4h | Day x