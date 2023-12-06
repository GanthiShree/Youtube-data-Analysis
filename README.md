# **YouTube Data Analysis**

## **Overview**

The `Youtube.py` script is a Python tool designed to retrieve and analyze data from YouTube channels. It utilizes the YouTube Data API to fetch information about a specified channels such as its video,title, description, view count, likes, and comments. The fetched information is stored in  MongoDB database, subsequently migrated to a SQL data warehouse and made accessible for analysis and generates visualizations to represent key statistics and insights within the Streamlit app.

## **Features**

### **1. Basic Channel Information Retrieval**

The script can fetch basic information about a YouTube video, including:

- Video
- Title
- Description
- View count
- Like count
- Comment count

### **3. Data Visualization**

The script generates visualizations to represent key statistics and insights about the video. This can include charts and graphs to illustrate metrics like views, likes, and comments.

## **Getting Started**

1. **Clone the Repository:**
   - Use the `git clone` command to clone the repository to your local machine.

2. **Install Required Packages:**
   - Navigate to the project directory and install the required Python packages using `pip install -r requirements.txt`.

3. **Obtain API Key:**
   - Visit the [Google Cloud Console](https://console.developers.google.com/).
   - Create a new project or select an existing project.
   - Enable the YouTube Data API v3 for your project.
   - Create API credentials (API key) and restrict it to the YouTube Data API.

4. **Add API Key to the Script:**
   - Open the `Youtube.py` script in a text editor.
   - Locate the variable `API_KEY` and replace the placeholder `YOUR_API_KEY` with the API key you obtained.

5. **Run the Script:**
   - Execute the script using the command `python Youtube.py`.
   - Follow the prompts to input the YouTube video URL and choose analysis options.

## **Usage**

- When you run the script, it will prompt you to input the URL of the YouTube video you want to analyze.
- The script will then fetch the video information and ask if you want to perform sentiment analysis on the comments or generate visualizations.
- Follow the on-screen instructions to interact with the script.

## **Contributing**

If you encounter any issues or have suggestions for improvement, contributions are welcome! You can open an issue to report problems or submit a pull request with proposed changes.

## **License**

This project is licensed under the MIT License. Refer to the [LICENSE](LICENSE) file for details.
