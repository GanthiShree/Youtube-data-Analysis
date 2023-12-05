import googleapiclient.discovery
import pymongo
import pymysql
import pandas as pd
import datetime
import isodate
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
# API connection:
api_service_name = "youtube"
api_version = "v3"
key = "AIzaSyDPnusHFbCmmEvHykqzk55ch2fM5LTleVg"
youtube = googleapiclient.discovery.build(
api_service_name, api_version, developerKey =key) 


# mongoDB connection:
mongo_client  = pymongo.MongoClient("mongodb://localhost:27017")
mongo_db  = mongo_client["Youtube"]
myconnection = mongo_db["Channel_Details"]


# My SQL connection:
mysql_connection  =  pymysql.connect(host = "127.0.0.1",
                                user='root',
                                passwd='Nisha@130899',
                                database ="Youtube_Data",
                                autocommit=True)                                
mysql_cursor  = mysql_connection.cursor()
mongo_data = myconnection.find()

# Channel Information:
def channel_info(channel_id):
        request = youtube.channels().list(
                part="snippet,contentDetails,statistics,status",
                id= channel_id)
        response = request.execute()

        for i in response["items"]:
            details = dict(Channel_id = i["id"],
                           Channel_Name = i["snippet"]["title"],
                           Channel_Type = i["status"].get("privacyStatus"),
                           subscribers_count = i["statistics"]["subscriberCount"],
                           Total_view_count = i["statistics"]["viewCount"],
                           Total_video_count = i["statistics"]["videoCount"],
                           Playlist_ID = i["contentDetails"]["relatedPlaylists"]["uploads"] )
        return details

# Playlist Information:
def playlist_Details(channel_id):
    playlist_details = []
    next_page_token = None
    while True:
        request = youtube.playlists().list(
                                part = "snippet , contentDetails",
                                channelId = channel_id,
                                maxResults = 50,
                                pageToken = next_page_token)
        response = request.execute()
        for i in response["items"]:
            data = dict(
                        Channel_id = i["snippet"]["channelId"],
                        Channel_Name = i["snippet"]["channelTitle"],
                        Playlist_id = i["id"],
                        Playlist_Name = i["snippet"]["title"],
                        Video_Count = i["contentDetails"]["itemCount"]
                        )
            playlist_details.append(data)
        next_page_token  = response.get("nextPageToken")
        if next_page_token is None:
            break
    return playlist_details

