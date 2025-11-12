import streamlit as st
import pandas as pd
from datetime import date, datetime

# st.set_page_config(page_title="Reverse Mortgage Calculator", layout="centered")


st.title("🏠 Reverse Mortgage Calculator")

# # --- Load PLF CSVs ---
# pfl_chart = pd.read_excel("PFL.xlsx")

# hecm_plf = pfl_chart[["AGE", "HECM"]]
# hecm_plf.columns = ["AGE", "PLF"]

# jumbo_plf = pfl_chart[["AGE", "Jumbo"]]
# jumbo_plf.columns = ["AGE", "PLF"]


hecm_plf = [{'AGE': 60, 'PLF': 0.0}, {'AGE': 61, 'PLF': 0.0}, {'AGE': 62, 'PLF': 0.376}, {'AGE': 63, 'PLF': 0.383}, {'AGE': 64, 'PLF': 0.39}, {'AGE': 65, 'PLF': 0.397}, {'AGE': 66, 'PLF': 0.4042}, {'AGE': 67, 'PLF': 0.4114}, {'AGE': 68, 'PLF': 0.4186}, {'AGE': 69, 'PLF': 0.4258}, {'AGE': 70, 'PLF': 0.433}, {'AGE': 71, 'PLF': 0.4386}, {'AGE': 72, 'PLF': 0.4442}, {'AGE': 73, 'PLF': 0.4498}, {'AGE': 74, 'PLF': 0.4554}, {'AGE': 75, 'PLF': 0.461}, {'AGE': 76, 'PLF': 0.4698}, {'AGE': 77, 'PLF': 0.4786}, {'AGE': 78, 'PLF': 0.4874}, {'AGE': 79, 'PLF': 0.4962}, {'AGE': 80, 'PLF': 0.505}, {'AGE': 81, 'PLF': 0.5168}, {'AGE': 82, 'PLF': 0.5286}, {'AGE': 83, 'PLF': 0.5404}, {'AGE': 84, 'PLF': 0.5522}, {'AGE': 85, 'PLF': 0.564}, {'AGE': 86, 'PLF': 0.5774}, {'AGE': 87, 'PLF': 0.5908}, {'AGE': 88, 'PLF': 0.6042}, {'AGE': 89, 'PLF': 0.6176}, {'AGE': 90, 'PLF': 0.631}, {'AGE': 91, 'PLF': 0.6377}, {'AGE': 92, 'PLF': 0.6444}, {'AGE': 93, 'PLF': 0.6511}, {'AGE': 94, 'PLF': 0.6578}, {'AGE': 95, 'PLF': 0.6645}, {'AGE': 96, 'PLF': 0.6712}, {'AGE': 97, 'PLF': 0.6779}, {'AGE': 98, 'PLF': 0.6846}, {'AGE': 99, 'PLF': 0.6913}]
jumbo_plf = [{'AGE': 60, 'PLF': 0.419}, {'AGE': 61, 'PLF': 0.424}, {'AGE': 62, 'PLF': 0.429}, {'AGE': 63, 'PLF': 0.435}, {'AGE': 64, 'PLF': 0.44}, {'AGE': 65, 'PLF': 0.446}, {'AGE': 66, 'PLF': 0.453}, {'AGE': 67, 'PLF': 0.46}, {'AGE': 68, 'PLF': 0.468}, {'AGE': 69, 'PLF': 0.477}, {'AGE': 70, 'PLF': 0.487}, {'AGE': 71, 'PLF': 0.497}, {'AGE': 72, 'PLF': 0.508}, {'AGE': 73, 'PLF': 0.516}, {'AGE': 74, 'PLF': 0.524}, {'AGE': 75, 'PLF': 0.534}, {'AGE': 76, 'PLF': 0.544}, {'AGE': 77, 'PLF': 0.556}, {'AGE': 78, 'PLF': 0.569}, {'AGE': 79, 'PLF': 0.581}, {'AGE': 80, 'PLF': 0.59}, {'AGE': 81, 'PLF': 0.6}, {'AGE': 82, 'PLF': 0.603}, {'AGE': 83, 'PLF': 0.606}, {'AGE': 84, 'PLF': 0.608}, {'AGE': 85, 'PLF': 0.61}, {'AGE': 86, 'PLF': 0.611}, {'AGE': 87, 'PLF': 0.611}, {'AGE': 88, 'PLF': 0.611}, {'AGE': 89, 'PLF': 0.611}, {'AGE': 90, 'PLF': 0.611}, {'AGE': 91, 'PLF': 0.611}, {'AGE': 92, 'PLF': 0.611}, {'AGE': 93, 'PLF': 0.611}, {'AGE': 94, 'PLF': 0.611}, {'AGE': 95, 'PLF': 0.611}, {'AGE': 96, 'PLF': 0.611}, {'AGE': 97, 'PLF': 0.611}, {'AGE': 98, 'PLF': 0.611}, {'AGE': 99, 'PLF': 0.611}]


