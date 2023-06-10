from flask import Flask, jsonify, request
import tensorflow as tf
import tensorflow_hub as hub
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import numpy as np

# Initialize Flask app
app = Flask(__name__)

embed = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4", trainable=False)


# Get the path to the service account key file from the environment variable
service_account_key_path = os.environ.get('SERVICE_ACCOUNT_KEY')

# Connect to firebase
cred = credentials.Certificate(service_account_key_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load data
users = db.collection('users').get()

user_data = []
for doc in users:
    data = doc.to_dict()
    user_data.append(data)

profile_data = []
for doc in users:
    data = doc.to_dict()
    profile_data.append(data['profile'])

# Process data so it can be use

user_data = pd.DataFrame(user_data, columns=['uid'])
profile_data = pd.DataFrame(profile_data, columns=['displayName','skills', 'interests'])
merge_data = pd.merge(user_data, profile_data, left_index=True, right_index=True)

result_data = merge_data[['uid', 'displayName', 'skills', 'interests']]
result_data['skills'] = result_data['skills'].apply(lambda skill_list: ', '.join([skill_dict['name'] for skill_dict in skill_list if skill_dict and 'uid' in skill_dict]) if isinstance(skill_list, list) else 'No Skill')
result_data['interests'] = result_data['interests'].apply(lambda interest_list: ', '.join([interest_dict['name'] for interest_dict in interest_list if interest_dict and 'uid' in interest_dict]) if isinstance(interest_list, list) else 'No Interest')

user_data = pd.DataFrame(result_data)

# Define a function to generate user stories
def generate_user_stories(user_data):
    user_story = []
    for index, row in user_data.iterrows():
        user_story.append({
            "uid": row['uid'],
            "story": f"I have Skill {row['skills']}, and I'm Interested in {row['interests']}"
        })
    return user_story


# Define a function to find the top N most similar users to a given user
def find_top_similar_users(current_user_uid, user_story, embed, n=10):
    # Check if current user not found
    if user_data.loc[user_data['uid'] == current_user_uid].empty:
        return "Current user not found!"

    # Get the current user's data and story
    current_user = user_data.loc[user_data['uid'] == current_user_uid]
    current_user_story = f"I have Skill {current_user['skills'][0]} , and I'm Interested in {current_user['interests'][0]}"

    # Encode the current user story into a vector
    current_user_vector = embed([current_user_story])

    # Encode all other user stories into vectors and store them in a matrix along with the user uid
    other_user_vectors = []
    other_user_uid = []
    for user in user_story:
        vector = embed([user["story"]])
        other_user_vectors.append(vector)
        other_user_uid.append(user["uid"])
    other_user_matrix = np.array(other_user_vectors)

    # Calculate the similarity scores between the current user vector and all other user vectors in the matrix
    similarity_scores = tf.matmul(other_user_matrix, tf.transpose(current_user_vector))

    # Get the top N most similar users and their scores
    most_similar_users = np.argsort(similarity_scores.numpy().reshape(-1))[::-1][:n]
    most_similar_user_uid = [other_user_uid[i] for i in most_similar_users]
    most_similar_user_scores = similarity_scores.numpy().reshape(-1)[most_similar_users]

    for i in range(1, n):
        print(f"User ID: {most_similar_user_uid[i]}, Similarity Score: {most_similar_user_scores[i]}")

# Define a route for the API
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Define a route for the API
@app.route('/api/users/<string:uid>')
def get_similar_users(uid):
    # Generate user stories
    user_story = generate_user_stories(user_data)

    # Find the top N most similar users
    similar_users = find_top_similar_users(uid, user_story, embed, n=500)

    # Return the results as JSON
    return jsonify(similar_users)

if __name__ == '__main__':
    app.run(debug=True)