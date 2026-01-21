import random, json, re
import streamlit as st
import pandas as pd
from datetime import date, datetime
import requests

from fpdf import FPDF


def create_pdf(applicant1, applicant2, loan_type, PLF, PL, avail_proceeds, increase, PLU, df_name, df, _date, home_value, outstanding_loan, line_of_credit, current_interest, notes, eligible, Property_Tax, Loan1RecDate):
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

        for each in ["First Name","Last Name", "D.O.B", "Address", "City", "State", "Zipcode", "Mobile", "Home Phone", "Email"]:

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
        "Property Tax" : Property_Tax,

        "Loan1Amount $" : line_of_credit,
        "Loan1RecDate" : Loan1RecDate,
        "Loan1Rate %" : current_interest,
        }

    pdf.set_font('Arial', "", 10)
    for each in ["Home Loan $", "Outstanding Loan $", "Property Tax", "Loan1Amount $", "Loan1RecDate", "Loan1Rate %", ]:
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
    master_moom_file = pd.read_excel(response.content,  sheet_name=None)

    return master_moom_file

    # dfs = pd.read_excel(response.content, sheet_name=None)   # returns a dict of DataFrames
    # # dfs = pd.read_excel("MOOM.xlsx",  sheet_name=None)

    # DB_fixed_rate  = dfs["SecureEquity"]
    # DB_ARM         = dfs["ARM"]
    # DB_HECM5       = dfs["HECM"]
    # DB_HECM_Fixed  = dfs["HECM_Fixed"]

    # ##############################
    # # pfl_chart = pd.read_excel("PFL.xlsx")
    # pfl_chart = dfs["PLF"]
    # hecm_plf = pfl_chart[["AGE", "HECM"]]
    # hecm_plf.columns = ["AGE", "PLF"]

    # jumbo_plf = pfl_chart[["AGE", "Jumbo"]]
    # jumbo_plf.columns = ["AGE", "PLF"]
    # ##############################

    # return DB_fixed_rate, DB_ARM, DB_HECM5, DB_HECM_Fixed, hecm_plf, jumbo_plf



# DB_fixed_rate, DB_ARM, DB_HECM5, DB_HECM_Fixed, hecm_plf, jumbo_plf = download_excel()

# master_moom_file = pd.read_excel("MOOM.xlsx",  sheet_name=None)
master_moom_file = download_excel()

config = master_moom_file["Config"]
plf_master = master_moom_file["PLF"]



###### CHECK QUERY PARAMS

def dob_from_age(age: int, as_of: date | None = None) -> date:
    if not age:
        return None

    as_of = as_of or date.today()

    try:
        return as_of.replace(year=as_of.year - age)
    except ValueError:
        # Handles Feb 29
        return as_of.replace(month=2, day=28, year=as_of.year - age)


params = st.query_params
def load_param_once(key, default=None, cast=None):
    if key not in st.session_state:
        val = params.get(key, default)
        if val in ("", None):
            st.session_state[key] = default
        else:
            try:
                st.session_state[key] = cast(val) if cast else val
            except:
                st.session_state[key] = default


load_param_once("APN")
load_param_once("Borrower1FName")
load_param_once("Borrower1LName")


if "AGE1" not in st.session_state:
    if "AGE1" in params:
        st.session_state["Toggle1"] = True
        st.session_state["AGE1"] = int(params.get("AGE1", 0))
        st.session_state["DOB1"] = dob_from_age(st.session_state["AGE1"])

if "DOB1" not in st.session_state:
    if "DOB1" in params:
        st.session_state["Toggle1"] = False
        load_param_once("DOB1", cast=lambda x: date.fromisoformat(x))

# load_param_once("AGE1", cast=int)
load_param_once("Address1")
load_param_once("City1")
load_param_once("State1")
load_param_once("Zipcode1")
load_param_once("Mobile1")
load_param_once("HomePhone1")
load_param_once("Email1")



load_param_once("Borrower2FName")
load_param_once("Borrower2LName")
if "AGE2" not in st.session_state:
    if "AGE2" in params:
        st.session_state["Toggle2"] = True
        st.session_state["AGE2"] = int(params.get("AGE2", 0))
        st.session_state["DOB2"] = dob_from_age(st.session_state["AGE2"])

