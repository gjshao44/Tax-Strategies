import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comprehensive Retirement Wealth & Tax Optimizer", layout="wide")

# --- 1. LANGUAGE DICTIONARY ---
LANG_MAP = {
    "English": {
        "title": "🛡️ Comprehensive Retirement Wealth & Tax Optimizer",
        "motivation_h": "✍️ Motivation",
        "motivation_body": "This tool provides prospective retirees or current retirees with a tax strategy simulation and individualizes the various levers to convert to Roth; to realize capital gains; to test different growth scenarios. The goal is to minimize the next 15 year total federal tax paid, therefore achive optimum total wealth.",
        "meth_h": "🔬 Methodology",
        "meth_body": """
* **Asset Progression:** Tracks growth rates across three buckets (IRA, Roth, Brokerage).
* **Tax Attribution:** Distributes the annual Federal Tax burden proportionally across taxable yield sources.
* **IRMAA Monitoring:** Includes Municipal Interest in the MAGI calculation to track Medicare surcharge thresholds.
* **Waterfall Withdrawal Strategy:** a systematic approach to spending down retirement assets that prioritizes tax efficiency and capital preservation, in the order of taxable accounts, IRA accounts and Roth IRA accounts.
""",
        "use_h": "🕹️ How to Use",
        "use_body": """
* **Adjust Strategic Levers:** Use the sidebar to simulate different Roth conversion levels and Capital Gain harvesting.
* **Test Diffrent Growth and Expense Scenarios:** Use the sidebar to test different growth assumptions, inflation rate and annual living expenses.
* **Observe Total NW:** Watch the final column of the roadmap to see how paying taxes early (in Roth conversion, tax free bond, harvesting capital gains) preserves long-term capital.
""",
        "kpi_h": "🚀 15-Year Strategic Outlook",
        "kpi_init_nw": "Initial Net Worth",
        "kpi_nw": "Estimated Final NW (Year 15)",
        "kpi_tax": "Total Federal Tax Paid",
        "kpi_roth": "Total Roth Reservoir",
        "kpi_total_outflow": "Total 15-Yr Outflow",
        "kpi_cap_outflow": "Total living expenses plus all federal taxes paid.",        
        "kpi_cap_init": "Your starting capital across all accounts.",
        "kpi_cap_nw": "Total capital remaining across all accounts.",
        "kpi_cap_tax": "Cumulative tax burden over the 15-year period.",
        "kpi_cap_roth": "Final tax-free balance available for heirs or late-life needs.",
        "roadmap_h": "Retirement Roadmap starting",
        "summary_h": "📊 Strategic Account Summary (15-Year Cumulative)",
        "sidebar_timeline": "⏳ 1. Retirement Timeline",
        "sidebar_assets": "💰 Initial Assets",
        "sidebar_growth": "📈 Growth",
        "sidebar_cash": "💵 Cash Flow, Yield & Expenses",
        "sidebar_ss": "📈 Social Security",
        "sidebar_levers": "🎚️ Strategy Levers",
        "col_ltcg": "INPUT: LTCG",
        "col_muni": "INPUT: Tax-Free Int",
        "col_tax_div": "INPUT: Taxable Div",
        "col_ss": "INPUT: SS",
        "col_roth": "LEVER: Roth",
        "col_magi": "OUT: MAGI",
        "col_tax": "OUT: Fed Tax",
        "col_nw": "Total Net Worth",
        "col_events": "🚨 Important Events",
        "col_outflow": "OUT: Total Outflow",
        "event_oom": "⚠️ OUT OF MONEY",        
        "event_retire": "Retirement",
        "event_roth_stop": "🛑 Roth Stop",
        "event_hmed": "H-Medicare",
        "event_wmed": "W-Medicare",
        "event_hrmd": "H-RMD Start",
        "event_wrmd": "W-RMD Start",
        "acc_ira": "Tax-Deferred (IRA)",
        "acc_roth": "Tax-Free (Roth)",
        "acc_broker": "Taxable (Brokerage/Muni)",
        "sum_init": "Initial Balance",
        "sum_final": "Final Asset Balance",
        "sum_yield": "Total 15-Yr Yield/Income",
        "sum_liability": "Total 15-Yr Tax Liability",
        "sum_outflow": "Total 15-Yr Outflow",
        "total_label": "**TOTAL**"
    },
    "Chinese": {
        "title": "🛡️ 综合退休财富与税务优化工具",
        "motivation_h": "✍️ 建立初衷",
        "motivation_body": "本工具为准退休人员或已退休人员提供税务策略模拟。通过量化 Roth 转换、资本利得变现及不同增长场景等杠杆，目标是最小化未来 15 年的联邦税总支出，从而实现总财富的最优配置。",
        "meth_h": "🔬 模拟方法论",
        "meth_body": """
* **资产演进:** 追踪三大类账户的增长（IRA, Roth, 经纪账户）。
* **税务归属:** 将年度联邦税负担按比例分配到各个应税收益来源中。
* **IRMAA 监测:** 将市政债券利息纳入 MAGI 计算，以追踪医保附加费 (Medicare surcharge) 的阈值。
* **瀑布式提款策略:** 一种系统化的提款方式，优先考虑税务效率和资本保全，提款顺序依次为：应税账户、IRA 账户、最后是 Roth IRA 账户。
""",
        "use_h": "🕹️ 使用说明",
        "use_body": """
* **调整策略杠杆:** 使用侧边栏模拟不同的 Roth 转换水平和资本利得获取。
* **测试增长与支出场景:** 测试不同的增长假设、通货膨胀率和年度生活支出。
* **观察总净资产 (Total NW):** 关注路线图的最后一列，观察通过早期纳税（如 Roth 转换、税收减免债券、资本利得变现）如何保护长期资本。
""",
        "kpi_h": "🚀 15年战略展望",
        "kpi_init_nw": "初始净资产",
        "kpi_nw": "预计最终净资产 (第15年)",
        "kpi_tax": "联邦税总支出",
        "kpi_roth": "Roth 账户储备",
        "kpi_total_outflow": "15年总支出",
        "kpi_cap_outflow": "总生活支出与联邦税收之和",        
        "kpi_cap_init": "您的账户初始总资本",        
        "kpi_cap_nw": "所有账户中的剩余总资本",
        "kpi_cap_tax": "15年期间累计的税务负担",
        "kpi_cap_roth": "可供继承或后期使用的最终免税余额",
        "roadmap_h": "退休财务路线图 - 始于",
        "summary_h": "📊 战略账户总结 (15年累计)",
        "sidebar_timeline": "⏳ 1. 退休时间轴",
        "sidebar_assets": "💰 初始资产",
        "sidebar_growth": "📈 增长",
        "sidebar_cash": "💵 现金流,收益与支出",
        "sidebar_ss": "📈 社会安全金",
        "sidebar_levers": "🎚️ 策略杠杆",
        "col_ltcg": "长期资本利得",
        "col_muni": "免税利息 (Muni)",
        "col_tax_div": "应税股息",
        "col_ss": "社保收入",
        "col_roth": "Roth转换",
        "col_magi": "MAGI(医保判定)",
        "col_tax": "联邦税支出",
        "col_nw": "总净资产",
        "col_events": "🚨 重要事件",
        "col_outflow": "总支出 (含税)",
        "event_oom": "⚠️ 资金耗尽",        
        "event_roth_stop": "🛑 Roth 转换停止",
        "event_retire": "退休",
        "event_hmed": "丈夫医保",
        "event_wmed": "妻子医保",
        "event_hrmd": "丈夫RMD开始",
        "event_wrmd": "妻子RMD开始",
        "acc_ira": "税收递延 (IRA)",
        "acc_roth": "免税 (Roth)",
        "acc_broker": "应税 (经纪账户/市政债)",
        "sum_init": "初始余额",
        "sum_final": "期末资产余额",
        "sum_yield": "15年总收益/收入",
        "sum_liability": "15年总税务责任",
        "sum_outflow": "15年总支出",        
        "total_label": "**总计**"
    }
}

