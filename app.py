from pymongo import MongoClient
import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
import streamlit.components.v1 as components
from datetime import datetime, timezone
import base64

# Configure the Google Generative AI API
genai.configure(api_key="AIzaSyCmOoKfi4I9sO1QW0qSEfmm93lmwu42pTA")
model = genai.GenerativeModel('gemini-1.5-flash')


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

# MongoDB connection
def get_mongo_client():
    client = MongoClient('mongodb+srv://jawan2608:vgIsDeU7MZvmZXE5@railways.9alpg.mongodb.net/?retryWrites=true&w=majority&appName=Railways')
    return client

# Insert complaint into MongoDB
def insert_complaint(data):
    client = get_mongo_client()
    db = client['complaints_db']  # Database name
    collection = db['complaints']  # Collection name
    result = collection.insert_one(data)
    return result.inserted_id

# Function to render the location component
def location_component():
    with open("location_component.html", "r") as f:
        html_code = f.read()
    components.html(html_code, height=85)

# Store location in a variable
def get_location():
    return st.session_state.get('location', "Unknown")

# Convert image to base64 string
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Streamlit UI
st.title('Railway Complaint Classifier')

# Initialize session state if not already present
if 'history' not in st.session_state:
    st.session_state.history = []

# Upload either an image or a video
uploaded_file = st.file_uploader("Upload an image or video", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])

# Input text
user_text = st.text_area("Enter your review (optional):", "")

# Render the location component
location_component()

# Extract location data
location = get_location()

if st.button("Send Complaint"):
    # Initialize summaries and data
    image_summary = None
    text_summary = None
    file_data = None
    content_type = None

    if uploaded_file is not None:
        file_type = uploaded_file.type.split('/')[0]  # image or video
        content_type = "Image" if file_type == "image" else "Video"

        if file_type == "image":
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            image_base64 = image_to_base64(image)  # Convert image to base64 string
            prompt = f"Classify the provided image into one of the following categories and give a one-line summary: {', '.join(complaint_categories)}"
            file_data = image_base64  # Store the base64 string
        elif file_type == "video":
            st.video(uploaded_file)
            file_data = io.BytesIO(uploaded_file.read()).getvalue()
            prompt = f"Classify the provided video into one of the following categories and give a one-line summary: {', '.join(complaint_categories)}"

        # Make sure to only use the image or video data for the API call
        response = model.generate_content([image, prompt])
        image_summary = response.text if response else "No summary available"
        st.write(f"{content_type} Classification and Summary:")
        st.success(image_summary)
    
    if user_text:
        prompt = f"{user_text} Rate this sentence on a scale of 0-5 whether the review is positive or negative and on what scale. Also, write only the summary of the review. Classify this from the following categories: {', '.join(complaint_categories)}"
        response = model.generate_content(prompt)
        text_summary = response.text if response else "No summary available"
        st.write("Text Classification and Summary:")
        st.success(text_summary)
    
    # Determine category based on either summary
    category = next((i for i in complaint_categories if i in (text_summary or '') or i in (image_summary or '')), "Uncategorized")
    location_data = st.session_state.get('location', {})

    # Extract the latitude and longitude from the location data
    latitude = location_data.get('latitude')
    longitude = location_data.get('longitude')

    # Prepare data to insert into MongoDB
    complaint_data = {
        "category": category,
        "original_complaint": user_text,
        "image_summary": image_summary,
        "text_summary": text_summary,
        "file_data": file_data,  # Store the base64 string for the image
        "status": "pending",
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "timestamp": datetime.now(timezone.utc)
    }

    # Insert into MongoDB
    insert_complaint(complaint_data)
