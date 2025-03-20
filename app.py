import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment variables")
        st.error("API key not configured. Please check your .env file.")
    else:
        genai.configure(api_key=api_key)
        logger.info("Google API configured successfully")
except Exception as e:
    logger.error(f"Error loading environment: {str(e)}")
    st.error(f"Configuration error: {str(e)}")

def get_gemini_response(input_text: str) -> Optional[str]:
    """Generate a response from the Gemini model with proper error handling"""
    logger.info("Generating response from Gemini model")
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(input_text)
        logger.info("Response generated successfully")
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return None

def extract_pdf_text(uploaded_file) -> Optional[str]:
    """Extract and concatenate text from all pages of the given PDF file"""
    logger.info(f"Processing PDF file: {uploaded_file.name}")
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        # Iterate through all the pages
        for page in range(len(reader.pages)):
            page_content = reader.pages[page]
            # Extracting the text
            text += str(page_content.extract_text())
        
        if not text.strip():
            logger.warning("Extracted text is empty")
            return None
            
        logger.info(f"Successfully extracted text from PDF with {len(reader.pages)} pages")
        return text
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return None

def parse_gemini_response(response: str) -> Dict[str, Any]:
    """Parse the JSON response from Gemini with error handling"""
    try:
        # Clean the response to ensure it's valid JSON
        # Sometimes the model might return additional text around the JSON
        response = response.strip()
        
        # Find JSON content (anything between { and })
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            result = json.loads(json_str)
            logger.info("Successfully parsed JSON response")
            return result
        else:
            logger.error("Could not find valid JSON in response")
            return {"error": "Invalid response format", "raw_response": response}
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return {"error": "Failed to parse response", "raw_response": response}

def create_prompt(resume_text: str, job_description: str) -> str:
    """Create a well-structured prompt for the Gemini model"""
    prompt = """
    You are an elite Applicant Tracking System (ATS) expert with deep specialization in technical recruitment for fields including 
    software engineering, data science, machine learning, data analysis, big data engineering, cloud computing, 
    and IT roles. You have 15+ years of experience in technical recruiting for top tech companies.
    
    Analyze the provided resume against the job description with extreme precision and provide:
    
    1. A percentage match score between the resume and job description. Be realistic but fair - most candidates don't exceed 85% match.
    2. A detailed, categorized list of important keywords/skills from the job description missing in the resume.
       Categorize them as: Technical Skills, Soft Skills, Experience, Education/Certifications.
    3. A compelling professional summary of the candidate's profile.
    4. 3-5 specific, actionable recommendations to improve the resume for this particular job.
    5. 2-3 strengths of the resume relative to the job description.
    6. A brief explanation of why certain skills/experiences are particularly valuable for this role.
    
    Resume:
    {resume}
    
    Job Description:
    {jd}
    
    Return your analysis in the following JSON format only:
    {{
        "JD Match": "XX%",
        "MissingKeywords": {{
            "Technical Skills": ["skill1", "skill2", ...],
            "Soft Skills": ["skill1", "skill2", ...],
            "Experience": ["exp1", "exp2", ...],
            "Education/Certifications": ["cert1", "cert2", ...]
        }},
        "Profile Summary": "Compelling summary of the candidate's profile",
        "Improvement Suggestions": ["suggestion1", "suggestion2", "suggestion3", ...],
        "Resume Strengths": ["strength1", "strength2", ...],
        "Key Role Requirements": "Brief explanation of the most critical skills for this role"
    }}
    
    Be thorough but ensure you maintain valid JSON format. Focus on practical, actionable insights that would genuinely help the candidate.
    """
    
    return prompt.format(resume=resume_text, jd=job_description)

