import yaml
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# SPOTIFY API KEYS CONFIG
try:
    with open("api_keys.yaml", "r") as file:
        api_keys = yaml.safe_load(file)
    CLIENT_ID = api_keys["client_id"]
    CLIENT_SECRET = api_keys["client_secret"]
except:
    print("api_keys.yaml file not found. Create it or add environment variables CLIENT_ID and CLIENT_SECRET.")

SPOTIFY_GREEN = "#1DB954"


@st.experimental_memo
def load_df(path_csv: str):
    return pd.read_csv(path_csv)


@st.experimental_memo
def plot_scatter(df, x, y, color, size, color_continuous_scale="Tealgrn"):
    return px.scatter(df, x=x, y=y, color=color, size=size, color_continuous_scale=color_continuous_scale)


@st.experimental_memo
def plot_corr(df, x, method="pearson", color_continuous_scale="Tealgrn"):
    corr_matrix = df.corr(method=method)
    return px.imshow(corr_matrix, x=x, color_continuous_scale=color_continuous_scale)


@st.experimental_memo
def plot_polar(df_1, df_2, chosen_decade, song_name, release_date):
    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=df_1["value"],
            theta=df_1["variable"],
            fill="toself",
            name=f"Decade {chosen_decade} average",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=df_2["value"],
            theta=df_2["variable"],
            fill="toself",
            name=f"{song_name}, {release_date}",
            # fillcolor=SPOTIFY_GREEN,
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        width=700,
        height=500,
        margin=dict(
            l=100,
            r=0,
            b=0,
            t=0,
            pad=5,
        ),
    )

    return fig


@st.experimental_singleton
def get_spotipy_session(client_id: str = CLIENT_ID, client_secret: str = CLIENT_SECRET):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp


# ================
# STREAMLIT CONFIG
# ================

st.set_page_config(
    page_title="Spotify Data Explorer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     "Get Help": "https://www.extremelycoolapp.com/help",
    #     "Report a bug": "https://www.extremelycoolapp.com/bug",
    #     "About": "# This is a header. This is an *extremely* cool app!",
    # },
)

# ===============
# SPOTIPY SESSION
# ===============

sp = get_spotipy_session()

# ============
# PAGE LAYOUT
# ============

with st.sidebar:
    header_ctn = st.container()
    st.write("-----------------------------")
    st.write("## What are we exploring today?")
    user_input_ctn = st.container()
    st.write("-----------------------------")
    info_ctn = st.container()

popup_ctn = st.container()
main_ctn = st.container()
footer_ctn = st.container()

# -------
# SIDEBAR
# -------

with user_input_ctn:
    page_selector = st.selectbox(
        "Select the desired page",
        ["Song examiner", "Popularity"],
    )

# -------
# HEADER
# -------

with header_ctn:
    st.write(
        """
    # Spotify data explorer
    ### by Caio Lang
    Using [Streamlit](https://streamlit.io/), the [Spotify Web API](https://developer.spotify.com/documentation/web-api/), [Spotypy](https://spotipy.readthedocs.io/en/2.19.0/) and [Plotly](https://plotly.com/python/).

    Have fun! 😃
    """
    )

# -----------------------
# DATAFRAME MANIPULATION
# -----------------------

# df_tracks = load_df("data/tracks.csv")

df_tracks_1 = load_df("data/tracks_1.csv")
df_tracks_2 = load_df("data/tracks_2.csv")

df_tracks = pd.concat([df_tracks_1, df_tracks_2])

df_tracks.dropna()
# st.dataframe(df_tracks.head(100))

# Only 71 null values in the value
# st.write(pd.isnull(df_tracks).sum().sum())

# Add year column, parsing it from release_date column
year = df_tracks["release_date"].apply(lambda x: x.split("-")[0])
df_tracks.insert(loc=8, column="year", value=pd.to_numeric(year))

# Add decade column
decade = df_tracks["year"].apply(lambda x: x - x % 10)
df_tracks.insert(loc=5, column="decade", value=pd.to_numeric(decade))


df_tracks["popularity"] = pd.to_numeric(df_tracks["popularity"])
df_tracks["danceability"] = pd.to_numeric(df_tracks["danceability"])
df_tracks["energy"] = pd.to_numeric(df_tracks["energy"])
df_tracks["mode"] = pd.to_numeric(df_tracks["mode"])
df_tracks["time_signature"] = pd.to_numeric(df_tracks["time_signature"])
df_tracks["explicit"] = pd.to_numeric(df_tracks["explicit"])


