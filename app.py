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
    with open("location_component.html", "r") as f:
        html_code = f.read()
    return components.html(html_code, height=85)

# Display the location component
st.write("Click the button below to get your location:")
location_component()


st.title('Railway Complaint Classifier')


# Get location data from query parameters
location_data = st.query_params.get('location')
if location_data:
    try:
        # Convert to JSON
        location = json.loads(location_data[0])
        print(location)
        latitude = location['lat']
        longitude = location['lon']
        prompt = "give name of the place and the city with latitude={latitude},longitude={longitude}"
        response = model.generate_content(prompt)
        st.success(response.text)
    except json.JSONDecodeError:
        st.write("Unable to decode location data.")
# else:
#     st.write("Location data not available.")

# Initialize session state if not already present
if 'history' not in st.session_state:
    st.session_state.history = []

# Function to add entry to history
def add_to_history(category, summary, type):
    st.session_state.history.append({'Type': type, 'Category': category, 'Summary': summary})

# Allow users to choose between image and text classification
option = st.selectbox("Choose functionality", ["Upload Image", "Post Message", "Upload Video","View History"])

if option == "Upload Image":
    try:
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
            st.success(response.text)

            # Extract category and summary
            category = ""
            summary = ""
            for i in complaint_categories:
                if i in response.text:
                    category = i
                    break

            if '.' in response.text:
                summary = response.text.split('.')[1].strip()
            else:
                summary = "No summary available"

            add_to_history(category, summary, 'Image Classification')
            
    except Exception as e:
        pass  # Suppress all errors

elif option == "Post Message":
    try:
        # Input text
        user_text = st.text_area("Enter your review:", "")

        if st.button("Classify Text"):
            # Generate text classification
            prompt = f"{user_text} Rate this sentence on a scale of 0-5 whether the review is positive or negative and on what scale also write only summary of the review. Classify this from the following categories: " + ", ".join(complaint_categories)
            response = model.generate_content(prompt)

            # Display the result
            st.write("Text Classification and Summary:")
            st.success(response.text)

            # Extract category and summary
            category = ""
            summary = ""
            for i in complaint_categories:
                if i in response.text:
                    category = i
                    break

            if ':' in response.text:
                parts = response.text.split(':', 1)
                category = parts[0].strip()
                summary = parts[1].strip()
            else:
                summary = "No summary available"

            add_to_history(category, summary, 'Text Classification')
    except Exception as e:
        pass  # Suppress all errors

elif option == "Upload Video":
    try:
        # Upload video
        uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

        if uploaded_video is not None:
            # Load the video
            st.video(uploaded_video)

            # Convert video to bytes
            video_bytes = io.BytesIO(uploaded_video.read())
            video_data = video_bytes.getvalue()

            # Prepare the prompt
            prompt = "Classify the provided video into one of the following categories and give one line summary of the video: " + ", ".join(complaint_categories)

            # Generate the classification and summary
            response = model.generate_content([video_data, prompt])

            # Display the result
            st.write("Classification and Summary:")
            st.success(response.text)

            # Extract category and summary
            category = ""
            summary = ""
            for i in complaint_categories:
                if i in response.text:
                    category = i
                    break

            if '.' in response.text:
                summary = response.text.split('.')[1].strip()
            else:
                summary = "No summary available"

            add_to_history(category, summary, 'Video Classification')
    except Exception as e:
        pass


elif option == "View History":
    try:
        st.header('History Dashboard')
        if st.session_state.history:
            st.write("### Previous Classifications")
            st.table(st.session_state.history)
        else:
            st.write("No history available.")
    except Exception as e:
        pass  # Suppress all errors
