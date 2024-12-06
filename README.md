StudentConnect Project Setup Guide
This guide provides detailed instructions on how to set up and run the "StudentConnect" project. Follow these steps carefully to ensure that your environment is configured correctly and the application runs smoothly.

1. Clone the Repository
First, you need to clone the repository:

bash
Copy code
git clone https://github.com/j-agbaje/StudentConnect.git
cd StudentConnect
2. Set Up a Virtual Environment
Setting up a virtual environment will help you isolate the project’s dependencies from your system’s Python environment.

Windows:
bash
Copy code
python -m venv venv
macOS and Linux:
bash
Copy code
python3 -m venv venv
Activate Virtual Environment
Activate the virtual environment by running:

bash
Copy code
# Windows
venv\Scripts\activate

# macOS and Linux
source venv/bin/activate
3. Install Dependencies
Navigate to the project directory and install the required packages specified in requirements.txt.

bash
Copy code
pip install -r requirements.txt
This command will install all the required dependencies for the project.

4. Set Up Environment Variables
You need to set up environment variables to run the application properly. You can do this by creating a .env file in the root directory of the project. Here’s an example:

bash
Copy code
ELASTICSEARCH_API_KEY=<your-elasticsearch-api-key>
ELASTICSEARCH_USER=<your-elasticsearch-username>
ELASTICSEARCH_PASSWORD=<your-elasticsearch-password>
REDIS_URL=<your-redis-url>
To create the .env file, you can copy the provided example and fill in the necessary details:

bash
Copy code
touch .env
Then, open the .env file in your text editor and add the following:

bash
Copy code
ELASTICSEARCH_API_KEY=YourElasticsearchAPIKeyHere
ELASTICSEARCH_USER=YourElasticsearchUsernameHere
ELASTICSEARCH_PASSWORD=YourElasticsearchPasswordHere
REDIS_URL=https://your-redis-server-url
Replace YourElasticsearchAPIKeyHere, YourElasticsearchUsernameHere, YourElasticsearchPasswordHere, and https://your-redis-server-url with your actual Elasticsearch and Redis credentials.

5. Configure Gunicorn (Optional)
If you plan to run your application with Gunicorn, you need to install it:

bash
Copy code
pip install gunicorn
Modify your application’s app.py file to use Gunicorn as the WSGI server:

python
Copy code
if __name__ == '__main__':
    from StudentConnect import app, socketio
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)
Run Gunicorn:

bash
Copy code
gunicorn app:app
This command starts the Gunicorn server and makes your Flask application accessible at http://0.0.0.0:10000.

6. Run the Application Locally
To run the application locally, execute:

bash
Copy code
python app.py
This will start your Flask application. You can access it via http://localhost:5000 by default.

7. Set Up for Deployment on Render
7.1 Prepare for Render
Ensure your environment variables are set correctly on Render:

Go to the environment settings in your Render dashboard.
Add the following environment variables:
ELASTICSEARCH_API_KEY
ELASTICSEARCH_USER
ELASTICSEARCH_PASSWORD
REDIS_URL
7.2 Deploy the Application on Render
Log in to your Render account.
Click "New Project" and select "Import Git Repository."
Provide the GitHub repository URL: https://github.com/j-agbaje/StudentConnect.git.
Follow the prompts to configure your environment variables (ELASTICSEARCH_API_KEY, ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD, REDIS_URL).
Deploy your application.
Once deployed, Render will automatically start your application.
7.3 Verify Deployment
After deployment, you should be able to access your application by visiting the provided URL in the Render dashboard.

8. Elasticsearch and Ngrok Integration
To connect your local Elasticsearch setup with your deployed app using Ngrok:

Set Up Ngrok:

Download and install Ngrok: https://ngrok.com/download.
Start Ngrok and forward port 5000:
bash
Copy code
ngrok http 5000
Update Elasticsearch URL:

In your .env file or your application, update the ELASTICSEARCH_URL to use Ngrok’s URL:
bash
Copy code
ELASTICSEARCH_URL=<ngrok-https-url>
Test Your Application:

Access your application through the Ngrok URL (e.g., https://1234abcd.ngrok.io).
This setup will allow your locally running application to communicate with Elasticsearch hosted in the cloud.

9. Common Issues and Solutions
Error: AuthenticationException(401, 'None'): Ensure that your Elasticsearch credentials (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD) are correctly set in the environment variables. Verify the credentials in the Elastic Cloud deployment dashboard.
Redis Connection Issues: Check that your Redis URL is correctly formatted and accessible. Ensure that the Redis server is running and not experiencing any issues.
SocketIO Errors: If you encounter errors with Redis and Eventlet, consider checking your Redis connection URL and ensure the Redis server is correctly configured.
10. Further Customizations and Features
Modifying the Frontend: You can customize the frontend by modifying the HTML, CSS, and JavaScript files in the templates directory.
Adding New Features: If you need to add new features, update the routes in app.py and ensure your database and services are correctly connected.
Monitoring and Logging: For monitoring and logging, consider integrating tools like Datadog or ELK Stack (Elasticsearch, Logstash, Kibana) to track application performance and logs.
