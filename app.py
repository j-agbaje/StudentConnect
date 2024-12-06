from StudentConnect import app, db
from StudentConnect import socketio

# from StudentConnect.routes import config




# print(config)
# Run the app
if __name__ == '__main__':  # Ensures app context is active   
    socketio.run(app)
    


