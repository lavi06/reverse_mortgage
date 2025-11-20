import random, json
import streamlit as st
import pandas as pd
from datetime import date, datetime
import requests

from fpdf import FPDF


def create_pdf(applicant1, applicant2, loan_type, PLF, PL, avail_proceeds, increase, PLU, df_name, df, _date, home_value, outstanding_loan, line_of_credit, current_interest, notes, eligible):
    border = 0

    pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')

    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_margins(20,20)


    pdf.rect(x = 15, y = 25 , w = 180, h= 115, style = "")

    pdf.cell(170, 15, ln = 1, border = border)

    pdf.cell(170, 5, txt = f"Loan Offer : Generated on {_date}", ln = 1, border = border, align="L")

    pdf.cell(170, 5, ln = 1, border = border, align="L")

    for i in range(1,3):
        pdf.set_font('Arial', "", 12)
        pdf.cell(170, 5, ln = 1, border = border, align="L")
        pdf.cell(170, 5, txt = f"Applicant {i} :", ln = 1, border = border, align="L")
        pdf.cell(15, 2, ln = 1, border = border, align="L")
         
        pdf.set_font('Arial', "", 10)

        for each in ["First Name","Last Name", "D.O.B", "Address", "City", "State", "Zipcode", "Mobile", "Home Phone"]:

            pdf.cell(15, 5, ln = 0, border = border, align="L")
            pdf.cell(30, 5, txt = each ,ln = 0, border = border, align="L")

            if each == "D.O.B":
                ln = 0
            else:
                ln = 1
            if i == 1:
                pdf.cell(30, 5, txt = str(applicant1[each]) ,ln = ln, border = border, align="L")
                if each == "D.O.B":
                    pdf.cell(30, 5, txt = "Age" ,ln = 0, border = border, align="L")
                    pdf.cell(30, 5, txt = f"{applicant1['years']} Y | {applicant1['months']} M" ,ln = 1, border = border, align="L")

            else:
                pdf.cell(30, 5, txt = str(applicant2[each]) ,ln = ln, border = border, align="L")

                if each == "D.O.B":
                    pdf.cell(30, 5, txt = "Age" ,ln = 0, border = border, align="L")
                    pdf.cell(30, 5, txt = f"{applicant2['years']} Y | {applicant2['months']} M" ,ln = 1, border = border, align="L")



    # pdf.cell(40, 5, txt = "_____________________________________________________________________________________", ln = 1, border = border)

    pdf.set_font('Arial', "", 12)
    pdf.cell(170, 5, ln = 1, border = border, align="L")
    pdf.cell(170, 5, ln = 1, border = border, align="L")
    pdf.cell(170, 5, txt = "Property Details :", ln = 1, border = border, align="L")
    pdf.cell(15, 2, ln = 1, border = border, align="L")

    vals = {
        "Home Loan $" : home_value,
        "Outstanding Loan $" : outstanding_loan,
        "Line of Credit $" : line_of_credit,
        "Current Interest %" : current_interest
        }

    pdf.set_font('Arial', "", 10)
    for each in ["Home Loan $", "Outstanding Loan $", "Line of Credit $", "Current Interest %"]:
        pdf.cell(15, 5, ln = 0, border = border, align="L")
        pdf.cell(50, 5, txt = each ,ln = 0, border = 1, align="L")
        pdf.cell(50, 5, txt = str(vals[each]) ,ln = 1, border = 1, align="L")


    pdf.set_font('Arial', "", 12)
    pdf.cell(170, 5, ln = 1, border = border, align="L")
    pdf.cell(170, 5, txt = "Result Snapshot :", ln = 1, border = border, align="L")
    pdf.cell(15, 2, ln = 1, border = border, align="L")

    vals = {
        "PLF %" : PLF,
        "Principal Limit $" : PL,
        "Avail. Proceeds" : avail_proceeds,
        "Increase from Previous Avail. Proceeds" : increase,
        "PL Utilised %" : PLU
        }

    pdf.set_font('Arial', "", 10)
    for each in ["PLF %", "Principal Limit $", "Avail. Proceeds", "Increase from Previous Avail. Proceeds", "PL Utilised %"]:
        pdf.cell(15, 5, ln = 0, border = border, align="L")
        pdf.cell(70, 5, txt = each ,ln = 0, border = 1, align="L")
        pdf.cell(70, 5, txt = vals[each] ,ln = 1, border = 1, align="L")


    pdf.cell(40, 5, txt = "_____________________________________________________________________________________", ln = 1, border = border)

    pdf.set_font('Arial', "B", 12)

    if "no" in eligible.lower():
        txt = f"Sorry! Applicant is Not Eligible for a {loan_type} Loan."
    else:             
        txt = f"Congrats! Applicant is Eligible for a {loan_type} Loan of {PL}."
    pdf.cell(170, 5, ln = 1, border = border, align="L")
    pdf.cell(170, 5, txt = txt, ln = 1, border = border, align="L")


    if df_name:
        txt = "Please find below the recommended Offer based on Current Market Values."
        pdf.cell(170, 5, ln = 1, border = border, align="L")
        pdf.cell(170, 5, txt = txt, ln = 1, border = border, align="L")
        pdf.cell(15, 5, ln = 1, border = border, align="L")


    if df_name or len(notes) > 0:
        pdf.add_page()
        pdf.set_xy(0, 0)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_margins(20,20)


    if df_name:
        ####### ADDING DF

        pdf.cell(170, 25, ln = 1, border = border)
        pdf.cell(170, 5, txt = df_name, ln = 1, border = border, align="L")
        pdf.cell(170, 5, ln = 1, border = border, align="L")

        line_height = pdf.font_size * 1
        page_width = pdf.w - 2 * pdf.l_margin  # printable width
        col_width = page_width / max(1, len(df.columns))


        pdf.cell(col_width, line_height, ln = 1, border = border)

        pdf.set_font("Arial", "B", 8)
        for col in df.columns:
            pdf.cell(col_width, line_height, str(col), border=1, align = "C")

        pdf.ln(line_height)

        pdf.set_font("Arial", size=8)
        avg_char_w = pdf.get_string_width("a") or 1
        max_chars = max(1, int((col_width - 2) / avg_char_w))

        for _, row in df.iterrows():
            for item in row:
                s = str(item)
                if len(s) > max_chars:
                    s = s[:max(0, max_chars - 3)] + "..."
                pdf.cell(col_width, line_height, s, border=1, align = "C")
            pdf.ln(line_height)


    if len(notes) > 0 :

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(170, 25, ln = 1, border = border)
        pdf.cell(170, 10, txt = "NOTES", ln = 1, border = border)

        pdf.set_font("Arial", "B", 8)
        pdf.multi_cell(170, 25, txt = notes, border = 1)


    pdf.output('HomeLoanOffer.pdf', 'F')

    with open('HomeLoanOffer.pdf', "rb") as pdf_file:
        encoded_string = pdf_file.read()

    return encoded_string