# --- 2. SIDEBAR: INPUTS & LANGUAGE ---
with st.sidebar:
    lang = st.radio("Language / 语言选择", ["English", "Chinese"], horizontal=True)
    t = LANG_MAP[lang]
    
    st.header(t["sidebar_timeline"])
    retire_year = st.number_input("Full Retirement Year", value=2026)
    h_age_at_retire = st.number_input(f"Husband Age in {retire_year}", value=64)
    w_age_at_retire = st.number_input(f"Wife Age in {retire_year}", value=64)

    st.header(t["sidebar_assets"])
    ira_h_init = st.number_input("Husband IRA Balance ($)", value=1500000)
    ira_w_init = st.number_input("Wife IRA Balance ($)", value=10000)
    roth_init = st.number_input("Roth IRA Balance ($)", value=100000)
    brokerage_init = st.number_input("Taxable Brokerage Balance ($)", value=1000000)

    st.header(t["sidebar_ss"])
    ss_h_monthly = st.number_input("H Monthly SS ($)", value=4000)
    ss_h_start = st.number_input("H Start Year", value=2029)
    ss_w_monthly = st.number_input("W Monthly SS ($)", value=3000)
    ss_w_start = st.number_input("W Start Year", value=2029)

    st.header(t["sidebar_levers"])
    roth_conv = st.slider("Annual Roth Conversion ($)", 0, 100000, 40000, step=5000)
    annual_ltcg = st.slider("Annual Cap Gains Realized ($)", 0, 100000, 20000, step=5000)

    st.header(t["sidebar_cash"])
    annual_expense = st.number_input("Annual Living Expense (Today's $)", value=100000)
    muni_int = st.number_input("Annual Tax-Free Muni Interest", value=37000)
    taxable_div = st.number_input("Annual Taxable Dividends", value=33000)
    last_salary = st.number_input("Final Salary (Retirement Year)", value=90000)
    
    st.header(t["sidebar_growth"])
    ira_growth = st.slider("IRA Growth Rate (%)", 1.0, 10.0, 4.0) / 100
    roth_growth = st.slider("Roth Growth Rate (%)", 1.0, 10.0, 5.0) / 100
    broker_growth = st.slider("Brokerage Growth Rate (%)", 1.0, 10.0, 3.0) / 100
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 5.0, 2.5) / 100