if "DOB2" not in st.session_state:
    if "DOB2" in params:
        st.session_state["Toggle2"] = False
        load_param_once("DOB2", cast=lambda x: date.fromisoformat(x))

load_param_once("Address2")
load_param_once("City2")
load_param_once("State2")
load_param_once("Zipcode2")
load_param_once("Mobile2")
load_param_once("HomePhone2")
load_param_once("Email2")

load_param_once("home_value", cast=int)

load_param_once("zillow_estimate", cast=int)
load_param_once("redfinn_estimate", cast=int)

load_param_once("line_of_credit", cast=int)
load_param_once("property_tax", cast=int)
load_param_once("existing_loan", cast=int)

load_param_once(
    "existing_loan_date",
    cast=lambda x: date.fromisoformat(x),
    default = date(1900, 1, 1)
)

load_param_once("existing_loan_interest", cast=float)
load_param_once("new_interest", cast=float)

load_param_once("Loan1LenderName")
load_param_once("Loan1FinancingType")
load_param_once("ProductType_Flag")

load_param_once("NOTES")


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
        first_name = left.text_input(f"Borrower {i+1} First Name", key = f"Borrower{i+1}FName")
        last_name = right.text_input(f"Borrower {i+1} Last Name" , key = f"Borrower{i+1}LName")


        toggle = st.toggle("Select Age", key = f"Toggle{i+1}") 

        if not toggle:
            left, right = st.columns(2)

            dob = left.date_input(
                "D.O.B (YY-MM-DD)",
                min_value = min_date,
                max_value = today,
                value = date(1900, 1, 1),
                key = f"DOB{i+1}"
            )

            age = calculate_age(st.session_state[f"DOB{i+1}"], today)
            dob = dob.strftime("%m/%d/%Y")

            right.badge("")
            right.badge(f"{age[0]} Y {age[1]} M")

        else:
            left, right,c = st.columns(3)

            age_year  = left.number_input("Years"  ,min_value=0 ,max_value=120 ,step=1 ,format="%d", key = f"AGE{i+1}")
            age_month = right.number_input("Months",min_value=0 ,max_value=12 ,step=1 ,format="%d", key=f"AGE_MONTH{i+1}")
            dob = "-"
            age = [age_year, age_month]


        if age[1] >= 6 :
            age_used = age[0] + 1 
        else:
            age_used = age[0]



        address = st.text_input(f"Address", key = f"Address{i+1}")

        left, right = st.columns(2)
        city = left.text_input(f"City", key = f"City{i+1}")
        state = right.text_input(f"State", key = f"State{i+1}")
        zipcode = st.text_input(f"Zipcode", key = f"Zipcode{i+1}")

        mobile = st.text_input("Mobile Phone", placeholder="Enter 10-digit mobile number", key = f"Mobile{i+1}")
        home_phone = st.text_input("Home Phone" , placeholder="Enter home number", key = f"HomePhone{i+1}")
        email = st.text_input(f"Borrower {i+1} Email" , placeholder="Enter Email", key = f"Email{i+1}")


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
            "Home Phone" : home_phone,
            "Email" : email
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



left, right, corner = st.columns(3)

home_value         = left.number_input("Home Value ($)"        , min_value=0.0, format="%.2f", key = "home_value")
zillow_estimate    = right.number_input("Zillow Estimate ($)"  , min_value=0.0, format="%.2f", key = "zillow_estimate")
redfinn_estimate   = corner.number_input("Redfinn Estimate ($)", min_value=0.0, format="%.2f", key = "redfinn_estimate")


left, right, x = st.columns(3)
line_of_credit = left.number_input("Line of Credit ($)", min_value=0.0, format="%.2f", key = "line_of_credit")
Property_Tax   = right.number_input("Annual Property Tax Amount ($)", min_value=0.0, format="%.2f", key = "property_tax")

st.markdown("-----------")


left, right, more_right = st.columns(3)