st.set_page_config(page_title="Reverse Mortgage Calculator", layout="wide")
# st.title("🏠 Reverse Mortgage Calculator")



def download_excel():

    url = "https://github.com/lavi06/reverse_mortgage/raw/refs/heads/main/MOOM.xlsx"

    response = requests.get(url)
    response.raise_for_status()
    dfs = pd.read_excel(response.content, sheet_name=None)   # returns a dict of DataFrames
    # dfs = pd.read_excel("MOOM.xlsx",  sheet_name=None)

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


def get_cmt():

    url = "https://api.stlouisfed.org/fred/series/observations?series_id=DGS1&api_key=ec4dad690a78e68befef631d6169ecc7&file_type=json"
    try:
        res = requests.get(url)

        res = res.json()

        return float(res["observations"][-1]["value"])
    except:
        return None 


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
                "D.O.B (YY-MM-DD)",
                min_value = min_date,
                max_value = today,
                value = date(1900, 1, 1),
                key = f"dob - {i}"
            )

            age = calculate_age(dob, today)
            dob = dob.strftime("%m/%d/%Y")

            right.badge("")
            right.badge(f"{age[0]} Y {age[1]} M")

        else:
            left, right,c = st.columns(3)

            age_year  = left.number_input("Years"  ,min_value=0 ,max_value=120 ,step=1 ,format="%d")
            age_month = right.number_input("Months",min_value=0 ,max_value=12 ,step=1 ,format="%d")
            # dob = f"{age_month}/01/{age_year}"
            dob = "-"
            age = [age_year, age_month]


        if age[1] >= 6 :
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
            "First Name" : first_name,
            "Last Name"  : last_name,
            "D.O.B"    : dob,
            "years"    : age[0],
            "months"   : age[1],
            "age_used" : age_used,
            "Address"  : address,
            "City"     : city,
            "State"    : state,
            "Zipcode"  : zipcode,
            "Mobile"   : mobile,
            "Home Phone" : home_phone
            })