# --- 3. CALCULATION ENGINE ---
def calculate_roadmap():
    rows = []
    irmaa_base_2026 = 218000
    cur_ira_h, cur_ira_w = ira_h_init, ira_w_init
    cur_roth, cur_brokerage = roth_init, brokerage_init

    # Track OOM status to trigger event only once
    oom_triggered = False    
    
    # Track if we have already flagged the conversion stop to avoid duplicate events
    conversion_already_stopped = False

    # DYNAMIC RMD AGE CALCULATION
    # Based on birth year derived from age in the start year (2026)
    birth_year_h = 2026 - h_age_at_retire
    birth_year_w = 2026 - w_age_at_retire
    
    # SECURE Act 2.0 Logic:
    # Born 1951-1959 -> RMD Age 73
    # Born 1960 or later -> RMD Age 75
    rmd_age_h = 75 if birth_year_h >= 1960 else 73
    rmd_age_w = 75 if birth_year_w >= 1960 else 73

    for i in range(15):
        year = retire_year + i
        age_h, age_w = h_age_at_retire + i, w_age_at_retire + i
        inf_factor = (1 + inflation_rate) ** i
        ev = []
        
        # 1. Timeline Events using Dynamic RMD Ages
        if year == retire_year: ev.append(t["event_retire"])
        if age_h == 65: ev.append(t["event_hmed"])
        if age_w == 65: ev.append(t["event_wmed"])
        if age_h == rmd_age_h: ev.append(t["event_hrmd"])
        if age_w == rmd_age_w: ev.append(t["event_wrmd"])

        # 2. SMART CONVERSION STOP LOGIC
        active_conversion = roth_conv
        stop_reason = ""

        # Stop condition A: RMD age reached
        if age_h >= rmd_age_h or age_w >= rmd_age_w:
            active_conversion = 0
            stop_reason = "RMD Start"

        # Stop condition B: Low IRA Balance
        if (cur_ira_h + cur_ira_w) < 50000 and active_conversion > 0:
            active_conversion = 0
            stop_reason = "IRA Depleted"

        # 3. RECORD "ROTH STOP" EVENT
        if active_conversion == 0 and not conversion_already_stopped:
            # We check if the user actually had a conversion amount set to begin with
            if roth_conv > 0:
                ev.append(f"{t['event_roth_stop']} ({stop_reason})")
                conversion_already_stopped = True

        # 2. Inflows & RMDs
        rmd_h = (cur_ira_h / 24.6) if age_h >= rmd_age_h else 0
        rmd_w = (cur_ira_w / 26.5) if age_w >= rmd_age_w else 0
        total_rmd = rmd_h + rmd_w
        salary = last_salary if year == retire_year else 0
        h_ss = (ss_h_monthly * 12 * inf_factor) if year >= ss_h_start else 0
        w_ss = max((ss_w_monthly * 12 * inf_factor), (h_ss * 0.5)) if year >= ss_w_start else 0
        total_ss = h_ss + w_ss
        
        # 3. Tax Calculation
        provisional = (salary + taxable_div + annual_ltcg + active_conversion + total_rmd) + muni_int + (total_ss * 0.5)
        taxable_ss = total_ss * 0.85 if provisional > 44000 else 0
        agi = salary + taxable_div + annual_ltcg + active_conversion + taxable_ss + total_rmd
        magi = agi + muni_int
        
        # 4. IRMAA GUARD (Reduce conversion to stay under threshold if applicable)
        irmaa_limit = irmaa_base_2026 * inf_factor
        if magi > irmaa_limit and active_conversion > 0:
            overshoot = magi - irmaa_limit
            active_conversion = max(0, active_conversion - overshoot)
            # Recalculate AGI/MAGI after adjustment
            agi = salary + taxable_div + annual_ltcg + active_conversion + taxable_ss + total_rmd
            magi = agi + muni_int

        deduct = (32200 + (2 if age_h >= 65 and age_w >= 65 else 1) * 1650) * inf_factor
        taxable_inc = max(0, agi - deduct)
        fed_tax = (max(0, taxable_inc - (98900 * inf_factor)) * 0.15) + (min(taxable_inc, 98900 * inf_factor) * 0.11)
        target_expense = (annual_expense * inf_factor) + fed_tax        
        
        # 5. Waterfall Withdrawals
        target_expense = (annual_expense * inf_factor) + fed_tax
        available_cash = total_ss + salary + taxable_div + annual_ltcg + muni_int + total_rmd
        shortfall = max(0, target_expense - available_cash)

        # Calculate total liquid assets before withdrawals
        total_assets_available = cur_brokerage + (cur_ira_h + cur_ira_w) + cur_roth        
        
        # Trigger "Out of Money" event if shortfall exceeds total assets
        if shortfall > total_assets_available and not oom_triggered:
            ev.append(t["event_oom"])
            oom_triggered = True        

        from_broker = min(cur_brokerage, shortfall)
        cur_brokerage -= from_broker
        shortfall -= from_broker
        from_ira = min(cur_ira_h + cur_ira_w, shortfall * 1.15)
        ira_withdrawn = from_ira
        shortfall = max(0, shortfall - (from_ira / 1.15))
        from_roth = min(cur_roth, shortfall)
        cur_roth -= from_roth

        # 6. Progression
        ira_total = cur_ira_h + cur_ira_w
        if ira_total > 0:
            cur_ira_h -= (cur_ira_h / ira_total) * (ira_withdrawn + active_conversion * 0.95)
            cur_ira_w -= (cur_ira_w / ira_total) * (ira_withdrawn + active_conversion * 0.05)
        
        cur_ira_h = max(0, cur_ira_h) * (1 + ira_growth)
        cur_ira_w = max(0, cur_ira_w) * (1 + ira_growth)
        yearly_roth_growth = cur_roth * roth_growth
        cur_roth = (cur_roth + active_conversion + yearly_roth_growth)
        # 1. Calculate the 'Price Growth' (Total Return minus what was paid out as cash)
        # We divide by the current balance to get the yield percentage
        current_yield_rate = (taxable_div + muni_int) / max(1, cur_brokerage)
        effective_price_growth = broker_growth - current_yield_rate

        # 2. Apply growth only to the remaining principal
        cur_brokerage = cur_brokerage * (1 + effective_price_growth)        
        rows.append({
            "Year": year,
            "Ages": f"{age_h}/{age_w}",
            "annual_ltcg": annual_ltcg,  # <--- ADD THIS LINE
            "raw_div": taxable_div,
            "raw_muni": muni_int,
            "LEVER: Roth": active_conversion,
            "OUT: MAGI": magi,
            "OUT: Fed Tax": fed_tax,
            "raw_outflow": target_expense,
            "Total NW": total_assets_available,
            "IRMAA": irmaa,
            "🚨 Important Events": " / ".join(ev) if ev else ""
        })    
        return pd.DataFrame(rows)

