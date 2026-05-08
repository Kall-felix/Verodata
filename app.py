import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="VeroData", layout="wide", page_icon="iconverodata.png")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton>button {
        background-color: #ac3416 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: 900 !important;
        font-size: 18px !important;
        letter-spacing: 1px;
        width: 100%;
        border: none;
        padding: 1.5rem !important;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(172, 52, 22, 0.3);
    }
    .stButton>button:hover { 
        background-color: #8f4e01 !important; 
        box-shadow: 0 6px 12px rgba(143, 78, 1, 0.4);
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: bold; font-size: 16px; }
    .stTabs [aria-selected="true"] { color: #ac3416 !important; }
    </style>
""", unsafe_allow_html=True)

class VeroDataPipeline:
    """Handles all data cleaning operations and health score calculations."""
    
    def __init__(self, raw_dataframe):
        self.df = raw_dataframe.copy()
        self.metrics = {
            "duplicates_removed": 0, 
            "nulls_imputed": 0, 
            "negatives_fixed": 0, 
            "health_score": 100.0
        }

    def remove_duplicates(self):
        initial_row_count = self.df.shape[0]
        self.df = self.df.drop_duplicates()
        self.metrics["duplicates_removed"] = initial_row_count - self.df.shape[0]

    def impute_missing_values(self):
        initial_null_count = self.df.isna().sum().sum()
        
        # Fill missing prices with the mean, and missing sales with the median
        if 'price' in self.df.columns: 
            self.df['price'] = self.df['price'].fillna(self.df['price'].mean())
        if 'sales' in self.df.columns: 
            self.df['sales'] = self.df['sales'].fillna(self.df['sales'].median())
            
        self.metrics["nulls_imputed"] = initial_null_count

    def apply_critical_cleaning(self):
        if 'store_name' in self.df.columns:
            self.df = self.df.dropna(subset=['store_name'])
            self.df = self.df[self.df['store_name'].astype(str).str.lower() != 'none']
            
            # Remove trailing spaces and expand abbreviations
            self.df['store_name'] = self.df['store_name'].apply(
                lambda name: str(name).strip().replace("Str.", "Store") if pd.notna(name) else name
            )

    def fix_negative_values(self):
        negatives_found = 0
        for column in ['price', 'sales']:
            if column in self.df.columns:
                negatives_found += (self.df[column] < 0).sum()
                # Use a lambda function to convert all numbers to their absolute (positive) value
                self.df[column] = self.df[column].apply(lambda x: abs(x) if pd.notna(x) else x)
                
        self.metrics["negatives_fixed"] = negatives_found

    def standardize_dates_and_score(self, total_initial_cells):
        if 'date' in self.df.columns:
            self.df['date'] = self.df['date'].astype(str).str.strip().str.replace(r'^-', '', regex=True)
            
            # Convert to datetime assuming day comes first (European/BR format)
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce', dayfirst=True)
            self.df = self.df.dropna(subset=['date'])
            self.df['date'] = self.df['date'].dt.strftime('%Y-%m-%d')
        
        # Health Score
        total_errors = (self.metrics["duplicates_removed"] * self.df.shape[1]) + self.metrics["nulls_imputed"] + self.metrics["negatives_fixed"]
        
        if total_initial_cells > 0:
            calculated_score = 100.0 - ((total_errors / total_initial_cells) * 100)
            self.metrics["health_score"] = round(max(0.0, calculated_score), 1)

if 'is_processing_complete' not in st.session_state:
    st.session_state.is_processing_complete = False

if 'completed_steps' not in st.session_state:
    st.session_state.completed_steps = [False] * 5 

with st.sidebar:
    st.write("") 
    st.image("verodatalogo.png", use_container_width=True)
    st.divider()
    
    st.markdown("<h3 style='text-align: center; color: #313638;'>CleanFlow Tool</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 14px; color: #666; margin-bottom: 20px;'>Initialize processing to apply data governance and engineering rules to raw data.</p>", unsafe_allow_html=True)
    
    run_cleaning_btn = st.button("RUN CLEANING", use_container_width=True)
    
    st.divider()
    st.markdown("<p style='text-align: center; font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase;'>VeroData System Health: Operational</p>", unsafe_allow_html=True)

tab_upload, tab_clean, tab_export = st.tabs(["📤 Upload", "🪄 Clean", "📤 Export"])

with tab_upload:
    st.subheader("Raw Data Import")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], label_visibility="collapsed")
    
    if uploaded_file:
        raw_dataframe = pd.read_csv(uploaded_file)
        st.dataframe(raw_dataframe.head(), use_container_width=True)

with tab_clean:
    st.subheader("CleanFlow Rules Engine")
    rules_placeholder = st.empty()

    def render_progress_checklist(status_list):
        unique_id = str(time.time()) # DuplicateElementId 
        
        with rules_placeholder.container():
            st.checkbox("🗑️ **Remove Duplicates**", value=status_list[0], disabled=True, key=f"c1_{unique_id}")
            st.checkbox("🧮 **Impute Missing Values**", value=status_list[1], disabled=True, key=f"c2_{unique_id}")
            st.checkbox("🧹 **Critical Cleaning**", value=status_list[2], disabled=True, key=f"c3_{unique_id}")
            st.checkbox("⚡ **Lambda Engine (Negatives)**", value=status_list[3], disabled=True, key=f"c4_{unique_id}")
            st.checkbox("📅 **Regex Standardization (Dates)**", value=status_list[4], disabled=True, key=f"c5_{unique_id}")

    render_progress_checklist(st.session_state.completed_steps)

with tab_export:
    if uploaded_file is not None:
        
        if run_cleaning_btn:
            # Reset the checkbox
            st.session_state.completed_steps = [False] * 5
            st.session_state.is_processing_complete = False
            render_progress_checklist(st.session_state.completed_steps)
            
            pipeline = VeroDataPipeline(raw_dataframe)
            total_cells = raw_dataframe.shape[0] * raw_dataframe.shape[1]
            
            with st.spinner('Removing duplicate records...'):
                pipeline.remove_duplicates()
                time.sleep(0.6) 
                st.session_state.completed_steps[0] = True
                render_progress_checklist(st.session_state.completed_steps) 

            with st.spinner('Imputing missing values...'):
                pipeline.impute_missing_values()
                time.sleep(0.6)
                st.session_state.completed_steps[1] = True
                render_progress_checklist(st.session_state.completed_steps)

            with st.spinner('Applying critical cleaning...'):
                pipeline.apply_critical_cleaning()
                time.sleep(0.6)
                st.session_state.completed_steps[2] = True
                render_progress_checklist(st.session_state.completed_steps)

            with st.spinner('Fixing negative signs with Lambda...'):
                pipeline.fix_negative_values()
                time.sleep(0.6)
                st.session_state.completed_steps[3] = True
                render_progress_checklist(st.session_state.completed_steps)

            with st.spinner('Standardizing dates using Regex...'):
                pipeline.standardize_dates_and_score(total_cells)
                time.sleep(0.6)
                st.session_state.completed_steps[4] = True
                render_progress_checklist(st.session_state.completed_steps)

            # Save the final results to session state
            st.session_state.clean_df = pipeline.df
            st.session_state.metrics = pipeline.metrics
            st.session_state.is_processing_complete = True
            st.success("✨ Data Cleaned Successfully! Check the 'Clean' tab for the progress log.")

        # Display results after the processing is done
        if st.session_state.is_processing_complete:
            left_column, right_column = st.columns([2.5, 1])
            
            with left_column:
                st.markdown("### Cleaning Summary")
                metric_col1, metric_col2 = st.columns(2)
                metric_col1.metric("Duplicates", f"{st.session_state.metrics['duplicates_removed']} removed")
                metric_col2.metric("Standardization", "Date format standardized")
                
                metric_col3, metric_col4 = st.columns(2)
                metric_col3.metric("Strings", "White spaces trimmed")
                metric_col4.metric("Missing Data", f"{st.session_state.metrics['nulls_imputed']} imputed")
                
                st.dataframe(st.session_state.clean_df.head(10), use_container_width=True)
                
            with right_column:
                st.markdown("### Export Data")
                
                csv_data = st.session_state.clean_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download CSV", 
                    data=csv_data, 
                    file_name="verodata_clean.csv", 
                    type="primary", 
                    use_container_width=True
                )
                
                st.write("")
                st.write("")
                st.write("")
                st.markdown(f"""
                    <div style="background-color: #313638; padding: 25px; border-radius: 12px; color: white; text-align: center;">
                        <p style="font-size: 11px; font-weight: bold; color: #E8E9EB; letter-spacing: 1px;">DATA HEALTH SCORE</p>
                        <h1 style="font-size: 50px; color: #F09D51; margin: 5px 0;">{st.session_state.metrics['health_score']}%</h1>
                        <p style="font-size: 13px; color: #d9dadc;">Dataset validated successfully.</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Please upload a file first to begin.")