# ==============
# SONG EXAMINER
# ==============

if page_selector == "Song examiner":
    with main_ctn:
        track_ctn = st.container()
        st.write("----------------------")
        artist_ctn = st.container()

        try:
            with track_ctn:
                st.write("## Choose a song and then compare it to a decade!")

                cols = st.columns([3, 5])

                with cols[0]:

                    track_name = st.text_input("Search for a track", value="Smoke on the Water")
                    search_result = sp.search(q=f"track:{track_name}", type="track", limit=3)

                    # Fetching song, artist and album information
                    song_name = search_result["tracks"]["items"][0]["name"]
                    song_url = search_result["tracks"]["items"][0]["preview_url"]
                    artist_name = search_result["tracks"]["items"][0]["artists"][0]["name"]
                    artist_url = search_result["tracks"]["items"][0]["artists"][0]["external_urls"]["spotify"]
                    album_name = search_result["tracks"]["items"][0]["album"]["name"]
                    album_url = search_result["tracks"]["items"][0]["album"]["external_urls"]["spotify"]
                    album_img_url = search_result["tracks"]["items"][0]["album"]["images"][1]["url"]
                    release_date = search_result["tracks"]["items"][0]["album"]["release_date"]

                    st.image(album_img_url)

                    # Song information and Spotify links
                    st.write(
                        f"""
                        ## {song_name}
                        ### [🔊]({artist_url}) {artist_name}
                        [💿]({album_url}) _{album_name}, {release_date}_
                        """
                    )

                    # Player with 30s snippet
                    st.audio(song_url)

                with cols[1]:

                    track_id = search_result["tracks"]["items"][0]["id"]
                    audio_feat = sp.audio_features(track_id)[0]

                    df_song_feats = pd.DataFrame(
                        dict(
                            variable=[
                                "danceability",
                                "energy",
                                "speechiness",
                                "acousticness",
                                "instrumentalness",
                                "liveness",
                                "valence",
                            ],
                            value=[
                                audio_feat["danceability"],
                                audio_feat["energy"],
                                audio_feat["speechiness"],
                                audio_feat["acousticness"],
                                audio_feat["instrumentalness"],
                                audio_feat["liveness"],
                                audio_feat["valence"],
                            ],
                        )
                    )

                    df_decades = df_tracks.groupby("decade").mean().reset_index()

                    # User input of decade
                    chosen_decade = st.selectbox("Decade to compare", df_decades["decade"])

                    columns_to_ignore = [
                        "duration_ms",
                        "decade",
                        "year",
                        "tempo",
                        "mode",
                        "key",
                        "time_signature",
                        "loudness",
                        "popularity",
                        "explicit",
                    ]

                    df_decade_feats = df_decades.query(f"decade == '{chosen_decade}'").drop(columns=columns_to_ignore).melt()

                    fig = plot_polar(df_decade_feats, df_song_feats, chosen_decade=chosen_decade, song_name=song_name, release_date=release_date)
                    st.plotly_chart(fig)

                st.write("## Audio features:")
                num_decimals = 3
                cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
                cols[0].metric("⚡ Energy", round(audio_feat["energy"], num_decimals))
                cols[1].metric("🕺🏽 Danceability", round(audio_feat["danceability"], num_decimals))
                cols[2].metric("🎻 Acousticness", round(audio_feat["acousticness"], num_decimals))
                cols[3].metric("🎼 Instrumentalness", round(audio_feat["instrumentalness"], num_decimals))
                cols[4].metric("🎫 Liveness", round(audio_feat["liveness"], num_decimals))
                cols[5].metric("😃 Valence", round(audio_feat["valence"], num_decimals))
                cols[6].metric("🎤 Speechiness", round(audio_feat["speechiness"], num_decimals))

                cols[7].metric("🔊 Loudness", round(audio_feat["loudness"], num_decimals))
                cols[8].metric("⏰ Tempo", int(audio_feat["tempo"]))
                duration_s = audio_feat["duration_ms"] / 1000
                cols[9].metric("⏳ Duration", str(f"{int(duration_s//60)}:{round(duration_s%60)}"))

        except IndexError:
            popup_ctn.error(":warning: Song not found, please try again.")

# -----------
# POPULARITY
# -----------

