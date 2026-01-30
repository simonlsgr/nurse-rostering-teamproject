# Run the docker container

## Prequisites
Make sure you have Docker installed on your machine.

### Licenses
#### Gurobi License
Ensure that the gurobi license is stored at `~/gurobi.lic`.
#### Hexaly License
The Hexaly license needs to be stored inside the project folder at `backend/hexaly_installation/license.dat`. A git ignore rule is in place to prevent it from being committed to version control.

Usually the license file can be found in `/opt/hexaly_14_0/license.dat` on  the local machine.

You can check whether the license is read correctly by checking the result on `http://127.0.0.1:8080/nurse_rostering_solver/v0/test_hx`.

## Instructions

To run the backend Docker container, follow these steps:
1. Make sure you have Docker installed on your machine. You can download it from [here](https://www.docker.com/get-started).
2. Open your terminal or command prompt.
3. Navigate to the `backend` folder.
4. Run the following command to build the Docker image:
   ```
   docker compose build
   ```
5. After the image is built, run the following command to start the Docker container:
   ```
   docker compose up
   ```
6. The backend server should now be running inside the Docker container. You can access it at `http://localhost:8080`.

