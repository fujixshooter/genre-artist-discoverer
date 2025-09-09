import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"  # Replace with your deployment name if different

# Initialize Azure OpenAI client
@st.cache_resource
def get_client():
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2023-05-15",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

client = get_client()

# Streamlit app
st.title("Genre-Based Emerging Artist Discoverer")
st.markdown("Select a music genre to discover up-and-coming artists and their new tracks! This uses Azure OpenAI to suggest new talent.")

# Genre dropdown for easy use
genres = ["Blues", "Hip-Hop", "Jazz", "Rock", "Classical", "Electronic", "Pop", "Other"]
selected_genre = st.selectbox("Select Genre:", genres)
if selected_genre == "Other":
    selected_genre = st.text_input("Enter Custom Genre:").strip()

if st.button("Discover New Talent") and selected_genre:
    with st.spinner("Generating recommendations..."):
        try:
            # Prompt for emerging artists - JSON braces escaped as {{ }} in f-string
            prompt = f"""
            Suggest 5 emerging or up-and-coming artists in the {selected_genre} genre who have gained attention in the last 5 years (as of 2025). 
            Avoid well-known mainstream artists. 
            For each artist, provide in JSON format: a list of objects with keys 'Artist Name', 'Brief Description' (1-2 sentences), 'Recommended New Song' (recent track), and 'Why Discover Them' (appeal to fans).
            Example: [{{ "Artist Name": "Example Artist", "Brief Description": "A rising star with soulful vibes.", "Recommended New Song": "New Hit", "Why Discover Them": "Perfect for fans of modern {selected_genre}." }}]
            """
            
            response = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            # Parse and display
            rec_text = response.choices[0].message.content
            parsed_response = json.loads(rec_text)
            
            # Extract the list (AI might wrap it in a dict; adjust if needed)
            if isinstance(parsed_response, dict):
                recommendations = parsed_response.get('recommendations', parsed_response.get('artists', list(parsed_response.values())[0] if parsed_response else []))
            else:
                recommendations = parsed_response
            
            if not recommendations:
                raise ValueError("No recommendations found in response.")
            
            st.success("Here are some emerging talents!")
            for rec in recommendations:
                with st.expander(f"**{rec['Artist Name']}** - {rec['Recommended New Song']}"):
                    st.write(f"**Description:** {rec['Brief Description']}")
                    st.write(f"**Why Discover Them:** {rec['Why Discover Them']}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}. Check your Azure setup or try again.")

st.markdown("---")
st.caption("Built with Azure OpenAI. Prototype for portfolio.")