if page_selector == "Popularity":
    with main_ctn:
        df_popular = df_tracks[df_tracks["popularity"] > 80]

        st.write("## How do the different features* of a song impact its popularity?")
        st.info(
            """*To better understand what are these *features*,
        take a look at the _See metrics definitions_
        section at the bottom of this page!"""
        )

        df_pop_dance = df_tracks.groupby("popularity")["danceability"].mean().sort_values(ascending=[False]).reset_index()
        df_pop_inst = df_tracks.groupby("popularity")["instrumentalness"].mean().sort_values(ascending=[False]).reset_index()

        col_left, col_right = st.columns(2)

        with col_left:
            st.write("### Danceability VS Popularity")
            st.plotly_chart(
                plot_scatter(
                    df_pop_dance,
                    x="popularity",
                    y="danceability",
                    color="danceability",
                    size="danceability",
                )
            )

        with col_right:
            st.write("### Instrumentalness VS Popularity")
            st.plotly_chart(
                plot_scatter(
                    df_pop_inst,
                    x="popularity",
                    y="instrumentalness",
                    color="instrumentalness",
                    size="instrumentalness",
                )
            )

        st.write("### Correlation between all features")
        param_list = [
            "popularity",
            "duration_ms",
            "explicit",
            "decade",
            "year",
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "time_signature",
        ]

        st.plotly_chart(plot_corr(df_tracks, x=param_list))
        st.write(
            """
            For positive values, the correlation is positive
            (if one parameter increases, the other also tends to increase).
            The most relevant correlations with *popularity* are:
            """
        )
        st.success("📈 POSITIVE : *year*, *loudness*, *energy*, *explicit* and *danceability*")
        st.error("📉 NEGATIVE : *acousticness* and *instrumentalness*")

        st.write(
            """
            ### Insights:
            """
        )

        st.info(
            "🔊 The *loudness*/*popularity* correlation can be related to the famous *[loudness war](https://en.wikipedia.org/wiki/Loudness_war)*!"
        )
        st.info("🗓️ The most popular songs were launched recently (which explains the *year*/*popularity* correlation)")
        st.info("🤬 *Explicit* songs tend to be more popular!")
        st.info("🕺🏽 *Danceable* and *energetic* songs are good bets for popular songs (but this we could imagine, right?)")
        st.warning("🎻 *Acoustic* and *instrumental* tracks tend to be less popular")

# -------
# FOOTER
# -------

with footer_ctn:
    with st.expander("See the features' definitions"):
        cols = st.columns(2)
        with cols[0]:
            st.write(
                """
                #### 🎻 Acousticness
                A confidence measure from 0.0 to 1.0 of whether the track is acoustic.
                1.0 represents high confidence the track is acoustic.

                #### 🕺🏽 Danceability
                Describes how suitable a track is for dancing based on a combination
                of musical elements including tempo, rhythm stability, beat strength, and overall regularity.
                A value of 0.0 is least danceable and 1.0 is most danceable.

                #### ⚡ Energy
                Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity.
                Typically, energetic tracks feel fast, loud, and noisy.

                #### 🎼 Instrumentalness
                Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated
                as instrumental in this context. Rap or spoken word tracks are clearly “vocal.”
                The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content.
                Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
                """
            )

        with cols[1]:
            st.write(
                """
                #### 🎫 Liveness
                Detects the presence of an audience in the recording. Higher liveness values represent
                an increased probability that the track was performed live. A value above 0.8 provides strong likelihood
                that the track is live.

                #### 🎤 Speechiness
                Speechiness detects the presence of spoken words in a track. The more exclusively speech-like
                the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value.
                Values above 0.66 describe tracks that are probably made entirely of spoken words.
                Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered,
                including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.

                #### ⏰ Tempo
                The overall estimated tempo of a track in beats per minute (BPM). In musical terminology,
                tempo is the speed or pace of a given piece and derives directly from the average beat duration.

                #### 😃 Valence
                A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
                Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence
                sound more negative (e.g. sad, depressed, angry).
                """
            )

        st.write(
            "Source: [Spotify Web API documentation](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features)"
        )

# -------
# INFO
# -------

with info_ctn:
    with st.expander("Sources/Inspiration"):
        st.write(
            """
        - [lehaknarnauli @Kaggle](https://www.kaggle.com/lehaknarnauli/spotify-datasets) | Dataset
        - [Spotify Web API](https://developer.spotify.com/documentation/web-api/) | Documentation
        - [Datascience.fm](https://datascience.fm/fun-analysis-of-spotify-dataset-to-gain-insights-on-music-industry/) | Data analysis
        
        """
        )
