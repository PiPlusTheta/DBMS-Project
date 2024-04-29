import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Set page title and favicon
st.set_page_config(
    page_title="Movie Database Management",
    page_icon="🎬",
    layout="wide"
)

# Function to fetch data from Google Sheets
def fetch_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(ttl=5).dropna(how="all")
    return data.iloc[:, :10]  # Select only the first 10 columns

# Function to update data in Google Sheets
def update_data(data):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(data=data)

# Main function to display the app
def main():
    # Set up sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["View All Movies", "Add New Movie", "Update Existing Movie", "Delete Movie"]
    )

    # Set page title
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>Movie Database Management Portal</h1>", unsafe_allow_html=True)

    if page == "Add New Movie":
        st.markdown("## Add New Movie")
        existing_data = fetch_data()
        with st.form(key="movie_form"):
            title = st.text_input(label="Title*", placeholder="Enter movie title")
            genre = st.selectbox("Genre*", options=existing_data["genre"].unique())
            director = st.text_input(label="Director*", placeholder="Enter director's name")
            country = st.selectbox("Country*", options=existing_data["country"].unique())
            release_year = st.number_input(label="Release Year*", min_value=1900, max_value=2100)
            rating = st.number_input(label="Rating*", min_value=0.0, max_value=10.0, step=0.1)
            duration = st.number_input(label="Duration (minutes)*", min_value=0)
            language = st.selectbox("Language*", options=existing_data["language"].unique())
            main_actor = st.text_input(label="Main Actor", placeholder="Enter main actor's name")

            submit_button = st.form_submit_button(label="Submit Movie Details")

            if submit_button:
                if not title or not director:
                    st.error("Please fill in all mandatory fields.")
                elif existing_data["title"].str.contains(title).any():
                    st.error("A movie with this title already exists.")
                else:
                    max_id = existing_data["movie_id"].max() if "movie_id" in existing_data.columns else 0
                    movie_id = max_id + 1

                    movie_data = pd.DataFrame(
                        [
                            {
                                "movie_id": movie_id,
                                "title": title,
                                "genre": genre,
                                "director": director,
                                "country": country,
                                "release_year": release_year,
                                "rating": rating,
                                "duration": duration,
                                "language": language,
                                "main_actor": main_actor,
                            }
                        ]
                    )
                    existing_data = pd.concat([existing_data, movie_data], ignore_index=True)
                    update_data(existing_data)
                    st.success("Movie details successfully added!")

    elif page == "Update Existing Movie":
        st.markdown("## Update Existing Movie")
        existing_data = fetch_data()
        movie_to_update = st.selectbox(
            "Select a Movie to Update", options=existing_data["title"].tolist()
        )
        movie_data = existing_data[existing_data["title"] == movie_to_update].iloc[0]

        with st.form(key="update_form"):
            movie_id = st.number_input(label="ID", value=int(movie_data["movie_id"]), min_value=0, step=1)
            title = st.text_input(label="Title*", value=movie_data["title"], placeholder="Enter movie title")
            genre = st.text_input(label="Genre*", value=movie_data["genre"], placeholder="Enter movie genre")
            director = st.text_input(label="Director*", value=movie_data["director"], placeholder="Enter director's name")
            country = st.text_input(label="Country*", value=movie_data["country"], placeholder="Enter country")
            release_year = st.number_input(
                label="Release Year*", value=int(movie_data["release_year"]), min_value=1900, max_value=2100, step=1
            )
            rating = st.number_input(
                label="Rating*", value=float(movie_data["rating"]), min_value=0.0, max_value=10.0, step=0.1
            )
            duration = st.number_input(
                label="Duration (minutes)*", value=int(movie_data["duration"]), min_value=0, step=1
            )
            language = st.text_input(label="Language*", value=movie_data["language"], placeholder="Enter movie language")
            main_actor = st.text_input(label="Main Actor", value=movie_data["main_actor"], placeholder="Enter main actor's name")

            update_button = st.form_submit_button(label="Update Movie Details")

            if update_button:
                if not title or not director:
                    st.error("Please fill in all mandatory fields.")
                else:
                    updated_movie_data = pd.DataFrame(
                        [
                            {
                                "movie_id": movie_id,
                                "title": title,
                                "genre": genre,
                                "director": director,
                                "country": country,
                                "release_year": release_year,
                                "rating": rating,
                                "duration": duration,
                                "language": language,
                                "main_actor": main_actor,
                            }
                        ]
                    )
                    existing_data = existing_data.drop(
                        existing_data[existing_data["movie_id"] == movie_id].index, inplace=False
                    )
                    existing_data = pd.concat(
                        [existing_data, updated_movie_data], ignore_index=True
                    )
                    update_data(existing_data)
                    st.success("Movie details successfully updated!")

    elif page == "View All Movies":
        st.markdown("## All Movies")
        existing_data = fetch_data()
        st.dataframe(existing_data)

    elif page == "Delete Movie":
        st.markdown("## Delete Movie")
        existing_data = fetch_data()
        movie_to_delete = st.selectbox(
            "Select a Movie to Delete", options=existing_data["title"].tolist()
        )

        if st.button("Delete"):
            existing_data = existing_data.drop(
                existing_data[existing_data["title"] == movie_to_delete].index, inplace=False
            )
            update_data(existing_data)
            st.success("Movie successfully deleted!")

# Run the app
if __name__ == "__main__":
    main()