hecm_plf = pd.DataFrame(hecm_plf)
jumbo_plf = pd.DataFrame(jumbo_plf)

# input("--")


# # --- SIDEBAR: Borrower & Property Inputs ---
# st.sidebar.header("👤 Borrower Details")

# num_borrowers = st.sidebar.number_input("Number of Borrowers", min_value=1, max_value=3, value=1)

# borrowers = []
# today = date.today()
# min_date = date(1900, 1, 1)

# for i in range(int(num_borrowers)):
#     st.sidebar.markdown(f"**Borrower {i+1}**")
#     name = st.sidebar.text_input(f"Name {i+1}")

#     dob = st.sidebar.date_input(
#         f"DOB {i+1}",
#         min_value=min_date,
#         max_value=today,
#         value=date(1960, 1, 1),
#         key=f"dob_{i}"
#     )
#     address = st.sidebar.text_area(f"Address {i+1}", key=f"addr_{i}")
#     borrowers.append({"name": name, "dob": dob, "address": address})



# # --- Borrower Input Section ---
st.header("👤 Borrower Details")

# num_borrowers = st.number_input("Number of Borrowers", min_value=1, max_value=3, value=1)
num_borrowers = 2
borrowers = []
today = date.today()
min_date = date(1900, 1, 1)


def calculate_age(dob, today=None):
    if today is None:
        today = date.today()

    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day

    # Adjust if the current month/day hasn't been reached yet
    if days < 0:
        months -= 1
    if months < 0:
        years -= 1
        months += 12

    return years, months


for i in range(int(num_borrowers)):
    with st.expander(f"Borrower {i+1}"):
        left, right = st.columns(2)
 
        first_name = left.text_input(f"First Name (Borrower {i+1})")
        last_name = right.text_input(f"Last Name (Borrower {i+1})")

        left, right = st.columns(2)

        dob = left.date_input(
            f"Date of Birth (Borrower {i+1})",
            min_value=min_date,
            max_value=today,
            value=date(1960, 1, 1)
        )

        # age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        age = calculate_age(dob, today)
        # age = (today - dob).days // 365
        right.text_input("Age", value = f"{age[0]} Years {age[1]} Months", disabled = True, key = f"Age{i}")

        if age[1] >=6 :
            age_used = age[0] + 1 
        else:
            age_used = age[0]

        address = st.text_area(f"Address (Borrower {i+1})")
        borrowers.append({"name": first_name,"last_name":last_name, "dob": dob, "address": address, "years" : age[0], "months" : age[1], "age_used" : age_used})



# # --- Calculate youngest borrower's age ---
# ages = [(today - b["dob"]).days // 365 for b in borrowers if b["dob"]]

ages = [b["age_used"] for b in borrowers if b["dob"]]
if ages:
    borrower_age = min(ages)
    st.write(f"**Youngest Borrower Age:** {borrower_age}")
else:
    st.warning("Please enter DOB for all borrowers.")
    st.stop()



# # --- Home details ---
# st.header("🏡 Property Details")


left, right = st.columns(2)
home_value    = left.number_input("Home Value ($)", min_value=0.0, format="%.2f")

existing_loan = right.number_input("Outstanding Loan ($)", min_value=0.0, format="%.2f")

# --- Helper to get PLF from chart ---
def get_plf(plf_df, age):
    eligible_ages = plf_df["AGE"].values
    # If age less than min or greater than max, clamp
    if age < eligible_ages.min():
        age = eligible_ages.min()
    elif age > eligible_ages.max():
        age = eligible_ages.max()
    return float(plf_df.loc[plf_df["AGE"] <= age, "PLF"].iloc[-1])

# --- Compute Results ---
hecm_plf_val = get_plf(hecm_plf, borrower_age)
jumbo_plf_val = get_plf(jumbo_plf, borrower_age)

results = []

for label, plf_val in [("HECM", hecm_plf_val), ("Jumbo", jumbo_plf_val)]:
    if home_value > 1150000 and label == "HECM":
        principal_limit = "NA"        
        avail_proceeds = "NA"
        eligible = "NA"
        results.append({
            "Type": label,
            "PLF": "NA",
            "Principal Limit ($)": "NA",
            "Available Proceeds ($)": "NA",
            "Eligible?": "NA"
        })

    else:
        principal_limit = home_value * plf_val
        avail_proceeds = principal_limit - existing_loan
        eligible = "✅ Yes" if principal_limit > existing_loan else "❌ No"

        results.append({
            "Type": label,
            "PLF": round(plf_val, 3),
            "Principal Limit ($)": f"{principal_limit:,.2f}",
            "Available Proceeds ($)": f"{avail_proceeds:,.2f}",
            "Eligible?": eligible
        })

# --- Display Results ---
if home_value > 0:
    st.subheader("📊 Results Summary")
    st.dataframe(pd.DataFrame(results))
else:
    st.info("Enter Home Value and Loan to calculate results.")


