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
   CREATE DATABASE carroll_classrooms;
   ```
4. Create a new user:
   ```
   CREATE USER 'caroll_user'@'localhost' IDENTIFIED BY 'REPLACE_WITH_USER_PASSWORD';
   CREATE USER 'caroll_user'@'%' IDENTIFIED BY 'REPLACE_WITH_USER_PASSWORD';
   ```
6. Give this user privileges on the newly created database:
    ```
    GRANT ALL PRIVILEGES ON carroll_classrooms.* TO 'carroll_user'@'localhost' WITH GRANT OPTION;
    GRANT ALL PRIVILEGES ON carroll_classrooms.* TO 'carroll_user'@'%' WITH GRANT OPTION;
    ```
5. Log out of the root account:
   ```
   quit
   ```
6. Log in as this newly created user, using the password used during the user's creation:
   ```
   mysql -u carroll_user -p carroll_classrooms
   ```
7. If you can successfully log in, the database is all set up! Log out of this user before continuing.

### Installing Dependencies
The database for the application is now created with a user able to access it. Next, install the necessary dependencies and build the front end of the project. Ensure that you are still in the parent directory of the project. Before running these steps, ensure that you have Python (can be downloaded [here](https://www.python.org/downloads/)) installed on your machine. 
1. Install Django:
   ```
   pip3 install django
   ```
2. Clone the repository from GitHub:
   ```
   git clone https://github.com/rjohnson05/CarrollClassroomAnalytics
   ```
3. Move into the parent directory of the project
4. Install necessary back end dependencies:
   ```
   pip3 install -r requirements.txt
   ```
5. Move into the frontend directory
6. Install frontend dependencies:
   ```
   npm install
   ```
4. Build the React front end for production:
   ```
   npm run build
   ```
6. Move back to the parent directory of the project



### Creating the Database Structure
Next, the database structure used by the application must be moved into the created database. Ensure that you are in the parent directory.
1. Load the database structure:
   ```
   python manage.py migrate
   ```

### Launching the Application
Lastly, launch the program by running this command: 
```
py manage.py runserver
```
The application should now be visible after navigating to `localhost:8000` within a web browser. 
