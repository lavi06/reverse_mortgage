import streamlit as st
import pandas as pd
from datetime import date, datetime
import requests


st.set_page_config(page_title="Reverse Mortgage Calculator", layout="wide")
# st.title("🏠 Reverse Mortgage Calculator")



def download_excel():

    url = "https://github.com/lavi06/reverse_mortgage/raw/refs/heads/main/MOOM.xlsx"

    # response = requests.get(url)
    # response.raise_for_status()
    # dfs = pd.read_excel(response.content, sheet_name=None)   # returns a dict of DataFrames
    dfs = pd.read_excel("MOOM.xlsx",  sheet_name=None)

    DB_fixed_rate  = dfs["SecureEquity"]
    DB_ARM         = dfs["ARM"]
    DB_HECM5       = dfs["HECM"]
    DB_HECM_Fixed  = dfs["HECM_Fixed"]

    ##############################
    # pfl_chart = pd.read_excel("PFL.xlsx")
    pfl_chart = dfs["PLF"]
    hecm_plf = pfl_chart[["AGE", "HECM"]]
    hecm_plf.columns = ["AGE", "PLF"]

    jumbo_plf = pfl_chart[["AGE", "Jumbo"]]
    jumbo_plf.columns = ["AGE", "PLF"]
    ##############################

    return DB_fixed_rate, DB_ARM, DB_HECM5, DB_HECM_Fixed, hecm_plf, jumbo_plf




DB_fixed_rate, DB_ARM, DB_HECM5, DB_HECM_Fixed, hecm_plf, jumbo_plf = download_excel()


######################################################


# --- SIDEBAR: Borrower & Property Inputs ---
st.sidebar.header("👤 Borrower Details")

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
    with st.sidebar.expander(f"Borrower {i+1}"):
  
        first_name = st.text_input(f"Name", key = f"Name {i}")
  
        left, right = st.columns(2)

        dob = left.date_input(
            "Date of Birth",
            min_value = min_date,
            max_value = today,
            value = date(1960, 1, 1),
            key = f"dob - {i}"
        )

        age = calculate_age(dob, today)

        # right.text_area("Age", value = f"{age[0]} Y {age[1]} M", disabled = True, key = f"Age{i}", height=10)
        right.badge("")
        right.badge(f"{age[0]} Y {age[1]} M")

        if age[1] >=6 :
            age_used = age[0] + 1 
        else:
            age_used = age[0]

        address = st.text_area(f"Address (Borrower {i+1})")
        borrowers.append({"name": first_name,"dob": dob, "address": address, "years" : age[0], "months" : age[1], "age_used" : age_used})


# # --- Calculate youngest borrower's age ---
# ages = [(today - b["dob"]).days // 365 for b in borrowers if b["dob"]]

if borrowers:
    youngest_borrower = min(borrowers, key=lambda x: x["age_used"])

    st.sidebar.write(f"**Youngest Borrower Age:** {youngest_borrower['age_used']}")
    st.sidebar.write(f"**Name :** {youngest_borrower['name']}")
    st.sidebar.write(f"**D.O.B:** {youngest_borrower['dob']}")
    st.sidebar.markdown("------")

    borrower_age = youngest_borrower["age_used"]



# # --- Home details ---
# st.header("🏡 Property Details")


left, right = st.columns(2)
home_value    = left.number_input("Home Value ($)", min_value=0.0, format="%.2f")
# home_value = 1000000
existing_loan = right.number_input("Outstanding Loan ($)", min_value=0.0, format="%.2f")

left, right = st.columns(2)
line_of_credit = left.number_input("Line of Credit ($)", min_value=0.0, format="%.2f")



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

        results.append({
            "Type": label,
            "PLF": "NA",
            "Principal Limit ($)": "NA",
            "Total Avail Proceeds" : "NA",
            "Available Proceeds ($)": "NA",
            "Eligible": "NA"
        })

    else:
        principal_limit = home_value * plf_val
        total_proceeds = principal_limit - existing_loan + line_of_credit
        avail_proceeds = principal_limit - existing_loan
        eligible = "✅ Yes" if principal_limit > existing_loan else "❌ No"

        results.append({
            "Type": label,
            "PLF": round(plf_val, 3),
            "Principal Limit ($)"   : principal_limit,
            "Total Avail Proceeds"  : total_proceeds,
            "Available Proceeds ($)": avail_proceeds,
            "Eligible": eligible
        })


# "Principal Limit ($)": f"{principal_limit:,.0f}",


HECM_tab, Jumbo_tab, config_tab = st.tabs(["HECM", "JUMBO", "Config"])