# --- 4. MAIN DISPLAY ---
st.title(t["title"])
st.subheader(t["motivation_h"])
st.write(t["motivation_body"])

st.subheader(t["meth_h"])
st.write(t["meth_body"])

st.subheader(t["use_h"])
st.write(t["use_body"])

st.divider()

df = calculate_roadmap()

# --- KPI SECTION ---
st.subheader(t["kpi_h"])
kpi0, kpi1, kpi2, kpi3, kpi4 = st.columns(5)

# New Initial Net Worth Item
with kpi0:
    initial_nw = ira_h_init + ira_w_init + roth_init + brokerage_init
    st.metric(t["kpi_init_nw"], f"${initial_nw:,.0f}")
    st.caption(t["kpi_cap_init"])

with kpi1:
    st.metric(t["kpi_nw"], f"${df.iloc[-1]['Total NW']:,.0f}")
    st.caption(t["kpi_cap_nw"])

with kpi2:
# Sum the total outflow (Living + Tax)
    total_outflow = df["raw_outflow"].sum()
    st.metric(t["kpi_total_outflow"], f"${total_outflow:,.0f}")
    st.caption(t["kpi_cap_outflow"])

with kpi3:
    st.metric(t["kpi_tax"], f"${df['OUT: Fed Tax'].sum():,.0f}")
    st.caption(t["kpi_cap_tax"])