# # --- Calculate youngest borrower's age ---
if borrowers:
    youngest_borrower = min(borrowers, key=lambda x: x["age_used"])

    st.sidebar.write(f"**Youngest Borrower Age:** {youngest_borrower['age_used']}")
    st.sidebar.write(f"**Name :** {youngest_borrower['First Name']} {youngest_borrower['Last Name']}")
    st.sidebar.write(f"**D.O.B:** {youngest_borrower['D.O.B']}")
    st.sidebar.markdown("------")

    borrower_age = youngest_borrower["age_used"]



# # --- Home details ---
# st.header("🏡 Property Details")

left, right = st.columns(2)
home_value    = left.number_input("Home Value ($)", min_value=0.0, format="%.2f")

existing_loan = right.number_input("Outstanding Loan ($)", min_value=0.0, format="%.2f")

left, right = st.columns(2)
line_of_credit = left.number_input("Line of Credit ($)", min_value=0.0, format="%.2f")
current_interest = right.number_input("Current interest Rate $", min_value=0.0 , format="%.2f")



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

    if label == "HECM":
        if home_value > 1209750:
            principal_limit = 1209750 * plf_val
        else:
            principal_limit = home_value * plf_val
    else:
        principal_limit = home_value * plf_val

    total_proceeds = principal_limit - existing_loan + line_of_credit
    avail_proceeds = principal_limit - existing_loan


    eligible = "✅ Yes" if principal_limit > existing_loan else "❌ No"

    results.append({
        "Type": label,
        "PLF": plf_val,
        "Principal Limit ($)"   : principal_limit,
        "Total Avail Proceeds"  : total_proceeds,
        "Available Proceeds ($)": avail_proceeds,
        "Eligible": eligible
    })



if "HECM_Notes" not in st.session_state:
    st.session_state["HECM_Notes"] = ""    
if "JUMBO_Notes" not in st.session_state:
    st.session_state["JUMBO_Notes"] = ""    


HECM_tab, Jumbo_tab, config_tab = st.tabs(["HECM", "JUMBO", "Config"])

