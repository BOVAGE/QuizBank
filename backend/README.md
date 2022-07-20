# Quizy
The documentation of this API can be accessed on here: [Postman](https://documenter.getpostman.com/view/20059082/UzQxP53p)

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/20059082-6994dd9e-5fbb-4190-a6d2-9365aa99b589?action=collection%2Ffork&collection-url=entityId%3D20059082-6994dd9e-5fbb-4190-a6d2-9365aa99b589%26entityType%3Dcollection%26workspaceId%3D1bc3a66a-a600-47c3-b04b-625e7fe3aba9)

## Local Development Setup
1. Install [python](https://www.python.org/) if you do not have it installed.

**NB:** Ensure you have pip installed in PATH environment variable.

2. Clone this repo.
```
git clone https://github.com/BOVAGE/QuizBank.git
```
3. In the terminal / cmd, change directory to backend
```bash
cd backend/
```
4. Install [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv) using pip inorder to run this project in a virtual environment in order to avoid project's dependencies conflict.
```bash
pip install pipenv
```
**NB:** The rest of these commands below need to be run inside the `backend` directory.

5. In the backend directory, Run this command to install all the packages required in a virtual environment to run this project.
```bash
pipenv install
```
6. Once the installation is successful, fill in the empty environment variables in the `.env.sample` file with the approriate values.

### Setting up PlanetScale Database inorder to Get The Environment Variables.

7. Go to [PlanetScale](https://auth.planetscale.com/sign-up) and create an account.
8. Download the [Pscale CLI](https://github.com/planetscale/cli) in order to make a secure connection to your database and you use a local address to connect to your application. The local address basically act as a planetscale proxy.

9. You can create a database either in the [PlanetScale dashboard](https://app.planetscale.com/) or from the PlanetScale CLI. Once you have a db created, note the following credentials.
`DB_NAME`, `DB_USER`, `DB_PASSWORD` & `BRANCH_NAME`.
10. Authenticate the CLI with the following command:
```
pscale auth login
```
11. Create a secure local connection to pscale db 
```
pscale connect <DATABASE_NAME> <BRANCH_NAME>
```
12. Once the env vars have the appropriate variable, rename the `.env.sample` file to   `.env`.

> To know more about connecting a Django Application to PlanetScale Database, click [here](https://docs.planetscale.com/tutorials/connect-django-app)

### Starting the Server

13. Run this command to activate the virtual environment.
```bash
pipenv shell
```
14. Run this command to start the server at port 8000
```
python manage.py runserver
```
If you want to use another port, run this command replacing the port_number placeholder with your desired port.
```
python manage.py runserver ${port_number}
```