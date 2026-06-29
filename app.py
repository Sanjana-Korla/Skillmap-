import streamlit as st
import pandas as pd
import numpy as np
import os
import json

from rag.retriever import CareerRAGRetriever
from agents.skill_profiler import SkillProfilerAgent
from agents.market_agent import MarketDemandAgent
from agents.gap_agent import GapIdentifierAgent
from agents.roadmap_agent import RoadmapBuilderAgent
from agents.resource_agent import ResourceRecommendationAgent
from agents.progress_agent import ProgressTrackerAgent
from utils.resume_parser import SimpleResumeParser
from utils.charts import generate_comparison_chart, generate_market_demand_chart
from utils.pdf_export import PDFExporter

# Helper to automatically clear the cached roadmap when the week duration slider is adjusted
def reset_roadmap_cache():
    st.session_state.roadmap = {}

# Page layout and initial config
st.set_page_config(
    page_title="SkillMap - AI Career Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme configurations
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}
div.stButton > button:first-child {
    background-color: #238636;
    color: white;
    border: none;
    border-radius: 6px;
}
div.stButton > button:hover {
    background-color: #2ea043;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Application global state configuration variables
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user_skills = []
    st.session_state.proficiency_levels = {}
    st.session_state.experience_years = 1.0
    st.session_state.target_role = ""
    st.session_state.profile_report = {}
    st.session_state.gap_report = {}
    st.session_state.roadmap = {}
    st.session_state.resources = {}
    st.session_state.completed_weeks = []
    st.session_state.market_demand = {}
    st.session_state.rag_meta = {}
    st.session_state.uploaded_file_name = None
    st.session_state.agent_assessment = ""  # Cache for detailed advisor assessment

st.sidebar.title("SkillMap Navigation")
page = st.sidebar.radio(
    "Select Action Portal",
    ["Home Panel", "Skill Profiler", "Market Metrics", "Gap Analysis",
     "Development Roadmap", "Progress Hub", "AI Agent Assistant", "Export Portal"]
)

@st.cache_resource
def get_rag_retriever():
    return CareerRAGRetriever()

# ==================== HOME PANEL ====================
if page == "Home Panel":
    st.title("SkillMap - AI Career Intelligence System")
    st.markdown("""
    Welcome to **SkillMap**, your agentic talent intelligence advisor. This platform maps skill profiles against parsed industry benchmarks using multi-agent verification pathways.
    
    ### Dynamic Pipelines Active
    * **RAG Parser Core**: Extracts market data constraints out of customized local document stores.
    * **Negotiation Engine Core**: Correlates targets through cooperative processing nodes.
    * **Visualizer Suite**: Computes structural comparisons, market weights, and tracking metrics.
    """)
    st.info("Step 1: Open the 'Skill Profiler' to initialize your developer persona.")

# ==================== SKILL PROFILER ====================
elif page == "Skill Profiler":
    st.title("Persona Structuring Portal")
    st.markdown("Enter your background details below to build your core skill profile.")
    
    uploaded_file = st.file_uploader("Bootstrap from PDF Resume (Optional)", type=["pdf"])
    parsed_skills = []
    
    if uploaded_file:
        st.session_state.uploaded_file_name = uploaded_file.name
        parser = SimpleResumeParser()
        parsed_skills = parser.parse_pdf(uploaded_file)
        if parsed_skills:
            st.success(f"Extracted matching technologies from resume: {', '.join(parsed_skills)}")
            st.session_state.user_skills = list(set(st.session_state.user_skills + parsed_skills))
    elif st.session_state.uploaded_file_name:
        st.info(f" **Active Resume**: `{st.session_state.uploaded_file_name}` is currently processed and loaded in this session.")
            
    default_skills = ", ".join(st.session_state.user_skills) if st.session_state.user_skills else ""
            
    skills_input = st.text_input(
        "Input Core Skillsets (Comma-Separated)",
        value=default_skills,
        placeholder="e.g., Python, SQL, Git, JavaScript"
    )
    
    user_skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
    
    experience = st.number_input(
        "Years of Professional Experience", 
        min_value=0.0, 
        max_value=30.0, 
        value=float(st.session_state.get("experience_years", 1.0)), 
        step=0.5
    )
    
    proficiency_map = {}
    if user_skills_list:
        st.write("#### Define Technology Proficiency Levels")
        cols = st.columns(min(len(user_skills_list), 4))
        for idx, skill in enumerate(user_skills_list):
            col_target = cols[idx % 4]
            saved_prof = st.session_state.proficiency_levels.get(skill, "Intermediate")
            prof_options = ["Beginner", "Intermediate", "Expert"]
            default_idx = prof_options.index(saved_prof) if saved_prof in prof_options else 1
            proficiency_map[skill] = col_target.selectbox(
                f"Proficiency - {skill}", 
                prof_options, 
                index=default_idx, 
                key=f"prof_{skill}"
            )
            
    target_role_selection = st.text_input(
        "Enter Target Career Role",
        value=st.session_state.target_role,
        placeholder="e.g., AI Engineer, Data Scientist, Frontend Web Developer"
    )
    
    st.session_state.user_skills = user_skills_list
    st.session_state.proficiency_levels = proficiency_map
    st.session_state.experience_years = experience
    st.session_state.target_role = target_role_selection
    
    col_btn1, col_btn2 = st.columns([1, 3])
    
    with col_btn1:
        if st.button("Generate Profile & Query RAG Store"):
            if not user_skills_list or not target_role_selection:
                st.error("Please provide both your current skills and a target career role to proceed.")
            else:
                with st.spinner("Executing dynamic structural profiling and loading RAG vector store..."):
                    try:
                        retriever = get_rag_retriever()
                    except Exception as e:
                        st.error(f"Error loading FAISS vector database: {e}")
                        retriever = None

                    profiler = SkillProfilerAgent()
                    profile_report = profiler.profile_user(user_skills_list, proficiency_map, experience)
                    st.session_state.profile_report = profile_report
                    
                    if retriever:
                        rag_context = retriever.retrieve_context(target_role_selection)
                        st.session_state.rag_meta = rag_context
                        market_agent = MarketDemandAgent()
                        st.session_state.market_demand = market_agent.analyze_demand(rag_context)
                    
                    # Reset dynamic dependencies to trigger on-demand rebuilds
                    st.session_state.roadmap = {}
                    st.session_state.agent_assessment = ""
                    st.session_state.completed_weeks = []
                        
                    st.success("Analysis profiling sequence complete. Navigate to 'Market Metrics' to inspect market trends!")
                    st.rerun()
                    
    with col_btn2:
        if st.button("Reset Profiler & Start Fresh"):
            st.session_state.user_skills = []
            st.session_state.proficiency_levels = {}
            st.session_state.experience_years = 1.0
            st.session_state.target_role = ""
            st.session_state.profile_report = {}
            st.session_state.gap_report = {}
            st.session_state.roadmap = {}
            st.session_state.resources = {}
            st.session_state.completed_weeks = []
            st.session_state.market_demand = {}
            st.session_state.rag_meta = {}
            st.session_state.uploaded_file_name = None
            st.session_state.agent_assessment = ""
            st.success("Profile cache successfully cleared.")
            st.rerun()

    if st.session_state.profile_report:
        st.write("---")
        st.subheader("Your Generated Profile Summary")
        col_p1, col_p2 = st.columns(2)
        col_p1.metric("Competency Assessment Score", f"{st.session_state.profile_report.get('profile_score', 0):.1f}/100")
        col_p2.metric("Taxonomy Alignment", f"{st.session_state.profile_report.get('taxonomy_overlap_percentage', 0.0):.1f}%")
        st.json(st.session_state.profile_report.get("skill_groups", {}))

# ==================== MARKET METRICS ====================
elif page == "Market Metrics":
    st.title("Industry Alignment & Market Metrics")
    if not st.session_state.market_demand:
        st.markdown("### Market Analysis Portal Locked")
        st.info("No active developer profile has been analyzed yet. Follow the steps below to initialize:")
        st.markdown("""
        1. Open the  **Skill Profiler** portal from the sidebar.
        2. Input your current skill sets, years of experience, and a target career role.
        3. Click **Generate Profile & Query RAG Store** to build your persona context.
        """)
    else:
        rag_meta = st.session_state.rag_meta
        confidence = rag_meta.get("confidence_score", 0.0)
        matched_role_name = "None Found"
        if rag_meta.get("retrieved_roles"):
            matched_role_name = rag_meta["retrieved_roles"][0].get("role", "Unknown")
            
        total_jds = st.session_state.market_demand.get("total_jds_evaluated", 1)
        plural_suffix = "JD Profile" if total_jds == 1 else "JD Profiles"
            
        col1, col2, col3 = st.columns(3)
        col1.metric("Matched Role Profile", matched_role_name)
        col2.metric("Retrieval RAG Confidence rating", f"{confidence:.2f}")
        col3.metric("Evaluated JDs Target Volume", f"{total_jds} {plural_suffix}")
        
        if confidence < 0.20:
            st.error(" Insufficient market evidence detected! Preventing LLM hallucination: Retrieved score values under-index industry norms. Please broaden target role input targets.")
        else:
            st.success("Target context successfully grounded in factual local datasets.")
            
        default_data = st.session_state.market_demand
        skills = list(default_data.get("demand_scores", {}).keys())
        scores = list(default_data.get("demand_scores", {}).values())
        
        if skills:
            st.write("### Target Role Skills Frequency Distribution")
            fig = generate_market_demand_chart(skills, scores)
            if fig:
                st.pyplot(fig)
        else:
            st.info("No distinct skills found in standard file indexes matching search profiles.")
            
        st.write("---")
        st.subheader(" Market Trend Alerts")
        high_demand_trends = [skill for skill, score in default_data.get("demand_scores", {}).items() if score >= 0.6]
        
        if high_demand_trends:
            st.info(
                f"**Trending High-Demand Skills for {matched_role_name}:** "
                f"The market heavily prioritizes **{', '.join(high_demand_trends)}** (found in >60% of regional JDs). "
                "We recommend prioritizing these skills in your learning plan."
            )
        else:
            st.info("No single technology represents an overwhelming majority trend. Focus on standard core baseline requirements.")
            
        st.write("---")
        with st.expander("Ground Truth Verifiability (Traceable RAG Sources)"):
            st.info(f"RAG Explanation: {rag_meta.get('rag_explanation')}")
            for r in rag_meta.get("retrieved_roles", []):
                st.markdown(f" **Source Document File:** `{rag_meta.get('sources', ['Unknown'])[0]}` ({total_jds} profiles evaluated)")
                st.markdown(f" **Role Match:** `{r['role']}` (Domain: `{r['domain']}`)")
                st.write(f" *Skills Required:* {', '.join(r['skills'])}")
                st.write(f" *Confidence Score Value:* {r['relevance']:.2f}")

# ==================== GAP ANALYSIS ====================
elif page == "Gap Analysis":
    st.title("Skill Gaps Analysis & Priorities")
    if not st.session_state.market_demand:
        st.markdown("###  Gap Identification Locked")
        st.info("Before we can identify your skill gaps, we need to compare your profile against the market:")
        st.markdown("""
        1. Open the  **Skill Profiler** portal from the sidebar.
        2. Input your background technologies and set your target career goal.
        3. Run the generator to load factual JD benchmarks from our RAG vector store.
        """)
    elif st.session_state.rag_meta.get("confidence_score", 0.0) < 0.20:
        st.error("Core analysis is locked due to low retrieval confidence. Modify target parameters in the Profiler.")
    else:
        # Resolves raw strings into standardized profiles produced by the Profiler Agent
        normalized_user_skills = st.session_state.profile_report.get("normalized_skills", st.session_state.user_skills)
        
        gap_agent = GapIdentifierAgent()
        gap_report = gap_agent.identify_gaps(
            normalized_user_skills,
            st.session_state.market_demand,
            st.session_state.proficiency_levels
        )
        st.session_state.gap_report = gap_report
        
        st.subheader(f"Overall Fit Match Rating: {gap_report.get('match_score')}%")
        st.progress(gap_report.get('match_score') / 100.0)
        
        labels = []
        user_vals = []
        mkt_vals = []
        prof_score_map = {"none": 0.0, "beginner": 1.0, "intermediate": 2.5, "expert": 4.0}
        
        merged_radar_list = gap_report.get("matched_skills", [])[:4] + gap_report.get("missing_skills", [])[:4]
        
        user_skills_lower = [s.strip().lower() for s in normalized_user_skills]
        user_prof_lower = {k.strip().lower(): v.strip().lower() for k, v in st.session_state.proficiency_levels.items()}
        
        for item in merged_radar_list:
            skill = item["skill"]
            labels.append(skill)
            skill_lower = skill.strip().lower()
            if skill_lower in user_skills_lower:
                user_prof_raw = user_prof_lower.get(skill_lower, "beginner")
                u_score = prof_score_map.get(user_prof_raw, 1.0)
            else:
                u_score = 0.0
            user_vals.append(u_score)
            mkt_vals.append(3.0)
            
        if labels:
            st.write("### Skills Competency Benchmark")
            fig = generate_comparison_chart(labels, user_vals, mkt_vals)
            if fig:
                st.pyplot(fig)
                
        st.write("---")
        st.subheader("Core Skills Action Report")
        
        missing_data = gap_report.get("missing_skills", [])
        if missing_data:
            st.markdown("#### High Priority Gaps (Acquisition Required)")
            df_missing = pd.DataFrame(missing_data)
            df_missing["demand_percentage"] = df_missing["demand"].apply(lambda x: f"{int(x * 100)}%")
            df_missing_styled = df_missing[["skill", "demand_percentage", "priority_score"]].rename(
                columns={
                    "skill": "Required Technology",
                    "demand_percentage": "Market Demand Rate",
                    "priority_score": "Engine Priority Weight"
                }
            )
            st.dataframe(df_missing_styled, width="stretch", hide_index=True)
        else:
            st.success("No missing critical core skills detected.")
            
        st.write("")
        weak_data = gap_report.get("weak_skills", [])
        if weak_data:
            st.markdown("####  Skill Polishing Required (Upskilling Targets)")
            df_weak = pd.DataFrame(weak_data)
            df_weak["demand_percentage"] = df_weak["demand"].apply(lambda x: f"{int(x * 100)}%")
            df_weak_styled = df_weak[["skill", "demand_percentage", "priority_score"]].rename(
                columns={
                    "skill": "Target Technology",
                    "demand_percentage": "Market Demand Rate",
                    "priority_score": "Upskill Priority Weight"
                }
            )
            st.dataframe(df_weak_styled, width="stretch", hide_index=True)
        else:
            st.info("No weak baseline skills detected requiring upskilling.")

# ==================== DEVELOPMENT ROADMAP ====================
elif page == "Development Roadmap":
    st.title("Personalized Career Roadmap Plan")
    if not st.session_state.gap_report:
        st.markdown("### Custom Career Roadmap Locked")
        st.info("Your tailored, week-by-week upskilling curriculum requires an active gap analysis:")
        st.markdown("""
        1. Head over to the  **Skill Profiler** to declare your current and target skill profile.
        2. Open the  **Gap Analysis** page to compute critical priority gaps.
        3. Come back here to view your automatically synthesized learning roadmap!
        """)
    else:
        weeks_duration = st.slider(
            "Configure Track Roadmap Duration (Weeks)", 
            min_value=4, 
            max_value=12, 
            value=8,
            on_change=reset_roadmap_cache
        )
        
        # AUTOMATIC ON-DEMAND GENERATION
        if not st.session_state.roadmap:
            with st.spinner("Synthesizing tailored week-by-week curriculum based on your profile gaps..."):
                all_needed_skills = [m["skill"] for m in st.session_state.gap_report.get("missing_skills", [])] + \
                                    [w["skill"] for w in st.session_state.gap_report.get("weak_skills", [])]
                                    
                resource_agent = ResourceRecommendationAgent()
                curated_resources = resource_agent.recommend_resources(all_needed_skills)
                st.session_state.resources = curated_resources
                
                builder = RoadmapBuilderAgent()
                roadmap = builder.build_roadmap(
                    st.session_state.target_role,
                    st.session_state.gap_report,
                    curated_resources,
                    weeks_duration
                )
                st.session_state.roadmap = roadmap
                st.rerun()
                
        if st.session_state.roadmap:
            if "error" in st.session_state.roadmap:
                st.error(f"Failed to generate structured roadmap. Error detail: {st.session_state.roadmap['error']}")
                if st.button("Retry Generation"):
                    st.session_state.roadmap = {}
                    st.rerun()
            else:
                st.subheader(st.session_state.roadmap.get("roadmap_title", "Custom Career Acceleration Roadmap"))
                
                if st.session_state.rag_meta.get("sources"):
                    source_file = st.session_state.rag_meta["sources"][0]
                    st.caption(f" **Ground Truth Source File**: Verified using target profile distributions in `{source_file}`.")
                
                st.info(" Ground Truth RAG Verification: Curated resource platforms shown below are retrieved from validated course lists and dynamically scheduled.")
                for week in st.session_state.roadmap.get("weeks", []):
                    with st.expander(f"Week {week.get('week_number')}: {', '.join(week.get('focus_skills', []))}"):
                        st.markdown(f"**Topics Covered:** {', '.join(week.get('topics', []))}")
                        st.markdown(f"**Weekly Commitment Time:** {week.get('estimated_hours')} Hours")
                        st.info(f"**Goal:** {week.get('curriculum_goal')}")
                        st.success(f"**Deliverable Outcome:** {week.get('expected_outcome')}")
                        
                        st.markdown("####  Curated Week Resources")
                        w_res = week.get("resources", [])
                        if w_res:
                            for res in w_res:
                                st.markdown(f"- **{res.get('platform')}**: [{res.get('title')}]({res.get('url')})")
                        else:
                            st.write("*No resources registered for this week's goals.*")

# ==================== PROGRESS HUB ====================
elif page == "Progress Hub":
    st.title("Track Progress & Recalculate Roadmap")
    if not st.session_state.roadmap or "error" in st.session_state.roadmap:
        st.markdown("###  Interactive Progress Hub Locked")
        st.info("Interactive progression checklist milestones require an active roadmap program:")
        st.markdown("""
        1. Complete your profile modeling in the 👤 **Skill Profiler**.
        2. Generate your week-by-week curriculum under the 🗺️ **Development Roadmap** page.
        3. Open this hub to track your weekly progress and dynamically recalculate gaps.
        """)
    else:
        weeks = st.session_state.roadmap.get("weeks", [])
        total_weeks = len(weeks)
        st.subheader("Interactive Progression Milestones")
        
        for w in weeks:
            week_idx = w.get("week_number")
            is_checked = week_idx in st.session_state.completed_weeks
            if st.checkbox(f"Mark Week {week_idx} Complete: {', '.join(w.get('focus_skills', []))}", value=is_checked):
                if week_idx not in st.session_state.completed_weeks:
                    st.session_state.completed_weeks.append(week_idx)
            else:
                if week_idx in st.session_state.completed_weeks:
                    st.session_state.completed_weeks.remove(week_idx)
                    
        tracker = ProgressTrackerAgent()
        progress_pct = tracker.calculate_progress(st.session_state.completed_weeks, total_weeks)
        
        st.write("---")
        st.write("### Completed Rate Breakdown")
        st.metric("Total Progress Complete Percentage", f"{progress_pct}%")
        st.progress(progress_pct / 100.0)

        if st.session_state.completed_weeks and st.session_state.gap_report:
            completed_skills = []
            for w in weeks:
                if w.get("week_number") in st.session_state.completed_weeks:
                    completed_skills.extend(w.get("focus_skills", []))
            
            updated_gaps = tracker.recalculate_roadmap_gaps(st.session_state.gap_report, completed_skills)
            
            st.write("---")
            st.subheader(" Dynamic Gap Recalculation")
            st.write(f"Adjusted Overall Fit Match Rating: **{updated_gaps.get('match_score')}%**")
            
            if updated_gaps.get("missing_skills"):
                st.markdown("**Remaining Missing Skills to Acquire:**")
                st.write(", ".join([m["skill"] for m in updated_gaps["missing_skills"]]))
            else:
                st.success("All identified missing skills have been marked as completed! Your profile is aligned with market expectations.")

# ==================== AI AGENT ASSISTANT ====================
elif page == "AI Agent Assistant":
    st.title("Autonomous Career Agent Assistant")
    st.markdown("""
    The advisor agent can autonomously analyze your profile, retrieve benchmarks, and evaluate your skills.
    """)

    # Fetch active session variables from memory
    user_skills = st.session_state.get("user_skills", [])
    target_role = st.session_state.get("target_role", "")

    # Automatic Generation Flow
    if user_skills and target_role and st.session_state.gap_report and "error" not in st.session_state.gap_report:
        st.info(f" **Active Profile Detected:**\n* **Your Skills:** `{', '.join(user_skills)}` \n* **Target Role:** `{target_role}`")
        
        # EXTENSIVE, MULTI-SECTION "MORE MATTER" COMPILATION
        if not st.session_state.agent_assessment:
            with st.spinner("Agent is automatically compiling structured assessment..."):
                from utils.gemini_helper import GeminiHelper
                fast_helper = GeminiHelper()
                
                system_prompt = "You are an elite career advisory intelligence system."
                user_prompt = f"""
                Analyze this candidate profile for the target role of '{target_role}':
                - Candidate Normal Skills: {st.session_state.profile_report.get('normalized_skills')}
                - Overall Match score: {st.session_state.gap_report.get('match_score')}%
                - Missing Gaps to acquire: {[m['skill'] for m in st.session_state.gap_report.get('missing_skills', [])]}
                - Weak Gaps to polish: {[w['skill'] for w in st.session_state.gap_report.get('weak_skills', [])]}
                - Key Market Demands: {st.session_state.market_demand.get('demand_scores')}
                
                Provide an extensive, comprehensive, and highly detailed professional talent evaluation. 
                Structure your output into 4 detailed sections using Markdown:
                
                ### 1. Overall Competency Synthesis
                Write a detailed analysis of their current market readiness. Explain what their match percentage of {st.session_state.gap_report.get('match_score')}% means in the current landscape for a {target_role}, the competitiveness of their profile, and what adjustments they need to make to become highly competitive.
                
                ### 2. Key Foundational Strengths
                Provide a thorough breakdown of their existing skills. Explain why these specific skills are valuable to modern engineering teams, how they can leverage them in job applications, and how they serve as a foundation for further learning.
                
                ### 3. Critical Market Gaps & Risks
                Examine the missing skills. Discuss the high market demand rates of these missing skills, the real-world performance risks of entering the industry without them, and the specific career limitations they will face if they do not acquire them.
                
                ### 4. Actionable Professional Roadmap
                Lay out a step-by-step upskilling strategy. Give concrete, strategic, and practical advice on which skills to tackle first, how to schedule their learning, and how to practice these skills with hands-on projects.
                
                Be thorough, analytical, and substantial. Provide deep, text-rich, and authoritative advice.
                """
                assessment_text = fast_helper.generate_text(system_prompt, user_prompt)
                st.session_state.agent_assessment = assessment_text
                st.rerun()
                
        if st.session_state.agent_assessment:
            st.write("### Automatically Generated Advisor Assessment:")
            st.markdown(st.session_state.agent_assessment)
        
        st.write("---")
        st.write("####  Ask a Custom Question")
    else:
        st.markdown("###  Autonomous Advisory Portal Locked")
        st.info("The advisor needs to know who you are and where you want to go before generating a tailored evaluation:")
        st.markdown("""
        1. Configure your developer persona in the 👤 **Skill Profiler**.
        2. Once created, return here to view your autonomous diagnostic evaluation.
        3. You can still ask a custom technical question below at any time!
        """)

    # for custom questions
    default_placeholder = "Type your career or upskilling query here..."
    user_query = st.text_input("Enter your custom request", placeholder=default_placeholder)

    if st.button("Submit Custom Request"):
        if user_query:
            with st.spinner("Agent is reasoning and executing tools..."):
                from agents.orchestrator import CareerAgentOrchestrator
                orchestrator = CareerAgentOrchestrator()
                agent_response = orchestrator.query(user_query)
                st.write("### Agent Assessment:")
                st.info(agent_response)
        else:
            st.warning("Please enter a custom query.")

# ==================== EXPORT PORTAL ====================
elif page == "Export Portal":
    st.title("Export Acceleration Blueprint PDF")
    if not st.session_state.roadmap or "error" in st.session_state.roadmap:
        st.markdown("###  PDF Export Portal Locked")
        st.info("Your professional PDF acceleration blueprint cannot be compiled yet:")
        st.markdown("""
        1. Initialize your career target in the  **Skill Profiler**.
        2. Generate your structured curriculum track in the  **Development Roadmap** portal.
        3. Return to this portal to download your high-quality learning handbook!
        """)
    else:
        if st.button("Generate and Download PDF Document"):
            with st.spinner("Processing PDF Document assembly..."):
                pdf_data = PDFExporter.export_roadmap_to_pdf(
                    st.session_state.target_role,
                    st.session_state.gap_report,
                    st.session_state.roadmap
                )
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name="SkillMap_Career_Acceleration_Plan.pdf",
                    mime="application/pdf"
                )
                st.success("PDF compilation sequence executed.")