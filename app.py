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
  
        left, right = st.columns(2)
        first_name = left.text_input(f"First Name", key = f"FirstName {i}")
        last_name = right.text_input(f"Last Name", key = f"LastName {i}")


        toggle = st.toggle("Select Age", key = f"Toggle {i}") 

        if not toggle:

            left, right = st.columns(2)

            dob = left.date_input(
                "Date of Birth",
                min_value = min_date,
                max_value = today,
                value = date(1900, 1, 1),
                key = f"dob - {i}"
            )

            age = calculate_age(dob, today)

            right.badge("")
            right.badge(f"{age[0]} Y {age[1]} M")

        else:
            left, right,c = st.columns(3)

            age_year  = left.number_input("Years"  ,min_value=0 ,max_value=120 ,step=1 ,format="%d")
            age_month = right.number_input("Months",min_value=0 ,max_value=12 ,step=1 ,format="%d")
            dob = f"01-{age_month}-{age_year}"
            age = [age_year, age_month]


        if age[1] >=6 :
            age_used = age[0] + 1 
        else:
            age_used = age[0]


        address = st.text_input(f"Address", key = f"Address {i}")

        left, right = st.columns(2)
        city = left.text_input(f"City", key = f"City {i}")
        state = right.text_input(f"State", key = f"State {i}")
        zipcode = st.text_input(f"Zipcode", key = f"Zipcode {i}")

        mobile = st.text_input("Mobile Phone", placeholder="Enter 10-digit mobile number", key = f"Mobile {i}")
        home_phone = st.text_input("Home Phone" , placeholder="Enter home number", key = f"HomePhone {i}")

        borrowers.append({
            "first_name" : first_name,
            "last_name"  : last_name,
            "dob"    : dob,
            "years"  : age[0],
            "months" : age[1],
            "age_used" : age_used,
            "city"     : city,
            "state"    : state,
            "zipcode"  : zipcode,
            "mobile"   : mobile,
            "home_phone" : home_phone
            })





# # --- Calculate youngest borrower's age ---

if borrowers:
    youngest_borrower = min(borrowers, key=lambda x: x["age_used"])

    st.sidebar.write(f"**Youngest Borrower Age:** {youngest_borrower['age_used']}")
    st.sidebar.write(f"**Name :** {youngest_borrower['first_name']} {youngest_borrower['last_name']}")
    st.sidebar.write(f"**D.O.B:** {youngest_borrower['dob']}")
    st.sidebar.markdown("------")

    borrower_age = youngest_borrower["age_used"]



# # --- Home details ---
# st.header("🏡 Property Details")

left, right = st.columns(2)
home_value    = left.number_input("Home Value ($)", min_value=0.0, format="%.2f")

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




HECM_tab, Jumbo_tab, config_tab = st.tabs(["HECM", "JUMBO", "Config"])

