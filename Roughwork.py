# from flask import Flask, request, jsonify
# from textblob import TextBlob

# app = Flask(__name__)

# def get_sentiment_score(text):
#     # Analyze the sentiment of the text using TextBlob
#     blob = TextBlob(text)
#     sentiment = blob.sentiment.polarity

#     # Convert the sentiment score (-1 to 1) to a scale of 0 to 10
#     rating = (sentiment + 1) * 5
#     return round(rating, 1)

# @app.route('/rate-text', methods=['POST'])
# def rate_text():
#     # Get the text from the POST request
#     data = request.json
#     text = data.get('text')

#     if not text:
#         return jsonify({'error': 'No text provided'}), 400

#     # Get the sentiment rating
#     rating = get_sentiment_score(text)

#     return jsonify({'text': text, 'rating': rating})

# if __name__ == '__main__':
#     app.run(debug=True)












import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
import streamlit.components.v1 as components
import json


# Configure the Google Generative AI API
genai.configure(api_key="AIzaSyCmOoKfi4I9sO1QW0qSEfmm93lmwu42pTA")
model = genai.GenerativeModel('gemini-1.5-flash')

# Define the complaint categories
complaint_categories = [
    "Food Quality",
    "Food Safety",
    "Service Quality",
    "Cleanliness",
    "Comfort",
    "Facilities",
    "Timeliness",
    "Safety and Security",
    "Noise Levels",
    "Accessibility",
    "Booking and Ticketing",
    "Luggage Handling",
    "Communication",
    "Temperature Control",
    "Food Availability"
]


def location_component():
    # Load the HTML component
    with open("location_component.html", "r") as f:
        html_code = f.read()
    return components.html(html_code, height=300)

st.title('Railway Complaint Classifier')

# Display the location component
st.write("Click the button below to get your location:")
location_component()

# Get location data from JavaScript
location_data = st.query_params().get('location', None)
if location_data:
    try:
        # Convert to JSON
        location = json.loads(location_data[0])
        st.write(f"Latitude: {location['lat']}, Longitude: {location['lon']}")
    except json.JSONDecodeError:
        st.write("Unable to decode location data.")
else:
    st.write("Location data not available.")


st.title('Railway Complaint Classifier')

# Initialize session state if not already present
if 'history' not in st.session_state:
    st.session_state.history = []

# Function to add entry to history
def add_to_history(category, summary, type):
    st.session_state.history.append({'Type': type, 'Category': category, 'Summary': summary})

# Allow users to choose between image and text classification
option = st.selectbox("Choose functionality", ["Upload Image", "Post Message", "View History"])

if option == "Image Classification":
    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file is not None:
        # Load the image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Convert image to bytes
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_data = image_bytes.getvalue()

        # Prepare the prompt
        prompt = "Classify the provided image into one of the following categories and give one line summary of the image: " + ", ".join(complaint_categories)

        # Generate the classification and summary
        response = model.generate_content([image, prompt])  
        # Display the result
        st.write("Classification and Summary:")
        st.write(response.text)

        # Add result to history
        # Adapt response parsing as needed
        # Example split; adjust based on actual response format
        category=""
        for i in complaint_categories:
            if i in response.text:
                category = i
                break

        add_to_history(category, summary.strip(), 'Image Classification')

elif option == "Text Classification":
    # Input text
    user_text = st.text_area("Enter your review:", "")

    if st.button("Classify Text"):
        # Generate text classification
        prompt = f"{user_text} Rate this sentence on a scale of 0-5 whether the review is positive or negative and on what scale also write only summary of the review. Classify this from the following categories: " + ", ".join(complaint_categories)
        response = model.generate_content(prompt)

        # Display the result
        st.write("Text Classification and Summary:")
        st.write(response.text)

        # category, summary = response.text.split(':', 1)
        # add_to_history(category.strip(), summary.strip(), 'Text Classification')

elif option == "View History":
    st.header('History Dashboard')
    if st.session_state.history:
        st.write("### Previous Classifications")
        st.table(st.session_state.history)
    else:
        st.write("No history available.")



# Create a custom component