existing_loan = left.number_input("Loan1Amount $", min_value=0.0, format="%.2f", key = "existing_loan")

Loan1RecDate = right.date_input(
    "Loan1RecDate",
    min_value = min_date,
    max_value = today,
    # value = date(1900, 1, 1),
    key = "existing_loan_date"
)

Loan1LenderName  = more_right.text_input(f"Loan1LenderName"    , key = "Loan1LenderName")


######################################################
left, right, more_right, extreme_right = st.columns(4)

current_interest = left.number_input("Loan1Rate" , min_value=0.0 , format="%.2f", key = "existing_loan_interest")
new_interest     = right.number_input("New Rate" , min_value=0.0 , format="%.2f", key = "new_interest")

Loan1FinancingType = more_right.text_input(f"Loan1FinancingType", key = "Loan1FinancingType")
ProductType_Flag   = extreme_right.text_input(f"ProductType_Flag", key = "ProductType_Flag")

try:
    loan_diff = st.session_state.new_interest - st.session_state.existing_loan_interest

    st.write(f"Yearly Savings  : {(existing_loan * loan_diff):,.2f}")
    st.write(f"Monthly Savings : {(existing_loan * loan_diff / 12):,.2f}")
except:
    pass

# left, right, more_right = st.columns(3)
# current_interest = more_right.number_input("Loan1Rate" , min_value=0.0 , format="%.2f", key = "existing_loan_interest")
######################################################



st.markdown("-----------")


config = (config.set_index("Name").to_dict(orient="index"))




###########################################################################
###########################################################################

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


def prepare_fee(df, key, orgin_fee_pre, fixed_fee_pre):

    sec1,sec2, sec3, sec4 = st.columns(4)

    origination_fee = sec1.slider("Select origination fee %", min_value=0, max_value = 10, value = orgin_fee_pre, step=1, format="%d%%", key = f"{key}_origination")
    fixed_fee       = sec2.number_input("Fixed Fee", value = fixed_fee_pre, step=1, key = f"{key}_fixed_fee")

    total_fee_charge = (existing_loan * origination_fee/100) + fixed_fee

    max_fee = (df["Max Fee"].dropna().drop_duplicates().tolist())
    max_fee = max_fee[0] if max_fee else "-"

    sec3.badge(f"Input : {total_fee_charge:,.2f}")
    sec3.badge(f"Max : {max_fee}")

    try: fee_applied = min(max_fee, total_fee_charge)
    except: fee_applied = total_fee_charge 

    sec1.write(f"Applied Fee : {fee_applied:,.2f}")

    adj_avail_proceeds = avail_proceeds - fee_applied

    return total_fee_charge, fee_applied, adj_avail_proceeds

###########################################################################
###########################################################################


a,b,c,d = st.columns(4)
selected_program = a.selectbox("Choose a Program", config.keys())


# plf_value = plf_master.loc[plf_master["AGE"] == borrower_age, selected_program].iloc[0]
rows = plf_master.loc[plf_master["AGE"] == borrower_age, selected_program]

if rows.empty:
    plf_value = None
else:
    plf_value = rows.iloc[0]