with kpi4:
    st.metric(t["kpi_roth"], f"${df.iloc[-1]['Roth Bal']:,.0f}")
    st.caption(t["kpi_cap_roth"])

st.divider()

# --- ROADMAP TABLE ---
st.subheader(f"{t['roadmap_h']} {retire_year}")
col_map = {
    "raw_div": t["col_tax_div"],     # $33,000
    "raw_muni": t["col_muni"],       # $37,000
    "annual_ltcg": t["col_ltcg"],    # $20,000
    "LEVER: Roth": t["col_roth"],    # $40,000
    "OUT: MAGI": t["col_magi"],      # Total: $130,000
    "OUT: Fed Tax": t["col_tax"], 
    "raw_outflow": t["col_outflow"],
    "Total NW": t["col_nw"], 
    "🚨 Important Events": t["col_events"]
}

# Add the new columns to the selection
display_cols = [
    'Year', 'Ages', 'raw_div', 'raw_muni', 'annual_ltcg', 
    'LEVER: Roth', 'OUT: MAGI', 'OUT: Fed Tax', 
    'raw_outflow', 'Total NW', 'IRMAA', '🚨 Important Events'
]

st.table(df[display_cols].rename(columns=col_map).style.format({
    t["col_tax_div"]: "${:,.0f}",
    t["col_muni"]: "${:,.0f}",
    t["col_ltcg"]: "${:,.0f}",
    t["col_roth"]: "${:,.0f}",
    t["col_magi"]: "${:,.0f}", 
    t["col_tax"]: "${:,.0f}", 
    t["col_outflow"]: "${:,.0f}", 
    t["col_nw"]: "${:,.0f}"
}))

# --- SUMMARY TABLE WITH TOTAL ---
st.divider()
st.subheader(t["summary_h"])

# Tax attribution math
total_tax = df["OUT: Fed Tax"].sum()
total_inc_taxable = df["raw_div"].sum() + df["raw_cg"].sum() + df["raw_rmd"].sum()
tax_per_dollar = total_tax / max(1, total_inc_taxable)

summary_rows = [
    {
        "Type": t["acc_ira"],
        "Init": ira_h_init + ira_w_init,
        "Final": df.iloc[-1]['IRA Bal'],
        "Yield": df["raw_rmd"].sum(),
        "Liability": df["raw_rmd"].sum() * tax_per_dollar
    },
    {
        "Type": t["acc_roth"],
        "Init": roth_init,
        "Final": df.iloc[-1]['Roth Bal'],
        "Yield": df["raw_roth_yield"].sum(),
        "Liability": 0.0
    },
    {
        "Type": t["acc_broker"],
        "Init": brokerage_init,
        "Final": df.iloc[-1]['Brokerage'],
        "Yield": df["raw_div"].sum() + df["raw_cg"].sum() + df["raw_muni"].sum(),
        "Liability": (df["raw_div"].sum() + df["raw_cg"].sum()) * tax_per_dollar
    }
]

df_sum = pd.DataFrame(summary_rows)

# Generate the Account Totals row
totals = {
    "Type": t["total_label"],
    "Init": df_sum["Init"].sum(),
    "Final": df_sum["Final"].sum(),
    "Yield": df_sum["Yield"].sum(),
    "Liability": df_sum["Liability"].sum()
}

df_final_sum = pd.concat([df_sum, pd.DataFrame([totals])], ignore_index=True)

# Display Account Summary
st.table(df_final_sum.rename(columns={
    "Type": "Account", 
    "Init": t["sum_init"], 
    "Final": t["sum_final"], 
    "Yield": t["sum_yield"], 
    "Liability": t["sum_liability"]
}).style.format({
    t["sum_init"]: "${:,.0f}", 
    t["sum_final"]: "${:,.0f}", 
    t["sum_yield"]: "${:,.0f}", 
    t["sum_liability"]: "${:,.0f}"
}))