if home_value > 0:

    with HECM_tab:

        result = results[0]
        a,b,c,d = st.columns(4)

        principal_limit = result["Principal Limit ($)"]
        total_proceeds  = result["Total Avail Proceeds"]
        avail_proceeds  = result["Available Proceeds ($)"]
        # eligible = "✅ Yes" if principal_limit > existing_loan else "❌ No"
        
        try:
            PL_Utilised = (1 - float(avail_proceeds)/float(principal_limit))
        except:
            PL_Utilised = 0

        def show_value(value,sign = None):
            try:
                if sign == "%":
                    return f"{value*100:.2f}%"
                else:
                    return f"{value:,.0f}"
            except:
                return value


        a.metric(
                "PLF %",
                show_value(result['PLF'], "%"),
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        b.metric(
                "Principal Limit $",
                show_value(principal_limit),
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        c.metric(
                "Total Avail. Proceed $",
                show_value(total_proceeds),
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        d.metric(
                "Additional Avail. Proceed $",
                show_value(avail_proceeds),
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )
        

        a,b,c,d = st.columns(4)
        a.metric(
                "PL_Utilised %",
                f"{PL_Utilised*100:0.2f}%",
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        b.metric(
                "Eligibility",
                result["Eligible"],
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )



        if result["Eligible"] == "✅ Yes":
            ####################################
            st.markdown("-----")

            st.write("HECM Monthly Adj. 1Y CMT 5 CAP")

            sec1,sec2 = st.columns(2)


            HECM_origination = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=0, step=1, format="%d%%")
            adj_avail_proceeds = float(avail_proceeds) * (1-HECM_origination/100)

            s1,s2 = sec2.columns(2)
            HECM_fee = s1.number_input("Add Fee", value=0, step=1)
            adj_avail_proceeds = adj_avail_proceeds - HECM_fee

            df = DB_HECM5[DB_HECM5["Offer"] == "HECM5"]

            if PL_Utilised <= 0.1:
                col = "0-10%"
            elif PL_Utilised <= 0.2:
                col = "10-20%"
            elif PL_Utilised <= 0.3:
                col = "20-30%"
            elif PL_Utilised <= 0.4:
                col = "30-40%"
            elif PL_Utilised <= 0.5:
                col = "40-50%"
            elif PL_Utilised <= 0.6:
                col = "50-60%"
            elif PL_Utilised <= 0.7:
                col = "60-70%"
            elif PL_Utilised <= 0.8:
                col = "70-80%"
            elif PL_Utilised <= 0.9:
                col = "80-90%"
            else:
                col = "90-100%"

            df = df[["Margin%", col]]
            df["Margin%"] = df["Margin%"].astype(str) + "%"
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            product_data = df.to_dict(orient="records")

            df = pd.DataFrame(product_data)
            sec1.dataframe(df)


            st.markdown("-----")

            st.write("HECM Fixed Rate")

            sec1,sec2 = st.columns(2)

            HECMFixed_origination = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=0, step=1, format="%d%%", key = f"HECMFixed_origination")
            adj_avail_proceeds = float(avail_proceeds) * (1-HECMFixed_origination/100)

            s1,s2 = sec2.columns(2)
            HECMFixed_fee = s1.number_input("Add Fee", value=0, step=1, key = "HECMFixed_fee")
            adj_avail_proceeds = adj_avail_proceeds - HECMFixed_fee


            df = DB_HECM_Fixed[DB_HECM_Fixed["Offer"] == "HECM Fixed"]

            df = df[["Extra Fee", "Rate", "Premium"]]
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            product_data = df.to_dict(orient="records")

            df = pd.DataFrame(product_data)
            sec1.dataframe(df)





    with Jumbo_tab:

        result = results[1]
        a,b,c,d = st.columns(4)

        principal_limit = result["Principal Limit ($)"]
        total_proceeds  = result["Total Avail Proceeds"]
        avail_proceeds  = result["Available Proceeds ($)"]
        # eligible = "✅ Yes" if principal_limit > existing_loan else "❌ No"
        
        try:
            PL_Utilised = (1 - float(avail_proceeds)/float(principal_limit))
        except:
            PL_Utilised = 0

        a.metric(
                "PLF %",
                f"{result['PLF']*100:0.2f}%",
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        b.metric(
                "Principal Limit $",
                f"{principal_limit:,.0f}",
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        c.metric(
                "Total Avail. Proceed $",
                f"{total_proceeds:,.0f}",
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        d.metric(
                "Additional Avail. Proceed $",
                f"{avail_proceeds:,.0f}",
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )
        

        a,b,c,d = st.columns(4)
        a.metric(
                "PL_Utilised %",
                f"{PL_Utilised*100:0.2f}%",
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )

        b.metric(
                "Eligibility",
                result["Eligible"],
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )


        ####################################
        st.markdown("-----")

        st.write("SecureEquity Fixed Plus")

        sec1,sec2 = st.columns(2)

        # SecureEquity_origination = sec1.number_input("origination Fee %", value = 4)
        SecureEquity_origination = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=4, step=1, format="%d%%")
        adj_avail_proceeds = float(avail_proceeds) * (1-SecureEquity_origination/100)

        s1,s2 = sec2.columns(2)
        SecureEquityFixed_fee = s1.number_input("Add Fee", value=0, step=1, key = "SecureEquityFixed_fee")
        adj_avail_proceeds = adj_avail_proceeds - SecureEquityFixed_fee


        df = DB_fixed_rate[DB_fixed_rate["Offer"] == "SecureEquity Fixed Plus"]
        df = df[["Rate Type", "Rate", "Premium"]]
        df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"
 
        product_data = df.to_dict(orient="records")


        df = pd.DataFrame(product_data)
        sec1.dataframe(df)


        ####################################
        st.markdown("-----")

        st.write("SecureEquity Fixed Plus")

        sec1,sec2 = st.columns(2)

        # SecureEquity_origination = sec1.number_input("origination Fee %", value = 4)
        SecureEquityPlus_origination = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=1, step=1, format="%d%%", key = "Plus_origination")
        adj_avail_proceeds = float(avail_proceeds) * (1-SecureEquityPlus_origination/100)

        s1,s2 = sec2.columns(2)
        SecureEquityFixedPlus_fee = s1.number_input("Add Fee", value=0, step=1, key = "SecureEquityFixedPlus_fee")
        adj_avail_proceeds = adj_avail_proceeds - SecureEquityFixedPlus_fee

        df = DB_fixed_rate[DB_fixed_rate["Offer"] == "SecureEquity Fixed"]
        df = df[["Rate Type", "Rate", "Premium"]]

        df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

        product_data = df.to_dict(orient="records")

        df = pd.DataFrame(product_data)
        sec1.dataframe(df)


        ####################################
        st.markdown("-----")

        st.write("SecureEquity ARM")


        sec1,sec2 = st.columns(2)
        ARM_origination = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=1, step=1, format="%d%%", key = "ARM_origination")
        adj_avail_proceeds = float(avail_proceeds) * (1-ARM_origination/100)

        s1,s2 = sec2.columns(2)
        ARM_fee = s1.number_input("Add Fee", value=0, step=1, key = "ARM_fee")
        adj_avail_proceeds = adj_avail_proceeds - ARM_fee


        df = DB_ARM[DB_ARM["Offer"] == "ARM"]

        if PL_Utilised < 0.25:
            col = "0-25%"
        elif PL_Utilised <= 0.8:
            col = "25-80%"
        elif PL_Utilised <= 0.9:
            col = "80.01-90%"
        else:
            col = "90.01-100%"


        df = df[["Rate Type", "Margin%", col]]
        df["Margin%"] = df["Margin%"].astype(str) + "%"

        df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"
        product_data = df.to_dict(orient="records")
 
        df = pd.DataFrame(product_data)
        sec1.dataframe(df)




# # --- Display Results ---
# if home_value > 0:
#     st.subheader("📊 Results Summary")
#     st.dataframe(pd.DataFrame(results))
else:
    with HECM_tab:
        st.info("Enter Home Value and Loan to calculate results.")
    with Jumbo_tab:
        st.info("Enter Home Value and Loan to calculate results.")




with config_tab:
    st.header("⚙️ Configuration Database")


    hecm_plf_tab, jumbo_plf_tab, fixed_rate, arm, hemc5, hecm_fixed = st.tabs(["HECM", "JUMBO","SecureEquity Fixed", "ARM", "HEMC5", "HECM Fixed"])

    with hecm_plf_tab:
        s1, s2 = st.columns(2)
        s1.dataframe(
            hecm_plf
        )

    with jumbo_plf_tab:
        s1, s2 = st.columns(2)
        s1.dataframe(
            jumbo_plf
        )


    with fixed_rate:
        DB_fixed_rate = st.data_editor(
            DB_fixed_rate,
            num_rows="dynamic",
            use_container_width=True,
        )

    with arm:
        DB_ARM = st.data_editor(
            DB_ARM,
            num_rows="dynamic",
            use_container_width=True,
        )

    with hemc5:
        DB_HEMC5 = st.data_editor(
            DB_HECM5,
            num_rows="dynamic",
            use_container_width=True,
        )

    with hecm_fixed:
        DB_HEMC = st.data_editor(
            DB_HECM_Fixed,
            num_rows="dynamic",
            use_container_width=True,
        )

    st.write("Contact developer hggoyal06@gmail.com to change the config file")

