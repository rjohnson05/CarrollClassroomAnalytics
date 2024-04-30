# Carroll College Classroom Analytics Software

This software is a tool created for Caroll College, providing them with the ability to analyze the data of a single
course schedule. Via a heatmap, it shows how many classrooms are being used during any particular
time throughout the week. It also provides a list of used classrooms for any particular time, along with the courses
being held within the classroom. A classroom's schedule may also be viewed, showing all courses
held in a particular classroom on the current course schedule. This software has the capability to handle only one
course schedule at a time. As such, if a new course schedule is uploaded, all data from the previous
course schedule will be deleted. However, any classroom data uploaded will be preserved between course schedules. To
update the classroom information, a new spreadsheet must be uploaded with the corrected information. An example
classroom spreadsheet and course schedule spreadsheet have been provided in this project.

## Setting Up the Application

### Creating the Database

1. Install MySQL 8.0.34 on your local machine(can be downloaded [here](dev.mysql.com/downloads/mysql/)). Ensure that it
   is configured correctly by typing `mysql --version`. If MySQL is installed correctly, this command should output
   something similar to `mysql Ver 8.0.34`.

2. Log into the root account:

```
sudo mysql -u root
```

3. Once logged into the root account, create a new database:

```
CREATE DATABASE your_database_name;
```

In place of your_database_name, type the name you would like to give your database. **TAKE NOTE OF THIS NAME.** You’ll
need it again later.

4. Create a new user:

```
CREATE USER 'your_user_name'@'localhost' IDENTIFIED BY 'your_user_password;
CREATE USER 'caroll_user'@'%' IDENTIFIED BY 'your_user_password';
```

In place of `your_user_name` and `your_user_password`, type the username and password you would like to give your new
user. Again, **TAKE NOTE OF THE USERNAME AND PASSWORD**. You’ll need both of these later in the setup process.

5. Give this user privileges on the newly created database:

```
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_user_name'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_user_name'@'%' WITH GRANT OPTION;
```

Make sure to use the database name and user name you used in Steps 2 & 3.

6. Log out of the root account: `quit`

7. Log in as this newly created user, using the same username and database name as used in Steps 3-4. You will be
   prompted for a password – use the same password created in Step 4.

```
mysql -u your_user_name -p your_database_name
```

8. If you can successfully log in, your database is all set up! Log out of this user before continuing.

### Installing Dependencies

1. Install Git on your machine (can be downloaded [here](git-scm.com/downloads)). Ensure you have Git installed on your
   machine by typing `git --version`. If installed correctly, you should receive output similar to `git version 2.41`.

2. Install Node.js on your machine (can be downloaded [here](nodejs.org/en/download)).

3. Install npm on your machine (can be downloaded [here](www.npmjs.com/package/download)). Ensure you have Git installed
   on your machine by typing `npm --version`. If installed correctly, you should receive output similar to `10.0.0`.

4. Install Python 3.12 on your machine (can be downloaded [here](python.org/downloads/)). Ensure you have Python
   installed on your machine by typing `python3 –-version` if on Linux/MacOS or `python --version` if on Windows. If
   installed correctly, you should receive output similar to `Python 3.12`.

5. Ensure that you have the most recent version of pip installed. If using macOS or Linux, use this command:

```
sudo pip3 install -U pip
```

If using Windows, use:

```
pip install -U pip
```

6. Install Django:

```
pip3 install django
```

7. Clone the repository from GitHub:

```
git clone https://github.com/rjohnson05/CarrollClassroomAnalytics
```

8. Move into the parent directory of the project:

```
cd CarrollClassroomAnalytics
```

9. Install necessary back end dependencies:

```
pip3 install -r requirements.txt
```

10. Move into the frontend directory:

```
cd frontend
```

11. Install frontend dependencies:

```
npm install
```

12. Move back to the parent directory of the project:

```
cd ..
```

### Set Environment Variables

1. Ensure that you are in the parent directory. Make a copy of the *.env.template* file and rename it to *.env*. In
   Linux, this can be done with this command:

```
cp .env.template .env
```

In Windows, this can be done with the following command:

```
copy .env.template .env
```

2. Generate a secret key:

