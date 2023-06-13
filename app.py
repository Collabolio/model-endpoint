import os
from flask import Flask, jsonify, request, render_template
import tensorflow as tf
import tensorflow_hub as hub
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Initialize Port
port = int(os.environ.get('PORT', 8080))

# Connect to firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Use Tensorflow Hub to load Universal Sentence Encoder
embed = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4", trainable=False)


# Load data
def load_data():
    users = db.collection('users').get()

    user_data = []
    for doc in users:
        data = doc.to_dict()
        user_data.append(data)

    profile_data = []
    for doc in users:
        data = doc.to_dict()
        profile_data.append(data['profile'])

    return user_data, profile_data

# Process data so it can be use
def process_data(user_data, profile_data):
    user_data = pd.DataFrame(user_data, columns=['uid'])
    profile_data = pd.DataFrame(profile_data, columns=['displayName','skills', 'interests'])
    merge_data = pd.merge(user_data, profile_data, left_index=True, right_index=True)

    result_data = merge_data[['uid', 'displayName', 'skills', 'interests']]
    result_data['skills'] = result_data['skills'].apply(lambda skill_list: ', '.join([skill_dict['name'] for skill_dict in skill_list if skill_dict and 'uid' in skill_dict]) if isinstance(skill_list, list) else 'No Skill')
    result_data['interests'] = result_data['interests'].apply(lambda interest_list: ', '.join([interest_dict['name'] for interest_dict in interest_list if interest_dict and 'uid' in interest_dict]) if isinstance(interest_list, list) else 'No Interest')

    user_data = pd.DataFrame(result_data)

    return user_data

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
def find_top_similar_users(current_user_uid, user_data, user_story, embed, n):
    # Check if current user not found
    if user_data.loc[user_data['uid'] == current_user_uid].empty:
        return "Current user not found!"

    # Get the current user's data and story
    current_user = user_data.loc[user_data['uid'] == current_user_uid]
    current_user_story = f"I have Skill {current_user['skills'].values.item()} , and I'm Interested in {current_user['interests'].values.item()}"

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

    # Convert the similarity scores to float64
    most_similar_user_scores = most_similar_user_scores.astype(np.float64)

    # Create a list of dictionaries containing the user ID and similarity score for each of the top N most similar users
    similar_users = []
    for i in range(1, n):
        similar_user = {"uid": most_similar_user_uid[i], "similarity_score": most_similar_user_scores[i]}
        similar_users.append(similar_user)

    return similar_users


# Define a route for the API
@app.route('/')
def index():
    # Render the index.html template
    return render_template('index.html')

@app.route('/api/users/<string:current_user_uid>/<int:n>')
def get_similar_users(current_user_uid, n):
    # Load data
    user_data, profile_data = load_data()

    # Process data
    user_data = process_data(user_data, profile_data)

    # Generate user story
    user_story = generate_user_stories(user_data)

    # # Find the top N most similar users
    similar_users = find_top_similar_users(current_user_uid, user_data, user_story, embed, n)

    # Return the results as JSON
    return jsonify(similar_users)

if __name__ == '__main__':
    app.run()