if home_value > 0:

    with HECM_tab:

        result = results[0]
        a,b,c,d = st.columns(4)

        principal_limit = result["Principal Limit ($)"]
        total_proceeds  = result["Total Avail Proceeds"]
        avail_proceeds  = result["Available Proceeds ($)"]
        
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
                "Prev. Line of Credit $",
                show_value(line_of_credit),
                # delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
                width="content",
            )
        try:
            delta = avail_proceeds - line_of_credit
        except:
            delta = None

        d.metric(
                "Current Avail. Proceed $",
                show_value(avail_proceeds),
                delta = show_value(delta),
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

            key = "HECM5"
            st.checkbox("Export - HECM Monthly Adj. 1Y CMT 5 CAP", key = key)

            orgin_fee_pre = 0
            fixed_fee_pre = 5000

            df = DB_HECM5[DB_HECM5["Offer"] == key]


            sec1,sec2, sec3, sec4 = st.columns(4)

            origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value=10, value = orgin_fee_pre, step=1, format="%d%%", key = f"{key}_origination")
            fixed_fee       = sec2.number_input("Fixed Fee", value = fixed_fee_pre, step=1, key = f"{key}_fixed_fee")

            total_fee_charge = (avail_proceeds*origination_fee/100) + fixed_fee

            max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
            max_fee = max_fee[0] if max_fee else "-"


            sec3.badge(f"Input Fee : {total_fee_charge:,.2f}")
            sec3.badge(f"Max Fee : {max_fee}")

            try: fee_applied = min(max_fee, total_fee_charge)
            except: fee_applied = total_fee_charge 

            sec1.write(f"Applied Fee : {fee_applied:,.2f}")

            adj_avail_proceeds = avail_proceeds - fee_applied


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

            s1,s2 = st.columns(2)
            df = pd.DataFrame(product_data)
            s1.dataframe(df)


            ####################################
            st.markdown("-----")

            key = "HECM Fixed"
            st.checkbox("Export - HECM Fixed Rate", key = key)

            sec1,sec2, sec3, sec4 = st.columns(4)

            origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=0, step=1, format="%d%%", key = f"{key}_origination")
            adj_avail_proceeds = avail_proceeds * (1-origination_fee/100)

            fixed_fee = sec2.number_input("Fixed Fee", value=10000, step=1, key = f"{key}_fixed_fee")
            adj_avail_proceeds = adj_avail_proceeds - fixed_fee

            total_fee_charge = avail_proceeds - adj_avail_proceeds
            sec3.badge(f"Input Fee : {total_fee_charge:,.2f}")

            df = DB_HECM_Fixed[DB_HECM_Fixed["Offer"] == key]

            max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
            max_fee = max_fee[0] if max_fee else "-"

            sec3.badge(f"Max Fee : {max_fee}")

            try:
                fee_applied = min(max_fee, total_fee_charge)
            except:
                fee_applied = total_fee_charge 


            adj_avail_proceeds = avail_proceeds - fee_applied
            sec1.write(f"Applied Fee : {fee_applied:,.2f}")


            df = df[["Extra Fee", "Rate", "Premium"]]
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            product_data = df.to_dict(orient="records")

            s1,s2 = st.columns(2)
            df = pd.DataFrame(product_data)
            s1.dataframe(df)





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
        if result["Eligible"] == "✅ Yes":

            st.markdown("-----")

            key = "SecureEquity Fixed Plus"
            st.checkbox("Export - SecureEquity Fixed Plus", key = key)

            sec1,sec2, sec3, sec4 = st.columns(4)

            origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=4, step=1, format="%d%%", key = f"{key}_origination")
            adj_avail_proceeds = avail_proceeds * (1-origination_fee/100)

            fixed_fee = sec2.number_input("Fixed Fee", value=0, step=1, key = f"{key}_fixed_fee")
            adj_avail_proceeds = adj_avail_proceeds - fixed_fee

            total_fee_charge = avail_proceeds - adj_avail_proceeds
            sec3.badge(f"Input Fee : {total_fee_charge:,.2f}")

            df = DB_fixed_rate[DB_fixed_rate["Offer"] == key]

            max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
            max_fee = max_fee[0] if max_fee else "-"

            sec3.badge(f"Max Fee : {max_fee}")

            try:
                fee_applied = min(max_fee, total_fee_charge)
            except:
                fee_applied = total_fee_charge 

            adj_avail_proceeds = avail_proceeds - fee_applied
            sec1.write(f"Applied Fee : {fee_applied:,.2f}")


            df = df[["Rate Type", "Rate", "Premium"]]
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            product_data = df.to_dict(orient="records")
            s1,s2 = st.columns(2)
            df = pd.DataFrame(product_data)
            s1.dataframe(df)



            ####################################
            st.markdown("-----")

            key = "SecureEquity Fixed"
            st.checkbox("Export - SecureEquity Fixed", key = key)

            sec1,sec2, sec3, sec4 = st.columns(4)

            origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=1, step=1, format="%d%%", key = f"{key}_origination")
            adj_avail_proceeds = avail_proceeds * (1-origination_fee/100)

            fixed_fee = sec2.number_input("Fixed Fee", value=0, step=1, key = f"{key}_fixed_fee")
            adj_avail_proceeds = adj_avail_proceeds - fixed_fee

            total_fee_charge = avail_proceeds - adj_avail_proceeds
            sec3.badge(f"Input Fee : {total_fee_charge:,.2f}")

            df = DB_fixed_rate[DB_fixed_rate["Offer"] == key]

            max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
            max_fee = max_fee[0] if max_fee else "-"

            sec3.badge(f"Max Fee : {max_fee}")

            try:
                fee_applied = min(max_fee, total_fee_charge)
            except:
                fee_applied = total_fee_charge 

            adj_avail_proceeds = avail_proceeds - fee_applied
            sec1.write(f"Applied Fee : {fee_applied:,.2f}")


            df = DB_fixed_rate[DB_fixed_rate["Offer"] == "SecureEquity Fixed"]
            df = df[["Rate Type", "Rate", "Premium"]]

            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            product_data = df.to_dict(orient="records")
            s1,s2 = st.columns(2)
            df = pd.DataFrame(product_data)
            s1.dataframe(df)




            ####################################
            st.markdown("-----")

            key = "ARM"
            st.checkbox("Export - SecureEquity ARM", key = key)

            sec1,sec2, sec3, sec4 = st.columns(4)

            origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value=10, value=1, step=1, format="%d%%", key = f"{key}_origination")
            adj_avail_proceeds = avail_proceeds * (1-origination_fee/100)

            fixed_fee = sec2.number_input("Fixed Fee", value=0, step=1, key = f"{key}_fixed_fee")
            adj_avail_proceeds = adj_avail_proceeds - fixed_fee

            total_fee_charge = avail_proceeds - adj_avail_proceeds
            sec3.badge(f"Input Fee : {total_fee_charge:,.2f}")

            df = DB_ARM[DB_ARM["Offer"] == key]

            max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
            max_fee = max_fee[0] if max_fee else "-"

            sec3.badge(f"Max Fee : {max_fee}")

            try:
                fee_applied = min(max_fee, total_fee_charge)
            except:
                fee_applied = total_fee_charge 

            adj_avail_proceeds = avail_proceeds - fee_applied
            sec1.write(f"Applied Fee : {fee_applied:,.2f}")


            if PL_Utilised < 0.25:
                col = "0-25%"
            elif PL_Utilised <= 0.8:
                col = "25-80%"
            elif PL_Utilised <= 0.9:
                col = "80-90%"
            else:
                col = "90-100%"


            df = df[["Rate Type", "Margin%", col]]
            df["Margin%"] = df["Margin%"].astype(str) + "%"

            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            product_data = df.to_dict(orient="records")
            s1,s2 = st.columns(2)
            df = pd.DataFrame(product_data)
            s1.dataframe(df)




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



