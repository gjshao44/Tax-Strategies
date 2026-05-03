import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dynamic Retirement Roadmap", layout="wide")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("⏳ 1. Retirement Timeline")
    retire_year = st.number_input("Full Retirement Year", value=2026)
    h_age_at_retire = st.number_input(f"Husband Age in {retire_year}", value=64)
    w_age_at_retire = st.number_input(f"Wife Age in {retire_year}", value=69)
    filing_status = st.selectbox("Filing Status", ["Married Filing Jointly", "Single"])

    st.header("💰 Assets & Income")
    last_salary = st.number_input("Final Annual Salary", value=90000)
    ira_h_init = st.number_input("Husband IRA Balance ($)", value=1500000)
    ira_w_init = st.number_input("Wife IRA Balance ($)", value=10000)
    muni_int = st.number_input("Annual Muni Interest", value=37000)
    taxable_div = st.number_input("Annual Taxable Dividends", value=33000)
    
    st.header("📈 Social Security")
    ss_h_monthly = st.number_input("H Monthly SS ($)", value=4000)
    ss_h_start = st.number_input("H Start Year", value=2029)
    ss_w_monthly = st.number_input("W Monthly SS ($)", value=1200)
    ss_w_start = st.number_input("W Start Year", value=2027)

    st.header("🎚️ Strategy Levers")
    roth_conv = st.slider("Annual Roth Conversion ($)", 0, 100000, 40000, step=5000)
    annual_ltcg = st.slider("Annual Cap Gains ($)", 0, 100000, 20000, step=5000)

# --- CALCULATION ENGINE ---
def calculate_roadmap():
    rows = []
    # 2026 Base Parameters (IRS/Medicare)
    std_deduct_base = 32200
    sr_addon_base = 1650
    bonus_65_base = 6000
    irmaa_base_2026 = 218000
    
    cur_ira_h = ira_h_init
    cur_ira_w = ira_w_init

    for i in range(15):
        year = retire_year + i
        age_h = h_age_at_retire + i
        age_w = w_age_at_retire + i
        inf = (1.025 ** i)
        
        # 1. Logic-based Events
        ev = []
        if year == retire_year: ev.append("Retirement")
        if age_h == 65: ev.append("H-Medicare")
        if age_w == 73: ev.append("W-RMD Starts")
        if age_h == 75: ev.append("H-RMD Starts")
        if year == 2029: ev.append("OBBBA Bonus Sunsets")
        
        # 2. Separate RMD Calculations (SECURE 2.0 Logic)
        rmd_h = (cur_ira_h / 24.6) if age_h >= 75 else 0
        rmd_w = (cur_ira_w / 26.5) if age_w >= 73 else 0
        total_rmd = rmd_h + rmd_w
        
        # 3. Income Streams
        # Salary is only paid in the year of retirement (assuming 6 months/partial)
        salary = last_salary if year == retire_year else 0
        h_ss = (ss_h_monthly * 12 * inf) if year >= ss_h_start else 0
        w_ss_base = (ss_w_monthly * 12 * inf) if year >= ss_w_start else 0
        w_spousal = (h_ss * 0.5) if (year >= ss_w_start and year >= ss_h_start) else 0
        w_ss = max(w_ss_base, w_spousal)
        total_ss = h_ss + w_ss
        
        # 4. Tax Calculations
        provisional = (salary + taxable_div + annual_ltcg + roth_conv + total_rmd) + muni_int + (total_ss * 0.5)
        taxable_ss = total_ss * 0.85 if provisional > 44000 else (total_ss * 0.5 if provisional > 32000 else 0)
        
        agi = salary + taxable_div + annual_ltcg + roth_conv + taxable_ss + total_rmd
        magi = agi + muni_int
        
        # Deductions & Bonus Phase-out
        num_65 = (1 if age_h >= 65 else 0) + (1 if age_w >= 65 else 0)
        sen_bonus = (num_65 * bonus_65_base) if year <= 2028 else 0
        if magi > 150000 and sen_bonus > 0:
            sen_bonus = max(0, sen_bonus - (magi - 150000) * 0.06)
            
        deduct = (std_deduct_base * inf) + (num_65 * sr_addon_base * inf) + sen_bonus
        taxable_inc = max(0, agi - deduct)
        
        # Tax Estimate (Layered Bracket Approx)
        fed_tax = (max(0, taxable_inc - (98900 * inf)) * 0.15) + (min(taxable_inc, 98900 * inf) * 0.11)
        
        # 5. Asset Updates
        cur_ira_h = (cur_ira_h - rmd_h - (roth_conv * 0.95)) * 1.05
        cur_ira_w = (cur_ira_w - rmd_w - (roth_conv * 0.05)) * 1.05
        
        rows.append({
            "Year": year,
            "Ages(H/W)": f"{age_h}/{age_w}",
            "INPUT: SS": f"${total_ss:,.0f}",
            "LEVER: Roth": f"${roth_conv:,.0f}",
            "LEVER: Cap Gains": f"${annual_ltcg:,.0f}",
            "OUT: AGI": f"${agi:,.0f}",
            "OUT: MAGI(IRMAA)": f"${magi:,.0f}",
            "OUT: Fed Tax": f"${fed_tax:,.0f}",
            "IRMAA": "✅ Safe" if magi < (irmaa_base_2026 * inf) else "🚩 Above",
            "🚨 Important Events": ", ".join(ev)
        })
    return pd.DataFrame(rows)

# --- DISPLAY ---
st.subheader(f"Retirement Roadmap starting {retire_year}")
df = calculate_roadmap()
st.table(df)

# --- ADD THIS TO THE BOTTOM OF YOUR tax_app.py ---

st.markdown("---")
st.subheader("🏁 Strategic Execution Guide")

# Dynamic Commentary based on the DataFrame (df)
latest_magi = df.iloc[5]["OUT: MAGI(IRMAA)"].replace('$','').replace(',','')
if float(latest_magi) < 200000:
    st.success("✅ **Roth Capacity:** You have significant 'Tax Room.' Consider increasing Roth conversions in the early years to reduce the 2037 RMD spike.")
else:
    st.warning("⚠️ **IRMAA Danger:** You are approaching the Medicare surcharge cliff. Monitor your Capital Gains realized in years where SS and RMDs overlap.")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Watch the Bonus:**\nAfter 2028, the OBBBA senior bonus disappears. Your 'Taxable Income' will jump even if your actual income stays the same.")
with col2:
    st.info("**The RMD Cliff:**\nIn 2030 (Wife) and 2037 (Husband), your income becomes involuntary. Use the years 2027-2029 to lower your future RMD-heavy tax bill.")
with col3:
    st.info("**CG Harvest:**\nAim to realize Capital Gains while 'Taxable Income' is below $100k (indexed) to keep your Federal CG rate at 0%.")