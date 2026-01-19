import streamlit as st
import pandas as pd
from flo_finance_v2 import flo_finance, flo_finance_alt

# -------------------------
# Page Config (must come first)
# -------------------------
st.set_page_config(
	page_title="Florence Financial Impact",
	layout="wide",
	initial_sidebar_state="collapsed"
)

# -------------------------
# Global CSS (mobile friendly tweaks)
# -------------------------
st.markdown(
	"""
	<style>
	@media (max-width: 768px) {
		.block-container {
			padding-left: 0.5rem !important;
			padding-right: 0.5rem !important;
		}
		div[role="radiogroup"] label {
			font-size: 14px !important;
		}
		div[data-testid="stMarkdownContainer"] {
			font-size: 14px !important;
		}
		input[type="text"], input[type="number"] {
			font-size: 14px !important;
			padding: 4px !important;
		}
	}
	</style>
	""",
	unsafe_allow_html=True
)

# -------------------------
# Load CSVs
# -------------------------
@st.cache_data
def load_health_systems():
	df = pd.read_csv("health_system.csv")
	df = df.sort_values(by="Health_System_Name")
	return df.set_index("Health_System_ID").to_dict(orient="index")

@st.cache_data
def load_hospitals():
	df = pd.read_csv("all_hospitals.csv")
	df = df.sort_values(by="Hospital_Name")
	return df.set_index("CCN#").to_dict(orient="index")

health_systems = load_health_systems()
hospitals = load_hospitals()

# -------------------------
# Streamlit UI
# -------------------------
st.title("Florence Financial Impact")
st.caption("Note: If hospital or health system does not appear in the dropdown, there was no publicly reported Contracted Labor data to the HCRIS for that organization")
mode = st.radio("Search for Health System or Hospital", ["Health System", "Individual Hospital"])

# -------------------------
# Styled read-only fields
# -------------------------
def styled_readonly(label, value):
	st.markdown(
		f"""
		<div style="background-color:#cfe2f3;padding:10px 12px;border-radius:5px;margin-bottom:8px;font-size:16px;">
		<b>{label}:</b> {value}
		</div>
		""",
		unsafe_allow_html=True
	)

# -------------------------
# Get defaults based on mode
# -------------------------
if mode == "Health System":
	name_lookup = {v["Health_System_Name"]: k for k, v in health_systems.items()}
	choice_name = st.selectbox("Choose a health system (type to search)", sorted(name_lookup.keys()))
	defaults = health_systems[name_lookup[choice_name]]

	read_only_data = {
		"Health System Name": defaults["Health_System_Name"],
		"Bed Size": round(float(defaults["Bed_Size"])),
		"States": defaults["State(s)"],
		"Affiliated Hospitals": defaults["Affiliated_Hospitals"],
	}
else:
	states = sorted(set(v["State"] for v in hospitals.values()))
	chosen_state = st.selectbox("Choose a state", states)
	hospitals_in_state = {k: v for k, v in hospitals.items() if v["State"] == chosen_state}
	name_lookup = {v["Hospital_Name"]: k for k, v in hospitals_in_state.items()}
	choice_name = st.selectbox("Choose a hospital (type to search)", sorted(name_lookup.keys()))
	defaults = hospitals[name_lookup[choice_name]]

	read_only_data = {
		"Hospital Name": defaults["Hospital_Name"],
		"Bed Size": round(float(defaults["Bed_Size"])),
		"State": defaults["State"],
		"Health Care Affiliation": defaults.get("Health_System_Name", "N/A"),
	}

# -------------------------
# Sidebar notes
# -------------------------
with st.sidebar.expander("ℹ️ Data & Calculation Notes", expanded=False):
	agency_fte = defaults.get("Agency_Labor_FTE", "N/A")
	try:
		agency_fte = round(float(agency_fte), 1)
	except:
		pass

	st.markdown(
		f"""
		<div style="background-color:#b2dfdb;padding:10px;border-radius:5px;font-style:italic;">
		<p>1. All rate and staffing information pulled from HCRIS FY2024. Agency FTE use ({agency_fte}) assumes 80% RN mix at 1872 hours annually.</p>
		<p>2. Savings estimated over a 3-year period.</p>
		</div>
		""",
		unsafe_allow_html=True
	)

# -------------------------
# Calculation Section (shared logic)
# -------------------------
rn_needed = round(float(defaults.get("Estimated_RN_Need", 0)), 1)
agency_gt_staff = str(defaults.get("Agency>Staff", True)).lower() == "true"

st.subheader("Current Rates/Staffing (Can Edit)")

st.markdown("<label style='font-weight:bold;font-size:20px;'>Estimated RN Need</label>", unsafe_allow_html=True)
rn_input = st.text_input("", f"{rn_needed:.1f}", label_visibility="collapsed")
try:
	rn_needed = round(float(rn_input), 1)
except:
	pass

st.markdown(
	"""
	<style>
	input[type="text"] { font-weight:bold; font-size:20px; }
	</style>
	""",
	unsafe_allow_html=True
)

staff_rate = st.number_input("Staff Labor Rate ($)", value=float(defaults["Staff_Labor_Rate"]), step=0.01, format="%.2f")
agency_rate = st.number_input("Agency Labor Rate ($)", value=float(defaults["Agency_Labor_Rate"]), step=0.01, format="%.2f")

if agency_gt_staff:
	result = flo_finance(staff_rate, agency_rate, rn_needed)
	badge = "<span style='background:#d4edda;color:#155724;padding:4px 8px;border-radius:12px;font-size:12px;font-weight:bold;'>STANDARD FORMULA</span>"
else:
	result = flo_finance_alt(staff_rate, agency_rate, rn_needed)
	badge = "<span style='background:#fff3cd;color:#856404;padding:4px 8px;border-radius:12px;font-size:12px;font-weight:bold;'>ALT FORMULA</span>"

st.markdown(
	f"""
	<div style='border:2px solid #444;padding:10px;border-radius:5px;display:flex;justify-content:space-between;align-items:center;'>
		<span style='font-weight:bold;font-size:18px;'>Florence Financial Savings</span>
		{badge}
	</div>
	<div style='background:#d4edda;padding:15px;border-radius:5px;font-size:20px;font-weight:bold;margin-top:10px;'>
		Estimated Financial Savings: ${result:,.2f}
	</div>
	<div style='background:#e9ecef;padding:10px;border-radius:5px;font-size:16px;font-style:italic;margin-top:8px;'>
		Inputs → Staff Labor Rate: ${staff_rate:,.2f}, Agency Labor Rate: ${agency_rate:,.2f}, Estimated RN Need: {rn_needed:.1f}
	</div>
	""",
	unsafe_allow_html=True
)

# -------------------------
# Information Section
# -------------------------
st.subheader("Information")
for label, value in read_only_data.items():
	styled_readonly(label, value)

