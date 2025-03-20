# ResumeAI - ATS Optimization Tool
ResumeAI is an advanced Applicant Tracking System (ATS) optimization tool that helps job seekers improve their resumes for specific job applications. Powered by Google's Gemini 2.0 AI, this tool analyzes resumes against job descriptions to provide detailed insights, recommendations, and a match score.

## Features

- **Resume Analysis**: Upload your resume and get it analyzed against specific job descriptions
- **Match Scoring**: Receive a realistic percentage match score between your resume and the job requirements
- **Skills Gap Analysis**: Identify missing keywords and skills categorized by technical skills, soft skills, experience, and education/certifications
- **Professional Summary**: Get an AI-generated professional summary based on your profile
- **Actionable Recommendations**: Receive 3-5 specific suggestions to improve your resume
- **Resume Strengths**: Understand 2-3 key strengths of your resume relative to the job description
- **Critical Skills Insights**: Learn why certain skills/experiences are particularly valuable for the role

## Technologies Used

- **Frontend & App**: Streamlit
- **AI Model**: Google Gemini 2.0 Flash
- **PDF Processing**: PyPDF2
- **Environment Management**: dotenv
- **Language**: Python

## Installation & Setup

1. Clone the repository:
    ```
    git clone https://github.com/anikethhebbar/Resume-AI.git
    cd Resume-AI
    ```

2. Install dependencies on a virtual environment:
    ```
    pip install -r requirements.txt
    ```

3. Create a `.env` file with your Google API key:
    ```
    GOOGLE_API_KEY=your_google_api_key_here
    ```

4. Run the application:
    ```
    python3 streamlit run app.py
    ```

## How to Use

1. **Upload Your Resume**: Select your resume in PDF format
2. **Paste Job Description**: Copy and paste the job description you're interested in
3. **Analyze**: Click "Analyze My Resume" button
4. **Review Results**: Explore the different tabs to see your match score, profile analysis, skills gap, and recommendations
5. **Implement Changes**: Use the insights to improve your resume for the specific job

## Project Structure

- `app.py`: Main application file containing Streamlit UI and core functionality
- `requirements.txt`: List of required Python packages
- `.env`: Environment variables file (needs to be created)
- `app.log`: Application logs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgments

- Google Gemini AI for powering the resume analysis
- Streamlit for the web application framework
