from flask import Flask, request, jsonify
import requests
import logging
import DSM
from flask_cors import CORS



app = Flask(__name__)

CORS(app)
app.name = "flask-server-2"

# Clear the Flask's default logger
app.logger.handlers.clear()
# Set the logging level
app.logger.setLevel(logging.DEBUG)

# Create a log handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a log formatter
formatter = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the log handler to the application logger
app.logger.addHandler(console_handler)

all_job_categories = ["DEVELOPMENT", "MARKETING", "SALES", "BUSINESS"]
handle_categories = ["DEVELOPMENT", "MARKETING"]

master_node = "http://54.67.32.100:8080"


@app.route('/')
def hello():
    print(app.name)
    response = requests.get(master_node)
    return 'Hello, Flask!'+str(app.name) +" "+ str(response)


@app.route('/api/publish', methods=['POST'])
def post_published_data():
    data = request.get_json()

    if data["jobCategory"] not in handle_categories:
        print("inside if")
        response_data = requests.post(master_node+"/api/publish", json=data)
        data = response_data.json()
        return jsonify(data)

    DSM.JOB_POSTS.append(data)
    print(DSM.JOB_POSTS)

    response = jsonify({'message': 'Job posted successfullly',
                        'name': str(app.name)})
    response.status_code = 200

    return response


def send_data_for_subscriber():
    data = request.get_json()
    jobCategory = data["jobCategory"]



''' TO DO: Confirm query params and proceed '''


@app.route('/api/publish', methods=['GET'])
def get_subscribe_data():
    # send the job posts of that subscriber.
    data = request.args
    print(data)
    return None


@app.route('/api/subscribe', methods=['POST'])
def post_subscribed_data():
    data = request.get_json()
    subscriberName = data["subscriberName"]
    jobCategory = data["jobCategory"]
    existing_subscriber = False

    if jobCategory in handle_categories:

        for subscriber in DSM.SUBSCRIBER_DATA:
            if subscriber["subscriberName"].lower() == subscriberName.lower():
                subscriber["subscribed"].append(jobCategory)
                existing_subscriber = True
                break

        if not existing_subscriber:
            DSM.SUBSCRIBER_DATA.append({
                "subscriberName": data["subscriberName"],
                "subscribed": [data["jobCategory"]]
            })

        response = jsonify({
            "message": "Subscribed Successfully ",
            "name": str(app.name)

        })
        response.status_code = 200
        return response
    else:
        # send the request
        response = requests.post(url=master_node+"/api/subscribe", json=data)
        return response

@app.route('/api/subscribe', methods=['GET'])
def get_subscribed_data():
    response = []
    count = 0
    # return the list of objects with subscriber name and the list of job posts
    for subscriber in DSM.SUBSCRIBER_DATA:
        subscriberName = subscriber["subscriberName"]
        subscribed = subscriber["subscribed"]
        append_object = {
            "subscriberName": subscriberName,
            "jobPosts": []
        }
        print(count+1)

        for jobPost in DSM.JOB_POSTS:
            for subscribedCategory in subscribed:
                print(f"JOB POST: {jobPost}")
                if jobPost["jobCategory"].lower() in subscribedCategory.lower():
                    append_object["jobPosts"].append(jobPost)
        response.append(append_object)
                    
    return jsonify(response)



@app.errorhandler(Exception)
def server_error(error):
    app.logger.error(error)
    response = jsonify({
        'error': 'Internal Server error',
        'message': 'An unexpected error occurred on the server.'
    })
    response.status_code = 500
    return response


if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0", debug=True)