def display_results(analysis_results: Dict[str, Any]):
    """Display the analysis results in a user-friendly format"""
    if "error" in analysis_results:
        st.error("Error analyzing the resume")
        st.write("Raw response:")
        st.write(analysis_results.get("raw_response", "No response available"))
        return
    
    try:
        # Create tabs for organized display
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Match Score", "📋 Profile Analysis", "🔍 Skills Gap", "💡 Recommendations"])
        
        with tab1:
            # Display match percentage with an attractive gauge
            match_percentage = analysis_results.get("JD Match", "N/A")
            
            try:
                match_value = float(match_percentage.replace("%", ""))
                
                # Determine color and message based on score
                if match_value >= 80:
                    color = "#28a745"  # Green
                    emoji = "🌟"
                    message = "Excellent match!"
                elif match_value >= 65:
                    color = "#17a2b8"  # Blue
                    emoji = "👍"
                    message = "Good match!"
                elif match_value >= 50:
                    color = "#ffc107"  # Yellow
                    emoji = "⚠️"
                    message = "Moderate match"
                else:
                    color = "#dc3545"  # Red
                    emoji = "⚠️"
                    message = "Needs improvement"
                
                # Create a centered column for the gauge
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"<h1 style='text-align: center; color: {color};'>{match_percentage}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align: center;'>{emoji} {message}</h3>", unsafe_allow_html=True)
                    
                    # Create a more attractive circular gauge
                    html_gauge = f"""
                    <div style="display: flex; justify-content: center; margin: 20px 0;">
                        <div style="
                            width: 200px;
                            height: 200px;
                            border-radius: 50%;
                            background: conic-gradient({color} {match_value}%, #f3f3f3 0);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <div style="
                                width: 150px;
                                height: 150px;
                                border-radius: 50%;
                                background: white;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 24px;
                                font-weight: bold;
                            ">
                                {match_percentage}
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(html_gauge, unsafe_allow_html=True)
                    
                    # Score interpretation
                    st.markdown("""
                    #### Score Interpretation:
                    - **80-100%**: Excellent match, highly qualified
                    - **65-79%**: Good match, well-qualified with some gaps
                    - **50-64%**: Moderate match, has core qualifications but significant gaps
                    - **Below 50%**: Needs substantial improvement to be competitive
                    """)
            except (ValueError, TypeError):
                st.write(f"Match Percentage: {match_percentage}")
                
        with tab2:
            # Display profile summary with enhanced styling
            st.markdown("### Professional Profile Summary")
            profile_summary = analysis_results.get("Profile Summary", "No summary available")
            st.markdown(f"""
            <div style="
                background-color: #000000;
                border-left: 5px solid #6c757d;
                padding: 15px;
                border-radius: 4px;
            ">
                {profile_summary}
            </div>
            """, unsafe_allow_html=True)
            
            # Display resume strengths
            strengths = analysis_results.get("Resume Strengths", [])
            if isinstance(strengths, list) and strengths:
                st.markdown("### Resume Strengths")
                for i, strength in enumerate(strengths, 1):
                    st.markdown(f"""
                    <div style="
                        background-color: #000000;
                        border-left: 5px solid #17a2b8;
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 4px;
                    ">
                        <strong>{i}.</strong> {strength}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display key role requirements
            key_reqs = analysis_results.get("Key Role Requirements", "")
            if key_reqs:
                st.markdown("### Critical Skills for This Role")
                st.markdown(f"""
                <div style="
                    background-color: #bf80ff;
                    border-left: 5px solid #4d0099;
                    padding: 15px;
                    border-radius: 4px;
                ">
                    {key_reqs}
                </div>
                """, unsafe_allow_html=True)
                
        with tab3:
            # Display missing keywords
            missing_keywords = analysis_results.get("MissingKeywords", {})
            if isinstance(missing_keywords, dict) and missing_keywords:
                st.markdown("### Skills Gap Analysis")
                
                # Create expandable sections for each category
                categories = {
                    "Technical Skills": "💻",
                    "Soft Skills": "🤝",
                    "Experience": "📈",
                    "Education/Certifications": "🎓"
                }
                
                for category, emoji in categories.items():
                    skills = missing_keywords.get(category, [])
                    if isinstance(skills, list) and skills:
                        with st.expander(f"{emoji} {category} ({len(skills)})"):
                            col1, col2 = st.columns(2)
                            half = len(skills) // 2 + len(skills) % 2
                            
                            for i, skill in enumerate(skills[:half]):
                                col1.markdown(f"""
                                <div style="
                                    background-color: #000000;
                                    padding: 8px;
                                    margin: 5px 0;
                                    border-radius: 4px;
                                    border: 1px solid #dee2e6;
                                ">
                                    {skill}
                                </div>
                                """, unsafe_allow_html=True)
                                
                            for i, skill in enumerate(skills[half:]):
                                col2.markdown(f"""
                                <div style="
                                    background-color: #000000;
                                    padding: 8px;
                                    margin: 5px 0;
                                    border-radius: 4px;
                                    border: 1px solid #dee2e6;
                                ">
                                    {skill}
                                </div>
                                """, unsafe_allow_html=True)
            elif isinstance(missing_keywords, list) and missing_keywords:
                # Handle old format for backwards compatibility
                st.markdown("### Missing Keywords")
                for keyword in missing_keywords:
                    st.markdown(f"- {keyword}")
            else:
                st.write("No missing keywords found or unable to parse keywords.")
                
        with tab4:
            # Display improvement suggestions
            suggestions = analysis_results.get("Improvement Suggestions", [])
            if isinstance(suggestions, list) and suggestions:
                st.markdown("### Actionable Recommendations")
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"""
                    <div style="
                        background-color: #03530f;
                        border-left: 5px solid #28a745;
                        padding: 10px;
                        margin: 10px 0;
                        border-radius: 4px;
                    ">
                        <strong>{i}.</strong> {suggestion}
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Add a "Next Steps" section
                st.markdown("### Next Steps")
                st.markdown("""
                1. **Update Your Resume**: Add the missing keywords and skills where applicable
                2. **Tailor Your Experience**: Modify your experience descriptions to highlight relevant skills
                3. **Quantify Achievements**: Add metrics and specific outcomes to show impact
                4. **Focus on Keywords**: Ensure you're using the same terminology as the job description
                5. **Create a Tailored Cover Letter**: Address specific job requirements and how you meet them
                """)
            
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        st.error(f"Error displaying results: {str(e)}")
        st.write("Raw data:")
        st.write(analysis_results)

# Streamlit UI
def main():
    st.set_page_config(
        page_title="ResumeAI - ATS Optimization Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS with improved tab styling
    st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2c3e50;
        color: #f8f9fa;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #212529;
        color: #ffffff;
        border-bottom: 2px solid #17a2b8;
        font-weight: 600;
    }
    div.block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #4e89ae;
        color: white;
        font-weight: bold;
        height: 3em;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #2c3e50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/resume.png", width=100)
        st.title("ResumeAI")
        st.markdown("### ATS Optimization Tool")
        st.markdown("---")
        st.markdown("""
        **How it works:**
        1. Upload your resume (PDF)
        2. Paste the job description
        3. Click 'Analyze Resume'
        4. Get insights to improve your chances
        """)
        st.markdown("---")
        st.markdown("### Resume Tips")
        tips = [
            "Use keywords from the job description",
            "Quantify your achievements with numbers",
            "Keep formatting simple for ATS systems",
            "Customize your resume for each application",
            "Focus on relevant skills and experience"
        ]
        for tip in tips:
            st.markdown(f"- {tip}")
    
    # Main content
    st.title("🚀 ResumeAI - Smart ATS Analyzer")
    st.markdown("""
    <div style="background-color: #000000; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <p>Upload your resume and paste the job description to get AI-powered insights on how to improve your chances of getting an interview. Our tool analyzes your resume against the job description using advanced AI to identify gaps and suggest improvements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload and job description
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "📄 Upload Your Resume (PDF)", 
                type="pdf",
                help="Please upload a PDF file"
            )
            
            if uploaded_file:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Show preview option
                if st.checkbox("👁️ Preview Resume Text"):
                    with st.spinner("Extracting text..."):
                        preview_text = extract_pdf_text(uploaded_file)
                        if preview_text:
                            st.text_area("Resume Text Preview", preview_text, height=200)
                        else:
                            st.warning("⚠️ Could not extract text from the PDF. The file may be scanned or protected.")
        
        with col2:
            job_description = st.text_area(
                "💼 Paste the Job Description",
                height=300,
                placeholder="Paste the job description here to analyze against your resume..."
            )
    
    # Input example
    with st.expander("💡 Not sure what to do? Click here for an example job description"):
        st.markdown("""
        **Example Job Description:**
        
        **Data Scientist - Machine Learning**
        
        We are looking for a Data Scientist with strong machine learning experience to join our team. The ideal candidate will have:
        
        - 3+ years of experience in data science or related field
        - Proficiency in Python, SQL, and data visualization tools
        - Experience with machine learning frameworks (scikit-learn, TensorFlow, PyTorch)
        - Strong understanding of statistical analysis and modeling
        - Experience with NLP and computer vision is a plus
        - Excellent communication and presentation skills
        - MS or PhD in Computer Science, Statistics, or related field
        - Experience with cloud platforms (AWS, GCP, or Azure)
        
        Responsibilities include developing machine learning models, analyzing large datasets, creating data visualizations, and presenting insights to stakeholders.
        """)
    
    # Analysis button with improved styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze My Resume", type="primary", use_container_width=True)
    
    # Analysis section
    if analyze_button:
        if not uploaded_file:
            st.warning("⚠️ Please upload a resume PDF file")
            return
            
        if not job_description:
            st.warning("⚠️ Please provide a job description")
            return
        
        with st.spinner("🔍 AI is analyzing your resume... This may take up to 30 seconds"):
            # Extract text from PDF
            resume_text = extract_pdf_text(uploaded_file)
            
            if not resume_text:
                st.error("❌ Could not extract text from the uploaded PDF. Please check if the file is properly formatted or not password protected.")
                return
                
            # Create prompt and get response
            prompt = create_prompt(resume_text, job_description)
            response = get_gemini_response(prompt)
            
            if not response:
                st.error("❌ Failed to get analysis from the AI model. Please try again later.")
                return
                
            # Parse and display results
            st.markdown("## 📊 Resume Analysis Results")
            st.markdown("<div style='border-top: 1px solid #e6e6e6; margin-bottom: 30px;'></div>", unsafe_allow_html=True)
            
            analysis_results = parse_gemini_response(response)
            display_results(analysis_results)
            
            # Log completion
            logger.info("Analysis completed and displayed to user")
            
            # Footer
            st.markdown("<div style='border-top: 1px solid #e6e6e6; margin-top: 30px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align: center; margin-top: 20px; color: #6c757d;">
                ResumeAI helps you optimize your resume for Applicant Tracking Systems (ATS)<br>
                Powered by Google Gemini 2.0 AI and Aniketh and Animesh!
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()