if home_value > 0:

    def prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre):

        sec1,sec2, sec3, sec4 = st.columns(4)

        origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value = 10, value = orgin_fee_pre, step=1, format="%d%%", key = f"{key}_origination")
        fixed_fee       = sec2.number_input("Fixed Fee", value = fixed_fee_pre, step=1, key = f"{key}_fixed_fee")

        total_fee_charge = (avail_proceeds*origination_fee/100) + fixed_fee

        max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
        max_fee = max_fee[0] if max_fee else "-"

        sec3.badge(f"Input : {total_fee_charge:,.2f}")
        sec3.badge(f"Max : {max_fee}")

        try: fee_applied = min(max_fee, total_fee_charge)
        except: fee_applied = total_fee_charge 

        sec1.write(f"Applied Fee : {fee_applied:,.2f}")

        adj_avail_proceeds = avail_proceeds - fee_applied

        return total_fee_charge, fee_applied, adj_avail_proceeds

    def showcase_db(df):
        product_data = df.to_dict(orient="records")
        s1,s2 = st.columns(2)
        df = pd.DataFrame(product_data)
        s1.dataframe(df)

        return df

    def show_value(value,sign = None):
        try:
            if sign == "%":
                return f"{value*100:.2f}%"
            elif sign == "$":
                return f"{value:,.0f} $"
            else:
                return f"{value:,.0f}"
        except:
            return value


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


        a.metric("PLF %", f"{result['PLF']*100:.4f}%", width="content")
        b.metric("Principal Limit $", show_value(principal_limit), width="content")
        c.metric("Prev. Line of Credit $", show_value(line_of_credit), width="content")

        try: delta = avail_proceeds - line_of_credit
        except: delta = None
        d.metric("Current Avail. Proceed $", show_value(avail_proceeds), delta = show_value(delta), width="content")
        
        a,b,c,d = st.columns(4)
        a.metric( "PL_Utilised %", show_value(PL_Utilised, "%"), width="content")
        b.metric("Eligibility",show_value(result["Eligible"]), width="content")



        if result["Eligible"] == "✅ Yes":
            ####################################
            st.markdown("-----------")

            key = "HECM5"
            # st.checkbox("Export - HECM Monthly Adj. 1Y CMT 5 CAP", key = key)
            st.write("HECM Monthly Adj. 1Y CMT 5 CAP")

            orgin_fee_pre = 0
            fixed_fee_pre = 5000

            df = DB_HECM5[DB_HECM5["Offer"] == key]

            # ### PREPARING FEE
            total_fee_charge, fee_applied, adj_avail_proceeds = prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre)

            ### PREPARING DB
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

            df = df[["Rate","Margin%", col]]
            df["Margin%"] = df["Margin%"].astype(str) + "%"
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            ### SHOWCASING DB
            df = showcase_db(df)
            df_hecm5 = df


            ####################################
            ####################################

            st.markdown("-----------")

            key = "HECM_Fixed"
            # st.checkbox("Export - HECM Fixed", key = key)
            st.write("HECM Fixed")

            orgin_fee_pre = 0
            fixed_fee_pre = 10000

            df = DB_HECM_Fixed[DB_HECM_Fixed["Offer"] == key]

            # ### PREPARING FEE
            total_fee_charge, fee_applied, adj_avail_proceeds = prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre)

            df = df[["Extra Fee", "Rate", "Premium"]]
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            ### SHOWCASING DB
            df = showcase_db(df)
            df_hecm_fixed = df



        st.header("Export PDF")
        notes = st.text_area("Notes to include in PDF", value = st.session_state["HECM_Notes"], key = "Notes-HECM")
        st.session_state["HECM_Notes"] = notes


        if result["Eligible"] == "✅ Yes":

            choice = st.radio(
                "Select Offer to Escape:",
                ["HECM Monthly Adj. 1Y CMT 5 CAP", "HECM Fixed"]
            )
        else:
            choice = None


        left, right,a,b = st.columns(4)
        generate = left.button("Export PDF", key='generate_hecm')

        if generate:
            if choice == "HECM Monthly Adj. 1Y CMT 5 CAP":
                df = df_hecm5
                dfname = choice.replace("_"," ")
            elif choice == "HECM Fixed":
                df = df_hecm_fixed
                dfname = choice.replace("_"," ")
            else:
                df = None
                dfname = None


            pdf = create_pdf(borrowers[0], borrowers[1], "HECM", show_value(result['PLF'], "%"), show_value(principal_limit, "$"), show_value(avail_proceeds, "$"), 
                             show_value(delta, "$"), show_value(PL_Utilised, "%"), dfname, df, today.strftime("%m/%d/%Y"), 
                             show_value(home_value,"$"), show_value(existing_loan,"$"), show_value(line_of_credit,"$"), show_value(current_interest/100, "%"),
                             st.session_state["Notes-HECM"], result["Eligible"]

                )

            def invoice_downloaded():
                return

            # filename = f'HECM-{dfname}.pdf'
            filename = f'{youngest_borrower["Last Name"]}-{youngest_borrower["First Name"]}-{choice}.pdf'

            download_Invoice = right.download_button(label="Download PDF", data = pdf, file_name= filename, mime='application/octet-stream', disabled = False, on_click = invoice_downloaded)


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


        a.metric("PLF %", show_value(result['PLF'], "%"), width="content")
        b.metric("Principal Limit $", show_value(principal_limit), width="content")
        c.metric("Prev. Line of Credit $", show_value(line_of_credit), width="content")

        try: delta = avail_proceeds - line_of_credit
        except: delta = None
        d.metric("Current Avail. Proceed $", show_value(avail_proceeds), delta = show_value(delta), width="content")
        
        a,b,c,d = st.columns(4)
        a.metric( "PL_Utilised %", show_value(PL_Utilised, "%"), width="content")
        b.metric("Eligibility",show_value(result["Eligible"]), width="content")


        ####################################
        if result["Eligible"] == "✅ Yes":

            st.markdown("-----")

            key = "SecureEquity_Fixed_Plus"
            # st.checkbox("Export - SecureEquity Fixed Plus", key = key)
            st.write("SecureEquity Fixed Plus")

            orgin_fee_pre = 4
            fixed_fee_pre = 0

            df = DB_fixed_rate[DB_fixed_rate["Offer"] == key]

            # ### PREPARING FEE
            total_fee_charge, fee_applied, adj_avail_proceeds = prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre)

            ### PREPARING DB
            df = df[["Rate Type", "Rate", "Premium"]]
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            ### SHOWCASING DB
            df = showcase_db(df)
            df_SecureEquity_Fixed = df


            ####################################
            st.markdown("-----")

            key = "SecureEquity_Fixed"
            st.write("SecureEquity Fixed")
            # st.checkbox("Export - SecureEquity Fixed", key = key)

            orgin_fee_pre = 1
            fixed_fee_pre = 0

            df = DB_fixed_rate[DB_fixed_rate["Offer"] == key]

            # ### PREPARING FEE
            total_fee_charge, fee_applied, adj_avail_proceeds = prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre)

            ### PREPARING DB
            df = df[["Rate Type", "Rate", "Premium"]]

            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            ### SHOWCASING DB
            df = showcase_db(df)
            df_SecureEquity_Fixed_Plus = df


            ####################################
            st.markdown("-----")

            key = "ARM"
            st.write("SecureEquity ARM")
            # st.checkbox("Export - SecureEquity ARM", key = key)

            orgin_fee_pre = 1
            fixed_fee_pre = 0

            df = DB_ARM[DB_ARM["Offer"] == key]

            # ### PREPARING FEE
            total_fee_charge, fee_applied, adj_avail_proceeds = prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre)


            sec1,sec2, sec3, sec4 = st.columns(4)
            cc = get_cmt()
            if cc:
                cmt_ = sec1.number_input("CMT Value %", value = cc, min_value=0.0, format="%.2f", key = "cmt_value")
            else:
                cmt_ = sec1.number_input("CMT Value %", min_value=0.0, format="%.2f", key = "cmt_value")


            ### PREPARING DB

            if PL_Utilised < 0.25:
                col = "0-25%"
            elif PL_Utilised <= 0.8:
                col = "25-80%"
            elif PL_Utilised <= 0.9:
                col = "80-90%"
            else:
                col = "90-100%"

            df = df[["Rate Type", "Margin%", col]]
            df["Rate"] = cmt_ + df["Margin%"].astype(float)
            df["Rate"] = df["Rate"].astype(str) + "%"

            df["Margin%"] = df["Margin%"].astype(str) + "%"
            df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

            df = df[["Rate Type","Rate", "Margin%", col]]

            ### SHOWCASING DB
            df = showcase_db(df)
            df_ARM = df


            ####################################


        st.header("Export PDF")
        notes = st.text_area("Notes to include in PDF", value = st.session_state["JUMBO_Notes"], key = "Notes-JUMBO")
        st.session_state["JUMBO_Notes"] = notes

        if result["Eligible"] == "✅ Yes":

            choice = st.radio(
                "Select Offer to Escape:",
                ["SecureEquity_Fixed_Plus", "SecureEquity_Fixed", "SecureEquity_ARM"]
            )
        else:
            choice = None

        left, right,a,b = st.columns(4)
        generate = left.button("Export PDF", key='generate_jumbo')

        if generate:
            if choice == "SecureEquity_Fixed_Plus":
                df = df_SecureEquity_Fixed_Plus
                dfname = choice.replace("_"," ")
            elif choice == "SecureEquity_Fixed":
                df = df_SecureEquity_Fixed
                dfname = choice.replace("_"," ")
            elif choice == "SecureEquity_ARM":
                df = df_ARM
                dfname = choice.replace("_"," ")
            else:
                df = None
                dfname = None


            pdf = create_pdf(borrowers[0], borrowers[1], "JUMBO", show_value(result['PLF'], "%"), show_value(principal_limit, "$"), show_value(avail_proceeds, "$"), 
                             show_value(delta, "$"), show_value(PL_Utilised, "%"), dfname, df, today.strftime("%m/%d/%Y"), 
                             show_value(home_value,"$"), show_value(existing_loan,"$"), show_value(line_of_credit,"$"), show_value(current_interest/100, "%"),
                             st.session_state["Notes-JUMBO"], result["Eligible"]

                )

            def invoice_downloaded():
                return
                if not st.session_state.disabled:
                    st.success("Invoice Downloaded")    

            filename = f'{youngest_borrower["Last Name"]}-{youngest_borrower["First Name"]}-{choice}.pdf'

            download_Invoice = right.download_button(label="Download PDF", data = pdf, file_name= filename, mime='application/octet-stream', disabled = False, on_click = invoice_downloaded)


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