```
openssl rand -base64 32
```

Copy the output of this command.

3. Paste your generated secret key into the *.env* file after *SECRET_KEY=*

4. Fill in the database name, username and user password used when creating the database.

### Creating the Database Structure

1. Ensure that you are in the parent directory. First create the migration files needed to load the database structure:

```
python3 manage.py makemigrations api
```

2. Load the database structure:

```
python3 manage.py migrate
```

### Testing the Application

Testing the application runs all unit tests within the *api/tests/test_services.py* file. All tests for the methods
within *api/services.py* can be run to ensure the application’s backend logic is behaving correctly. These tests are
completely optional. If you don’t want to test the application, skip to the next section (“Building Static Files”) to
continue setting the app up.

1. Log into the root MySQL account:

```
sudo mysql -u root
```

2. Give the user created earlier privileges on the testing database

```
GRANT ALL PRIVILEGES ON test_`your_database_name`.* TO 'your_user_name'@'localhost' WITH GRANT OPTION;

GRANT ALL PRIVILEGES ON test_`your_database_name`.* TO 'your_user_name'@'%' WITH GRANT OPTION;
```

Notice that the name of the testing database is the same as that of the production database, but with *test_* placed in
front. So, if the name of the production database is database, the name of the testing database would be
*test_database*. Make sure to use the same user as created earlier.

3. Log out of the root account: `quit`

4. Ensure that you are in the root directory before running the tests:

```
python3 manage.py test
```

### Building Static Files

1. Ensure that you are in the parent directory. Move to the frontend directory:

```
cd frontend
```

2. Build the front end static files for production:

```
npm run build
```

3. Move back to the parent directory:

```
cd ..
```

4. Build static files in the back end:

```
python3 manage.py collectstatic
```

5. There should now be a *static/* directory within the parent directory.

### Setting Up a WSGI Server & Web Server

To set up the application for production, both a WSGI server and web server need to be set up. If using Linux, this can
be done using Gunicorn and Nginx, as shown below. For alternate setups, see Dunicorn’s
deployment [documentation](https://docs.gunicorn.org/en/latest/deploy.html)

1. Ensure that you are in the parent directory, and then move the static files to */var/www/*:

```
sudo cp -r static /var/www
```

2. Create a Gunicorn socket:

```
sudo nano /etc/systemd/system/gunicorn.socket
```

3. In *gunicorn.socket*, place the following:

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

4. Create a Gunicorn service:

```
sudo nano /etc/systemd/system/gunicorn.service
```

5. In *gunicorn.service*, place the following:

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=student
Group=www-data
WorkingDirectory=/home/student/CarrollClassroomAnalytics
ExecStart=/home/student/.local/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          carroll_classroom_analytics.wsgi:application

[Install]
WantedBy=multi-user.target
```

6. Start the socket:

```
sudo systemctl start gunicorn.socket
```

7. Enable the socket:

```
sudo systemctl enable gunicorn.socket
```

8. Check the status of the socket:

```
sudo systemctl status gunicorn.socket.
```

You should see that the gunicorn socket is active and enabled.

9. Test the gunicorn service by sending a testing request to the socket:

```
curl –unix-socket /run/gunicorn.sock localhost
```

You should receive an HTML response if it is working correctly.

10. Install Nginx on your machine (can be downloaded [here](https://nginx.org/en/download.html))

11. Create a new Nginx server block:

```
sudo nano /etc/nginx/sites-available/carroll_classrooms_analytics.conf 
```

12. In carroll_classrooms_analytics.conf, type the following:

```
server {
    listen 80;
    server_name 10.39.1.95;

    location /static/ {
        root /var/www;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

13. Link this newly created file to the sited-enabled directory:

```
sudo ln -s /etc/nginx/sites-available/carroll_classrooms_analytics.conf /etc/nginx/sites-enabled
```

14. Restart Nginx:

```
sudo systemctl restart nginx
```

### Launching the Application

1. Launch the program by running this command:

```
python3 manage.py runserver
```

2. The application should now be running! Test this by entering the IP address of the machine into a web browser on
   another machine. You should now be able to see the home page of the application, titled “Classroom Utilization
   Overview”.