# Video Id:
def get_video_Id(channel_id):
    video_id = []
    request = youtube.channels().list(
                    part = "snippet,contentDetails,statistics",
                    id = channel_id ).execute()
    playlist_id = request["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    NextPageToken = None

    while True: # because first page dont have nextPageToken
        request1 = youtube.playlistItems().list(
                        part = "snippet",
                        playlistId = playlist_id,
                        maxResults = 50, # max is 50 as per youtube data API
                        pageToken = NextPageToken ).execute()
        for i in range(len(request1["items"])):
            video_id.append(request1["items"][i]["snippet"]["resourceId"]["videoId"])
        NextPageToken = request1.get("nextPageToken")
        if NextPageToken is None:
            break
    return video_id
 
 # Video Details:
def get_video_details(video_id):
    Video_Details = []
    for i in video_id:
        request = youtube.videos().list(
                part = "snippet,contentDetails,statistics",
                id = i)
        response = request.execute()
        try:
            for i in response["items"]:
                data = dict(
                    Channel_name = i["snippet"]["channelTitle"],
                    video_id = i["id"],
                    Video_Name = i["snippet"]["title"],
                    Video_Description = i["snippet"]["description"],
                    Tags = i["snippet"].get("tags",0),
                    Publish_At = i["snippet"]["publishedAt"],
                    View_Count = i["statistics"]["viewCount"],
                    Like_Count = i["statistics"].get("likeCount", 0),
                    Favorite_count = i["statistics"].get("favoriteCount",0),
                    Comment_count = i["statistics"]["commentCount"],
                    Duration = i["contentDetails"]["duration"],
                    Thumbnails = i["snippet"]["thumbnails"]["default"]["url"],
                    Caption_Status = i["contentDetails"]["caption"]
                )
                Video_Details.append(data)
        except:
            print("error in getting video details")
    return Video_Details

# Comment Details:
def get_comment_details(video_id):
    try:
        comment_details = []
        for i in video_id:        
            request = youtube.commentThreads().list(
                    part = "snippet",
                    videoId = i,
                    maxResults = 50 )
            response = request.execute()

            for i in response["items"]:
                data = dict(
                            Comment_ID = i["id"],
                            video_id = i["snippet"]["videoId"],
                            Comment_text = i["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                            Comment_Author = i["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                            Comment_Published_data = i["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                            )
                comment_details.append(data)
        return comment_details
    except:
        pass

 
# Storing data in MongoDb:
def Channel_Details(channel_id):
    chn_info = channel_info(channel_id)
    ply_info = playlist_Details(channel_id)
    video_id  = get_video_Id(channel_id)
    vid_info = get_video_details(video_id)
    cmt_info = get_comment_details(video_id)
    
    collection = mongo_db["Channel_Details"]
    collection.insert_one({"Channel_information":chn_info ,"Playlist_information":ply_info ,
                            "Video_information":vid_info , "Comment_information" :cmt_info})
    return "Uploaded Successfully"

# migrating to SQL:
def channel():
    all_ch_data = []
    for document in mongo_data:
        ch_info = document.get("Channel_information", {})    
        all_ch_data.append(ch_info)
    # SQL channel table creation 
    try:
        create_query  = """CREATE TABLE IF NOT EXISTS channel(
                                                            Channel_id varchar(100) primary key,
                                                            Channel_Name varchar(100),
                                                            Channel_Type varchar(100),
                                                            subscribers_count bigint,
                                                            Total_view_count int,
                                                            Total_video_count int,
                                                            Playlist_ID varchar(100) )"""
        mysql_cursor.execute(create_query)
        mysql_connection.commit()

        for channel_data in all_ch_data:
            mysql_cursor.execute('SELECT * FROM channel WHERE Channel_id = %s', (channel_data['Channel_id'],))
            existing_channel_id = mysql_cursor.fetchone()

            if existing_channel_id:
                continue
            else:
                mysql_cursor.execute('''
                    INSERT INTO channel (Channel_id, 
                                        Channel_Name, 
                                        subscribers_count, 
                                        Total_view_count, 
                                        Total_video_count,
                                        Playlist_ID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    channel_data['Channel_id'],
                    channel_data['Channel_Name'],
                    channel_data['subscribers_count'],
                    channel_data['Total_view_count'],
                    channel_data['Total_video_count'],
                    channel_data['Playlist_ID']
                ))

        mysql_connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

def playlist():
    all_pl_data = []

    for document in mongo_data:
        pl_info = document.get("Playlist_information", {})    
        for channel in pl_info:
            all_pl_data.append(channel)

    # SQL Playlist table creation 
    try:
        create_query  = """CREATE TABLE IF NOT EXISTS playlist(
                                                            Channel_id varchar(100),
                                                            Channel_Name varchar(100),
                                                            Playlist_id varchar(100) primary key,
                                                            Playlist_Name varchar(100),
                                                            Video_Count int )"""
        mysql_cursor.execute(create_query)
        mysql_connection.commit()

        for playlist_data in all_pl_data:
            mysql_cursor.execute('SELECT * FROM playlist WHERE Playlist_id = %s',
                                     (playlist_data['Playlist_id'],))
            existing_playlist = mysql_cursor.fetchone()

            if existing_playlist:
                continue
            else:
                mysql_cursor.execute('''
                    INSERT INTO playlist (Channel_id, Channel_Name, Playlist_id, Playlist_Name, Video_Count)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    playlist_data['Channel_id'],
                    playlist_data['Channel_Name'],
                    playlist_data['Playlist_id'],
                    playlist_data['Playlist_Name'],
                    playlist_data['Video_Count']
                ))

        mysql_connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

def video():  
    all_vi_data = []
    for document in mongo_data:
        vi_info = document.get("Video_information", {}) 
        for data in vi_info:
            all_vi_data.append(data)

    # SQL video table creation 
    try:
        create_query  = """CREATE TABLE IF NOT EXISTS video(
                                                            Channel_name varchar(100),
                                                            video_id varchar(100) primary key,
                                                            Video_Name varchar(100),
                                                            Video_Description LONGTEXT,
                                                            Tags text,
                                                            Publish_At datetime,
                                                            View_Count int,
                                                            Like_Count bigint,
                                                            Favorite_count int,
                                                            Comment_count int,
                                                            Duration text,
                                                            Thumbnails text,
                                                            Caption_Status varchar(50))"""
        mysql_cursor.execute(create_query)
        mysql_connection.commit()

        for video_data in all_vi_data:

            mysql_cursor.execute('SELECT * FROM video WHERE video_id = %s', (video_data['video_id'],))
            existing_video_id = mysql_cursor.fetchone()

            if existing_video_id is not None:
                continue
            else:
                tags_string = ', '.join(video_data['Tags']) if video_data['Tags'] else None
                Publish_At = datetime.datetime.strptime(video_data['Publish_At'],
                                                                '%Y-%m-%dT%H:%M:%SZ')
                duration_str = video_data['Duration']
                duration_obj = isodate.parse_duration(duration_str)

                # Format duration as hh:mm:ss
                formatted_duration = str(duration_obj).split(", ")[-1]  # Extracting the time part
                formatted_duration = formatted_duration[:8]  # Extracting hh:mm:ss
                mysql_cursor.execute('''
                    INSERT INTO video (Channel_name,video_id ,Video_Name ,Video_Description ,
                                        Tags ,Publish_At ,View_Count ,Like_Count ,Favorite_count ,
                                        Comment_count ,Duration ,Thumbnails ,Caption_Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    video_data['Channel_name'],
                    video_data['video_id'],
                    video_data['Video_Name'],
                    video_data['Video_Description'],
                    tags_string,
                    Publish_At,
                    video_data['View_Count'],
                    video_data['Like_Count'],
                    video_data['Favorite_count'],
                    video_data['Comment_count'],
                    formatted_duration,
                    video_data['Thumbnails'],
                    video_data['Caption_Status']                
                ))

        mysql_connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

def comment():
    all_cmt_data = []

    for document in mongo_data:
        cmt_info = document.get("Comment_information", {}) 
        if cmt_info is not None:
            for data in cmt_info:
                all_cmt_data.append(data)
        else:
            continue

    create_query  = """CREATE TABLE IF NOT EXISTS comment(                                                    
                                                        Comment_ID varchar(255),
                                                        video_id varchar(255),
                                                        Comment_text LONGTEXT,
                                                        Comment_Author text,
                                                        Comment_Published_data datetime) """
    mysql_cursor.execute(create_query)
    mysql_connection.commit()

    for cmt_data in all_cmt_data:
        mysql_cursor.execute('SELECT * FROM comment WHERE Comment_ID = %s', (cmt_data['Comment_ID'],))
        existing_comment = mysql_cursor.fetchone()

        if existing_comment:
            continue
        else:
            comment_published_data = datetime.datetime.strptime(cmt_data['Comment_Published_data'],
                                                                '%Y-%m-%dT%H:%M:%SZ')

            mysql_cursor.execute('''
                INSERT INTO comment (Comment_ID, video_id, Comment_text, Comment_Author, 
                                    Comment_Published_data)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                cmt_data['Comment_ID'],
                cmt_data['video_id'],
                cmt_data['Comment_text'],
                cmt_data['Comment_Author'],
                comment_published_data
            ))

            mysql_connection.commit()

def tables():
    channel()
    playlist()
    video()
    comment()
    return "Table created successfully" 

def display_channel_data(channel_id):
    with st.spinner('Fetching Channel Data, Please Wait...'):
        chn_info = channel_info(channel_id)
        ply_info = playlist_Details(channel_id)
        video_id = get_video_Id(channel_id)
        vid_info = get_video_details(video_id)
        cmt_info = get_comment_details(video_id)

        st.write("Channel Information:")
        st.write(f"Channel Name: {chn_info['Channel_Name']}")
        st.write(f"Channel ID: {chn_info['Channel_id']}")
        st.write(f"Subscribers: {chn_info['subscribers_count']}")
        st.write(f"Views: {chn_info['Total_view_count']}")
        st.write(f"Total Videos: {chn_info['Total_video_count']}")


        st.success("Data fetched successfully.")
# Building code for streamlit:
with st.sidebar:
    selected = option_menu(
                menu_title = None,
                options = ["Home","Extract Data","Views"],
                icons = ["house","database-fill-check","folder2"],
                default_index = 0)
if selected =="Home":
    st.title(":rainbow[YouTube Channel Data Analysis]")
    st.markdown("""
    - **Input YouTube channel IDs.**
    - **Fetch channel data, display information, and store data in MongoDB.**
    - **Migrate data to MySQL.**
    - **Query and display analysis results using predefined SQL queries.**
    """)
if selected == "Extract Data":
    with st.form("channel_form"):
        # Get user input for YouTube channel ID :
        new_channel_id = st.text_input("Enter YouTube Channel ID:")
        st.caption("###### Hint : Go to channel's home page > Right click > View page source > Find channel_id")
        # Button to add channel ID to the list and fetch details
        add_button = st.form_submit_button("Add Channel ID")

    if 'channel_ids_list' not in st.session_state:
        st.session_state['channel_ids_list'] = []

    if add_button:
        if new_channel_id:
            if new_channel_id in st.session_state.channel_ids_list:
                st.warning(f"Channel ID {new_channel_id} is already in the list. Provide another channel ID.")
            else:
                st.session_state.channel_ids_list.append(new_channel_id)
                st.success(f"Channel ID {new_channel_id} added successfully in the list!")

    # Dropdown to select channel ID from the list
    selected_channel_id = st.selectbox("Select Channel ID:", st.session_state.channel_ids_list)

    # Button to fetch and display channel data
    if st.button("Fetch Channels Data"):
        display_channel_data(selected_channel_id)
    # Inserting data to MongoDb:
    if st.button("Insert Data into MongoDB"):
        with st.spinner('Inserting Data into MongoDB, Please Wait...'):
            channel_id = selected_channel_id
            if channel_id:
                insert = Channel_Details(channel_id)
                st.success("Data inserted into MongoDB successfully.")
            else:
                    st.warning("Fetch channel data first.")

    # Button to migrate data from MongoDB to SQL:
    if st.button("Migrate Data to SQL"):
        with st.spinner('Migrating Data into SQL, Please Wait...'):
            tables() 
            st.success("Data migrated to SQL successfully.")

if selected == "Views":
# Dictionary containing questions and corresponding SQL queries
    queries = {
        "1. What are the names of all the videos and their corresponding channels?": """
            SELECT v.Video_Name, c.Channel_Name
            FROM video v
            JOIN channel c ON v.Channel_name = c.Channel_Name;
        """,
        "2. Which channels have the most number of videos, and how many videos do they have?": """
            SELECT c.Channel_Name, COUNT(v.video_id) AS NumberOfVideos
            FROM channel c
            JOIN video v ON c.Channel_Name = v.Channel_name
            GROUP BY c.Channel_Name
            ORDER BY NumberOfVideos DESC;
        """,
        "3. What are the top 10 most viewed videos and their respective channels?": """
        SELECT v.Video_Name, v.View_Count, c.Channel_Name
            FROM video v
            JOIN channel c ON v.Channel_name = c.Channel_Name
            ORDER BY v.View_Count DESC
            LIMIT 10;
        """,
        "4. How many comments were made on each video, and what are their corresponding video names?": """
            SELECT v.Video_Name, COUNT(c.Comment_ID) AS CommentCount
            FROM video v
            LEFT JOIN comment c ON v.video_id = c.video_id
            GROUP BY v.Video_Name 
            ORDER BY  CommentCount DESC;
        """,
        "5. Which videos have the highest number of likes, and what are their corresponding channel names?": """
            SELECT v.Video_Name, v.Like_Count, c.Channel_name
            FROM video v
            JOIN channel c ON v.Channel_name = c.Channel_name
            ORDER BY v.Like_Count DESC
            LIMIT 10;
        """,
        "6. What is the total number of likes for each video, and what are their corresponding video names?": """
            SELECT v.Video_Name, SUM(v.Like_Count) AS TotalLikes
            FROM video v
            GROUP BY v.Video_Name;
        """,
        "7. What is the total number of views for each channel, and what are their corresponding channel names?": """
            SELECT c.Channel_Name, SUM(v.View_Count) AS TotalViews
            FROM channel c
            JOIN video v ON c.Channel_Name = v.Channel_name
            GROUP BY c.Channel_Name;
        """,
        "8. What are the names of all the channels that have published videos in the year 2022?": """
            SELECT DISTINCT c.Channel_Name
            FROM channel c
            JOIN video v ON c.Channel_Name = v.Channel_name
            WHERE YEAR(v.Publish_At) = 2022;
        """,
        "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?": """
            SELECT c.Channel_Name, AVG(TIME_TO_SEC(v.Duration)) / 60 AS Average_Duration_InMinutes
            FROM channel c
            JOIN video v ON c.Channel_Name = v.Channel_name
            GROUP BY c.Channel_Name;
        """,
        "10. Which videos have the highest number of comments, and what are their corresponding channel names?": """
            SELECT v.Video_Name, COUNT(c.Comment_ID) AS CommentCount, v.Channel_name
            FROM video v
            LEFT JOIN comment c ON v.video_id = c.video_id
            GROUP BY v.Video_Name, v.Channel_name
            ORDER BY CommentCount DESC
            LIMIT 10;
        """
    }
    selected_query = st.selectbox("Select any Analysis you want to know about :", list(queries.keys()))

    mysql_cursor = mysql_connection.cursor()

    # Button to fetch answers for selected query:

    if st.button("Fetch Answer"):
        with st.spinner('Executing Query, Please Wait...'):
            try:
                query = queries[selected_query]
                result_df = pd.read_sql(query, mysql_connection)
                if selected_query == "2. Which channels have the most number of videos, and how many videos do they have?":
                    # Bar chart for question 2
                    fig_bar_channel_videos, ax_bar_channel_videos = plt.subplots()
                    ax_bar_channel_videos.bar(result_df["Channel_Name"], result_df["NumberOfVideos"], color="skyblue")
                    ax_bar_channel_videos.set_ylabel("Number of Videos")
                    ax_bar_channel_videos.set_title("Channels with the Most Number of Videos")

                    st.subheader("Channels with the Most Number of Videos")
                    st.pyplot(fig_bar_channel_videos)

                elif selected_query == "3. What are the top 10 most viewed videos and their respective channels?":
                    fig_bar_views, ax_bar_views = plt.subplots()
                    ax_bar_views.barh(result_df["Video_Name"], result_df["View_Count"], color="skyblue")
                    ax_bar_views.set_xlabel("Number of Views")
                    ax_bar_views.set_title("Top 10 Most Viewed Videos")

                    st.subheader("Top 10 Most Viewed Videos")
                    st.pyplot(fig_bar_views)

                elif selected_query == "5. Which videos have the highest number of likes, and what are their corresponding channel names?":
                    # Bar chart for question 5
                    fig_bar_likes, ax_bar_likes = plt.subplots()
                    ax_bar_likes.barh(result_df["Video_Name"], result_df["Like_Count"], color="pink")
                    ax_bar_likes.set_xlabel("Number of Likes")
                    ax_bar_likes.set_title("Videos with the Highest Number of Likes")

                    st.subheader("Videos with the Highest Number of Likes")
                    st.pyplot(fig_bar_likes)

                elif selected_query == "10. Which videos have the highest number of comments, and what are their corresponding channel names?":
                    # Bar chart for question 10
                    fig_bar_comments, ax_bar_comments = plt.subplots()
                    ax_bar_comments.barh(result_df["Video_Name"], result_df["CommentCount"], color="red",alpha = 0.6)
                    ax_bar_comments.set_xlabel("Number of Comments")
                    ax_bar_comments.set_title("Videos with the Highest Number of Comments")

                    st.subheader("Videos with the Highest Number of Comments")
                    st.pyplot(fig_bar_comments)

                st.table(result_df)

            except Exception as e:
                st.error(f"An error occurred: {e}")