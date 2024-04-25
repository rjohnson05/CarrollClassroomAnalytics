# Carroll College Classroom Analytics Software

This software is a tool created for Caroll College, providing them with the ability to analyze the data of a single course schedule. Via a heatmap, it shows how many classrooms are being used during any particular 
time throughout the week. It also provides a list of used classrooms for any particular time, along with the courses being held within the classroom. A classroom's schedule may also be viewed, showing all courses
held in a particular classroom on the current course schedule. This software has the capability to handle only one course schedule at a time. As such, if a new course schedule is uploaded, all data from the previous
course schedule will be deleted. However, any classroom data uploaded will be preserved between course schedules. To update the classroom information, a new spreadsheet must be uploaded with the corrected information.

## Setting Up the Application

### Creating the Database
Before launching the application, a database must be created. Ensure that you have MySQL (can be downloaded [here](https://dev.mysql.com/downloads/mysql/)) installed onto your machine before completing the following steps: 
1. Log into the root account:
   ```
   mysql -u root
   ```
3. Once logged into the root account, create a new database:
   ```
   CREATE DATABASE replace_with_db_name;
   ```
4. Create a new user:
   ```
   CREATE USER 'replace_with_db_user'@'localhost' IDENTIFIED BY 'replace_with_password';
   CREATE USER 'replace_with_db_user'@'%' IDENTIFIED BY 'replace_with_password';
   ```
6. Give this user privileges on the newly created database:
    ```
    GRANT ALL PRIVILEGES ON replace_with_db_name.* TO 'replace_with_db_user'@'localhost' WITH GRANT OPTION;
    GRANT ALL PRIVILEGES ON replace_with_db_name.* TO 'replace_with_db_user'@'%' WITH GRANT OPTION;
    ```
5. Log out of the root account:
   ```
   quit
   ```
6. Log in as this newly created user, using the password used during the user's creation:
   ```
   mysql -u replace_with_db_user -p replace_with_db_name
   ```
7. If you can successfully log in, the database is all set up! Log out of this user before continuing.

### Installing Dependencies
The database for the application is now created with a user able to access it. Next, install the necessary dependencies and build the front end of the project. Ensure that you are still in the parent directory of the project. Before running these steps, ensure that you have the following installed on your machine: 
- Python: https://www.python.org/downloads/
- Git: https://git-scm.com/downloads
- Node.js: https://nodejs.org/en/download
   
1. Clone the repository from GitHub:
   ```
   git clone https://github.com/rjohnson05/CarrollClassroomAnalytics
   ```
2. Move into the parent directory of the project
3. Install necessary back end dependencies:
   ```
   pip3 install -r requirements.txt
   ```
4. Move into the frontend directory
5. Install frontend dependencies:
   ```
   npm install
   ```
6. Build the React front end for production:
   ```
   npm run build
   ```
7. Move back to the parent directory of the project

### Set Environment Variables
Before moving the database models contained by the Django project to the previously created database, you must set the environment variables to the values used when creating the database.
1. Make a copy of *.env.template*
2. Rename this file to *.env*
3. For each variable, enter the values used when creating the database.

### Final Steps
The database structure used by the application must now be moved into the created database, and the static files created to be served by a web server. Ensure that you are in the parent directory.
2.  Load the database structure:
   ```
   python3 manage.py migrate
   ```
3. Create the static files:
   ```
   python3 manage.py collectstatic
   ```

### Launching the Application
Finally, launch the program by running this command:
```
python3 manage.py runserver
```
The application should now be visible after navigating to `localhost:8000` within a web browser. 
