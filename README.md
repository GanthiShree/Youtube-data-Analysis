# **YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit**

## **Overview**

The `Youtube.py` script is a Python tool designed to retrieve and analyze data from YouTube channels. It utilizes the YouTube Data API to fetch information about a specified channels such as its video,title, description, view count, likes, and comments. The fetched information is stored in  MongoDB database, subsequently migrated to a SQL data warehouse and made accessible for analysis and generates visualizations to represent key statistics and insights within the Streamlit app.


## **Features**

### **1. Basic Channel Information Retrieval**

The script can fetch basic information about a YouTube video, including:

- Video
- Title
- View count
- Like count
- Comment count

### **2. Data Visualization**

The script generates visualizations to represent key statistics and insights about the video. This can include charts and graphs to illustrate metrics like views, likes, and comments.

## **Getting Started**

1. **Clone the Repository:**
   - Use the `git clone` command to clone the repository to your local machine.

2. **Install Required Packages:**
   - Navigate to the project directory and install the required packages listed below:
     ```
         pip install google-api-python-client
         pip install pymongo
         pip install pymysql
         pip install pandas
         pip install isodate
         pip install streamlit
        ```

3. **Obtain API Key:**
   - Visit the [Google Cloud Console](https://console.developers.google.com/).
   - Create a new project or select an existing project.
   - Enable the YouTube Data API v3 for your project.
   - Create API credentials (API key) and restrict it to the YouTube Data API.

4. **Add API Key to the Script:**
   - Open the `Youtube.py` script in a text editor.
   - Locate the variable `API_KEY` and replace the placeholder `YOUR_API_KEY` with the API key you obtained.

5. **Run the Script:**
   - Execute the script using the command `streamlit run Youtube.py`.
   - Follow the prompts to input the YouTube video URL and choose analysis options.

## **Usage**

- When you run the script, it will prompt you to input the URL of the YouTube Channel you want to analyze.
- The script will then fetch the Channel information and displays you the Channel information.
- You can store retrieved data in  MongoDB database based on user authorization.
- Users can choose which channel data should store in MongoDB.
- You can migrate the stored data from MongoDB to MySQL data warehouse
- To ensure compatibility with a structured format, the data is cleansed using the powerful pandas library.
- Following data cleaning, the information is segregated into separate tables, including channels, playlists, videos, and comments, utilizing MySQL queries.
- Follow the on-screen instructions to interact with the script.

**Data Analysis**

The project provides comprehensive data analysis capabilities using Plotly and Streamlit. With the integrated Plotly library, users can create interactive and visually appealing charts and graphs to gain insights from the collected data.

- **Channel Analysis:** Channel analysis includes insights on playlists, videos, subscribers, views, likes, comments, and durations. Gain a deep understanding of the channel's performance and audience engagement through detailed visualizations and summaries.

- **Video Analysis:** Video analysis focuses on views, likes, comments, and durations, enabling both an overall channel and specific channel perspectives. Leverage visual representations and metrics to extract valuable insights from individual videos.

Utilizing the power of Plotly, users can create various types of charts, including line charts, bar charts, scatter plots, pie charts, and more. These visualizations enhance the understanding of the data and make it easier to identify patterns, trends, and correlations.

The Streamlit app provides an intuitive interface to interact with the charts and explore the data visually. Users can customize the visualizations, filter data, and zoom in or out to focus on specific aspects of the analysis.

With the combined capabilities of Plotly and Streamlit, the Data Analysis section empowers users to uncover valuable insights and make data-driven decisions.

## **Contributing**

If you encounter any issues or have suggestions for improvement, contributions are welcome! Please feel free to submit a pull request.

## **License**

This project is licensed under the MIT License.