if plf_value:
    # tab_selected = config[selected_program]["Tab"]

    st.markdown("-----------")

    a,b,c,d = st.columns(4)

    principal_limit = home_value * plf_value

    total_proceeds = principal_limit - existing_loan + line_of_credit
    avail_proceeds = principal_limit - existing_loan


    try:
        PL_Utilised = (1 - float(avail_proceeds)/float(principal_limit))
    except:
        PL_Utilised = 0

    eligible = "✅ Yes" if principal_limit > existing_loan else "❌ No"


    a.metric("PLF %", f"{plf_value*100:.2f}%", width="content")
    b.metric("Principal Limit $", show_value(principal_limit), width="content")
    c.metric("Prev. Line of Credit $", show_value(line_of_credit), width="content")


    if "Adj. Proceeds" not in st.session_state:
        st.session_state["Adj. Proceeds"] = None

    try: delta = st.session_state["Adj. Proceeds"] - line_of_credit
    except: delta = None

    d.metric("Current Avail. Proceed $", show_value(avail_proceeds), delta = show_value(delta), width="content")

    a,b,c,d = st.columns(4)
    a.metric("PL_Utilised %", show_value(PL_Utilised, "%"), width="content")
    b.metric("Eligibility"  , show_value(eligible)        , width="content")

    st.write("")

    config_selected_program = config[selected_program]

    df_selected = master_moom_file[config_selected_program["Tab"]]
    df_selected = df_selected[df_selected["Offer"] == config_selected_program["Offertype"]]


    orgin_fee_pre = config_selected_program["Origination Fee%"]
    fixed_fee_pre = config_selected_program["Fixed Fee"]


    # ### PREPARING FEE
    total_fee_charge, fee_applied, adj_avail_proceeds = prepare_fee(df_selected, "11", orgin_fee_pre, fixed_fee_pre)
    st.session_state["Adj. Proceeds"] = adj_avail_proceeds



    cols_to_drop = ["Offer", "Min_PL", "Min Fee", "Max Fee"]
    for each in cols_to_drop:
        try:
            df_selected = df_selected.drop(columns = [each])
        except:
            pass


    def showcase_db(df):
        product_data = df.to_dict(orient="records")
        s1,s2 = st.columns(2)
        df = pd.DataFrame(product_data)
        s1.dataframe(df)

        return df


    def get_range_columns(df):
        """Return all columns that match format like 0-10%, 10-20, 20-50% etc."""
        range_cols = []
        pattern = re.compile(r"(\d+)-(\d+)%?$")   # supports both 10-20 and 10-20%
        
        for col in df.columns:
            if pattern.match(col):
                range_cols.append(col)
        return range_cols


    def get_matching_range_column(range_cols, plf_value):
        """Return the column name whose numeric range contains plf_value."""
        for col in range_cols:
            start, end = map(int, re.findall(r"(\d+)-(\d+)", col)[0])
            if start <= plf_value < end:
                return col
        return None


    def filter_df_on_plf(df, plf_value):
        """
        Returns:
            - matching column
            - list of all range columns
            - df with only the matching column kept
        """
        range_cols = get_range_columns(df)
        match_col = get_matching_range_column(range_cols, plf_value)

        if match_col is None:
            raise ValueError(f"No matching PLF range for value {plf_value}")

        # Keep only the matching range column
        filtered_df = df.drop(columns=[c for c in range_cols if c != match_col])

        return match_col, range_cols, filtered_df



    df = df_selected
    match, ranges, new_df = filter_df_on_plf(df, plf_value = plf_value*100)

    # df["Margin%"] = df["Margin%"].astype(str) + "%"
    new_df["Avail. Proceeds"] = f"{adj_avail_proceeds:,.0f}"

    ### SHOWCASING DB
    df = showcase_db(new_df)



    st.header("Export PDF")
    notes = st.text_area("Notes to include in PDF", key = "NOTES")

    left, right,a,b = st.columns(4)
    generate = left.button("Export PDF", key='generate_jumbo')

    if generate:

        pdf = create_pdf(borrowers[0], borrowers[1], selected_program, f"{plf_value*100:.2f}%", show_value(principal_limit, "$"), show_value(avail_proceeds, "$"), 
                         show_value(delta, "$"), show_value(PL_Utilised, "%"), selected_program, df, today.strftime("%m/%d/%Y"), 
                         show_value(home_value,"$"), show_value(existing_loan,"$"), show_value(line_of_credit,"$"), show_value(current_interest/100, "%"),
                         notes, eligible, Property_Tax, Loan1RecDate
            )

        def invoice_downloaded():
            return
            if not st.session_state.disabled:
                st.success("Invoice Downloaded")    

        filename = f'{youngest_borrower["Last Name"]}-{youngest_borrower["First Name"]}-{selected_program}.pdf'

        download_Invoice = right.download_button(label="Download PDF", data = pdf, file_name= filename, mime='application/octet-stream', disabled = False, on_click = invoice_downloaded)

else:
    st.write("AGE is Out of Bounds")


# st.write(df_selected)



