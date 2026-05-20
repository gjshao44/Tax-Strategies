import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comprehensive Retirement Wealth & Tax Optimizer", layout="wide")

# --- 1. LANGUAGE DICTIONARY ---
# --- MODIFIED: Added specific column keys for transparency ---
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
        "filing_status": "Tax Filing Status",
        "qd_ratio": "Qualified Dividend %",
        "col_ss": "INPUT: SS",
        "col_roth": "LEVER: Roth",
        "col_div": "INPUT: Taxable Div",
        "col_muni": "INPUT: Tax-Free Int",
        "col_cg": "INPUT: Cap Gains",
        "col_outflow": "OUT: Total Outflow",
        "col_magi": "OUT: MAGI",
        "col_tax": "OUT: Fed Tax",
        "col_nw": "Total Net Worth",
        "col_events": "🚨 Important Events",
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
        "total_label": "**TOTAL ASSETS**",
        "comp_header": "⚖️ Strategy vs. Baseline Comparison (15-Year Summary)",
        "comp_desc": "Compares your active strategy levers against a baseline scenario with no Roth conversions and no capital gains harvesting.",
        "kpi_nw_gain": "Final Net Worth Gain",
        "kpi_tax_saved": "Cumulative Taxes Saved",
        "kpi_tax_extra": "Upfront Tax Cost",
        "kpi_roth_boost": "Final Roth Reservoir Boost",
        "kpi_baseline": "Baseline",
        "kpi_strategy": "Strategy"
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
        "filing_status": "报税状态",
        "qd_ratio": "符合条件的股息比例 (Qualified %)",
        "col_ss": "社保收入",
        "col_roth": "Roth转换",
        "col_div": "应税股息",
        "col_muni": "免税利息(Muni)",
        "col_cg": "资本利得",
        "col_outflow": "总支出(含税)",
        "col_magi": "MAGI(医保判定)",
        "col_tax": "联邦税支出",
        "col_nw": "总净资产",
        "col_events": "🚨 重要事件",
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
        "total_label": "**资产总计**",
        "comp_header": "⚖️ 优化策略 vs. 基准对比 (15年累计)",
        "comp_desc": "将您当前的优化策略与“不做任何操作”（不进行 Roth 转换，不进行资本利得变现）的基准方案进行对比。",
        "kpi_nw_gain": "最终净资产提升",
        "kpi_tax_saved": "累计节省税款",
        "kpi_tax_extra": "前期税务成本",
        "kpi_roth_boost": "免税 Roth 账户增幅",
        "kpi_baseline": "基准方案",
        "kpi_strategy": "优化策略"
    }
}

# --- 2. SIDEBAR INPUTS ---
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

    st.header(t["sidebar_levers"])
    tax_status = st.selectbox(t["filing_status"], ["MFJ", "Single", "MFS"])
    roth_conv = st.slider("Annual Roth Conversion ($)", 0, 200000, 40000, step=5000)
    annual_ltcg = st.slider("Annual Cap Gains Realized ($)", 0, 1000000, 20000, step=10000)

    st.header(t["sidebar_cash"])
    annual_expense = st.number_input("Annual Living Expense (Today's $)", value=100000)
    qd_perc = st.slider(t["qd_ratio"], 0, 100, 80) / 100
    taxable_div_in = st.number_input("Annual Taxable Dividends", value=33000)
    muni_int_in = st.number_input("Annual Tax-Free Muni Interest", value=37000)
    last_salary = st.number_input("Final Salary (Retirement Year)", value=0)
    
    st.header(t["sidebar_ss"])
    ss_h_monthly = st.number_input("H Monthly SS ($)", value=4000)
    ss_h_start = st.number_input("H Start Year", value=2029)
    ss_w_monthly = st.number_input("W Monthly SS ($)", value=3000)
    ss_w_start = st.number_input("W Start Year", value=2029)

    st.header(t["sidebar_growth"])
    ira_growth = st.slider("IRA Growth Rate (%)", 1.0, 10.0, 4.0) / 100
    roth_growth = st.slider("Roth Growth Rate (%)", 1.0, 10.0, 5.0) / 100
    broker_growth = st.slider("Brokerage Growth Rate (%)", 1.0, 10.0, 3.0) / 100
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 5.0, 2.5) / 100

# --- 3. CORE TAX CALCULATOR ---
def calculate_comprehensive_tax(ordinary_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, status):
    # Ordinary Brackets (2026 Estimated)
    ord_tax = 0
    if status == "MFJ":
        brackets = [(23200, 0.10), (94300, 0.12), (201050, 0.22), (383900, 0.24)]
        top_rate = 0.32
    else: # Single or MFS
        brackets = [(11600, 0.10), (47150, 0.12), (100525, 0.22), (191950, 0.24)]
        top_rate = 0.32

    prev_limit = 0
    for limit, rate in brackets:
        adj_limit = limit * inf_factor
        taxable_in_bracket = min(ordinary_taxable, adj_limit) - prev_limit
        if taxable_in_bracket > 0:
            ord_tax += taxable_in_bracket * rate
        prev_limit = adj_limit
    if ordinary_taxable > prev_limit:
        ord_tax += (ordinary_taxable - prev_limit) * top_rate

    # Graduated LTCG/QD Brackets (0%, 15%, 20%)
    if status == "MFJ":
        zero_limit = 94050 * inf_factor
        fifteen_limit = 583750 * inf_factor
    else: # Single or MFS
        zero_limit = 47025 * inf_factor
        fifteen_limit = 291850 * inf_factor
    
    ltcg_in_zero = max(0, min(qd_ltcg_total, zero_limit - ordinary_taxable))
    ltcg_in_fifteen = max(0, min(qd_ltcg_total - ltcg_in_zero, fifteen_limit - max(ordinary_taxable, zero_limit)))
    ltcg_in_twenty = max(0, qd_ltcg_total - ltcg_in_zero - ltcg_in_fifteen)
    
    ltcg_tax = (ltcg_in_fifteen * 0.15) + (ltcg_in_twenty * 0.20)

    # NIIT (3.8%)
    niit_threshold = (250000 if status == "MFJ" else 200000 if status == "Single" else 125000) * inf_factor
    tax_niit = 0
    if magi > niit_threshold:
        investment_income = qd_ltcg_total + max(0, (ordinary_taxable - taxable_ss))
        tax_niit = min(investment_income, magi - niit_threshold) * 0.038
        
    return ord_tax + ltcg_tax + tax_niit

def get_rmd_divisor(age):
    if age < 73: return 0.0
    table = {
        73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
        80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
        87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1,
        94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4
    }
    return table.get(age, max(1.0, 6.4 - (age - 100) * 0.4))

# --- 4. CALCULATION ENGINE ---
def calculate_roadmap(conv_override=None, ltcg_override=None):
    rows = []
    irmaa_base_2026 = 218000 if tax_status == "MFJ" else 109000
    cur_ira_h, cur_ira_w = ira_h_init, ira_w_init
    cur_roth, cur_brokerage = roth_init, brokerage_init
    oom_triggered = False    
    conversion_already_stopped = False

    sim_roth_conv = conv_override if conv_override is not None else roth_conv
    sim_annual_ltcg = ltcg_override if ltcg_override is not None else annual_ltcg

    birth_year_h = 2026 - h_age_at_retire
    birth_year_w = 2026 - w_age_at_retire
    rmd_age_h = 75 if birth_year_h >= 1960 else 73
    rmd_age_w = 75 if birth_year_w >= 1960 else 73

    for i in range(15):
        year = retire_year + i
        age_h, age_w = h_age_at_retire + i, w_age_at_retire + i
        inf_factor = (1 + inflation_rate) ** i
        ev = []
        
        if year == retire_year: ev.append(t["event_retire"])
        if age_h == 65: ev.append(t["event_hmed"])
        if age_w == 65: ev.append(t["event_wmed"])
        if age_h == rmd_age_h: ev.append(t["event_hrmd"])
        if age_w == rmd_age_w: ev.append(t["event_wrmd"])

        # Cap conversion at available IRA balance
        active_conversion = min(sim_roth_conv, cur_ira_h + cur_ira_w)
        stop_reason = ""
        
        if age_h >= rmd_age_h or age_w >= rmd_age_w:
            active_conversion = 0
            stop_reason = "RMD Start"
        elif (cur_ira_h + cur_ira_w) <= 1000 and sim_roth_conv > 0:
            active_conversion = 0
            stop_reason = "IRA Depleted"

        if active_conversion == 0 and not conversion_already_stopped and sim_roth_conv > 0:
            ev.append(f"{t['event_roth_stop']} ({stop_reason})")
            conversion_already_stopped = True

        divisor_h = get_rmd_divisor(age_h)
        divisor_w = get_rmd_divisor(age_w)
        rmd_h = (cur_ira_h / divisor_h) if divisor_h > 0 else 0
        rmd_w = (cur_ira_w / divisor_w) if divisor_w > 0 else 0
        total_rmd = rmd_h + rmd_w
        salary = last_salary if year == retire_year else 0
        h_ss = (ss_h_monthly * 12 * inf_factor) if year >= ss_h_start else 0
        w_ss = max((ss_w_monthly * 12 * inf_factor), (h_ss * 0.5)) if year >= ss_w_start else 0
        total_ss = h_ss + w_ss
        
        qual_div = taxable_div_in * qd_perc
        ord_div = taxable_div_in * (1 - qd_perc)
        
        # IRS Graduated Social Security Combined Income "Tax Torpedo"
        combined_income = salary + ord_div + qual_div + sim_annual_ltcg + active_conversion + total_rmd + muni_int_in + (total_ss * 0.5)
        taxable_ss = 0
        if tax_status == "MFJ":
            if combined_income > 44000:
                taxable_ss = min(0.85 * total_ss, 6000 + 0.85 * (combined_income - 44000))
            elif combined_income > 32000:
                taxable_ss = min(0.5 * total_ss, 0.5 * (combined_income - 32000))
        else:
            if combined_income > 34000:
                taxable_ss = min(0.85 * total_ss, 4500 + 0.85 * (combined_income - 34000))
            elif combined_income > 25000:
                taxable_ss = min(0.5 * total_ss, 0.5 * (combined_income - 25000))
                
        ordinary_gross = salary + ord_div + taxable_ss + active_conversion + total_rmd
        qd_ltcg_total = qual_div + sim_annual_ltcg
        magi = ordinary_gross + qd_ltcg_total + muni_int_in
        
        # 5-Tier Medicare IRMAA Surcharge logic
        base_irmaa = irmaa_base_2026 * inf_factor
        t1, t2, t3, t4, t5 = base_irmaa, base_irmaa * (272/218), base_irmaa * (340/218), base_irmaa * (408/218), base_irmaa * (750/218)
        
        irmaa_tier = 0
        irmaa_surcharge = 0
        num_spouses_medicare = (1 if age_h >= 65 else 0) + (1 if age_w >= 65 else 0)
        
        if magi > t5: irmaa_tier, irmaa_surcharge = 5, 480 * 12 * num_spouses_medicare
        elif magi > t4: irmaa_tier, irmaa_surcharge = 4, 440 * 12 * num_spouses_medicare
        elif magi > t3: irmaa_tier, irmaa_surcharge = 3, 320 * 12 * num_spouses_medicare
        elif magi > t2: irmaa_tier, irmaa_surcharge = 2, 200 * 12 * num_spouses_medicare
        elif magi > t1: irmaa_tier, irmaa_surcharge = 1, 80 * 12 * num_spouses_medicare
        
        irmaa_surcharge *= inf_factor # adjust surcharges for inflation

        # Deduction Logic
        base_deduct = 32200 if tax_status == "MFJ" else 16100
        extra_deduct = 0
        if tax_status == "MFJ":
            if age_h >= 65: extra_deduct += 1650
            if age_w >= 65: extra_deduct += 1650
        else:
            if age_h >= 65: extra_deduct += 1950 # Assuming Single/H-focused
        
        deduct = (base_deduct + extra_deduct) * inf_factor
        ord_taxable = max(0, ordinary_gross - deduct)
        
        fed_tax = calculate_comprehensive_tax(ord_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, tax_status)
        
        target_expense = (annual_expense * inf_factor) + fed_tax + irmaa_surcharge       
        available_cash = total_ss + salary + taxable_div_in + sim_annual_ltcg + muni_int_in + total_rmd
        shortfall = max(0, target_expense - available_cash)
        
        if shortfall > (cur_brokerage + (cur_ira_h + cur_ira_w) + cur_roth) and not oom_triggered:
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

        ira_total = cur_ira_h + cur_ira_w
        if ira_total > 0:
            h_ratio = cur_ira_h / ira_total
            w_ratio = cur_ira_w / ira_total
            cur_ira_h -= h_ratio * (ira_withdrawn + active_conversion)
            cur_ira_w -= w_ratio * (ira_withdrawn + active_conversion)
        
        cur_ira_h = max(0, cur_ira_h) * (1 + ira_growth)
        cur_ira_w = max(0, cur_ira_w) * (1 + ira_growth)
        yearly_roth_growth = cur_roth * roth_growth
        cur_roth = (cur_roth + active_conversion + yearly_roth_growth)
        cur_brokerage *= (1 + broker_growth)
        
        rows.append({
            "Year": year, "Ages": f"{age_h}/{age_w}", "INPUT: SS": total_ss, 
            "raw_div": taxable_div_in, "raw_muni": muni_int_in, "raw_cg": sim_annual_ltcg,
            "LEVER: Roth": active_conversion, "OUT: MAGI": magi, "OUT: Fed Tax": fed_tax,
            "raw_outflow": target_expense, "Roth Bal": cur_roth, "IRA Bal": cur_ira_h + cur_ira_w, 
            "Brokerage": cur_brokerage, "Total NW": cur_ira_h + cur_ira_w + cur_roth + cur_brokerage,
            "IRMAA": "✅ Safe" if irmaa_tier == 0 else f"🚩 Tier {irmaa_tier}",
            "🚨 Important Events": ", ".join(ev), "raw_roth_yield": yearly_roth_growth, "raw_rmd": total_rmd
        })
    return pd.DataFrame(rows)

# --- 5. UI DISPLAY ---
st.title(t["title"])
st.subheader(t["motivation_h"])
st.write(t["motivation_body"])

st.subheader(t["meth_h"])
st.markdown(t["meth_body"])

st.subheader(t["use_h"])
st.markdown(t["use_body"])

df_baseline = calculate_roadmap(conv_override=0, ltcg_override=0)
df = calculate_roadmap()

# --- STRATEGY COMPARISON DASHBOARD ---
st.subheader(t["comp_header"])
st.write(t["comp_desc"])

nw_base = df_baseline.iloc[-1]['Total NW']
nw_strat = df.iloc[-1]['Total NW']
nw_gain = nw_strat - nw_base

tax_base = df_baseline['OUT: Fed Tax'].sum()
tax_strat = df['OUT: Fed Tax'].sum()
tax_saved = tax_base - tax_strat

roth_base = df_baseline.iloc[-1]['Roth Bal']
roth_strat = df.iloc[-1]['Roth Bal']
roth_boost = roth_strat - roth_base

c1, c2, c3 = st.columns(3)

with c1:
    sign_nw = "+" if nw_gain >= 0 else ""
    color_nw = "#2ecc71" if nw_gain >= 0 else "#e74c3c"
    bg_nw = "rgba(46, 204, 113, 0.08)" if nw_gain >= 0 else "rgba(231, 76, 60, 0.08)"
    border_nw = "rgba(46, 204, 113, 0.3)" if nw_gain >= 0 else "rgba(231, 76, 60, 0.3)"
    st.markdown(f"""
    <div style="background-color: {bg_nw}; border: 1px solid {border_nw}; padding: 15px; border-radius: 8px; text-align: center;">
        <h4 style="margin: 0; color: #888888; font-size: 0.9rem; font-weight: normal;">{t["kpi_nw_gain"]}</h4>
        <p style="margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold; color: {color_nw};">{sign_nw}${nw_gain:,.0f}</p>
        <span style="font-size: 0.8rem; color: #888888;">{t["kpi_baseline"]}: ${nw_base:,.0f} vs {t["kpi_strategy"]}: ${nw_strat:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if tax_saved >= 0:
        tax_title = t["kpi_tax_saved"]
        tax_color = "#2ecc71"
        tax_bg = "rgba(46, 204, 113, 0.08)"
        tax_border = "rgba(46, 204, 113, 0.3)"
        tax_val_str = f"+${tax_saved:,.0f}"
    else:
        tax_title = t["kpi_tax_extra"]
        tax_color = "#f39c12"  # Frontloaded tax is an investment
        tax_bg = "rgba(243, 156, 18, 0.08)"
        tax_border = "rgba(243, 156, 18, 0.3)"
        tax_val_str = f"-${abs(tax_saved):,.0f}"
        
    st.markdown(f"""
    <div style="background-color: {tax_bg}; border: 1px solid {tax_border}; padding: 15px; border-radius: 8px; text-align: center;">
        <h4 style="margin: 0; color: #888888; font-size: 0.9rem; font-weight: normal;">{tax_title}</h4>
        <p style="margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold; color: {tax_color};">{tax_val_str}</p>
        <span style="font-size: 0.8rem; color: #888888;">{t["kpi_baseline"]}: ${tax_base:,.0f} vs {t["kpi_strategy"]}: ${tax_strat:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    sign_roth = "+" if roth_boost >= 0 else ""
    color_roth = "#3498db" if roth_boost >= 0 else "#e74c3c"
    bg_roth = "rgba(52, 152, 219, 0.08)" if roth_boost >= 0 else "rgba(231, 76, 60, 0.08)"
    border_roth = "rgba(52, 152, 219, 0.3)" if roth_boost >= 0 else "rgba(231, 76, 60, 0.3)"
    st.markdown(f"""
    <div style="background-color: {bg_roth}; border: 1px solid {border_roth}; padding: 15px; border-radius: 8px; text-align: center;">
        <h4 style="margin: 0; color: #888888; font-size: 0.9rem; font-weight: normal;">{t["kpi_roth_boost"]}</h4>
        <p style="margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold; color: {color_roth};">{sign_roth}${roth_boost:,.0f}</p>
        <span style="font-size: 0.8rem; color: #888888;">{t["kpi_baseline"]}: ${roth_base:,.0f} vs {t["kpi_strategy"]}: ${roth_strat:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- ACTIVE STRATEGY DETAILS ---
st.subheader(t["kpi_h"])
k0, k1, k2, k3, k4 = st.columns(5)
k0.metric(t["kpi_init_nw"], f"${(ira_h_init + ira_w_init + roth_init + brokerage_init):,.0f}", help=t["kpi_cap_init"])
k1.metric(t["kpi_nw"], f"${df.iloc[-1]['Total NW']:,.0f}", help=t["kpi_cap_nw"])
k2.metric(t["kpi_total_outflow"], f"${df['raw_outflow'].sum():,.0f}", help=t["kpi_cap_outflow"])
k3.metric(t["kpi_tax"], f"${df['OUT: Fed Tax'].sum():,.0f}", help=t["kpi_cap_tax"])
k4.metric(t["kpi_roth"], f"${df.iloc[-1]['Roth Bal']:,.0f}", help=t["kpi_cap_roth"])

st.divider()
st.subheader(f"{t['roadmap_h']} {retire_year}")
col_map = {"INPUT: SS": t["col_ss"], "raw_div": t["col_div"], "raw_muni": t["col_muni"], "raw_cg": t["col_cg"], "LEVER: Roth": t["col_roth"], "OUT: MAGI": t["col_magi"], "OUT: Fed Tax": t["col_tax"], "raw_outflow": t["col_outflow"], "Total NW": t["col_nw"], "🚨 Important Events": t["col_events"]}
st.table(df[['Year', 'Ages', 'INPUT: SS', 'raw_div', 'raw_muni', 'raw_cg', 'LEVER: Roth', 'OUT: MAGI', 'OUT: Fed Tax', 'raw_outflow', 'Total NW', 'IRMAA', '🚨 Important Events']].rename(columns=col_map).style.format({t["col_ss"]: "${:,.0f}", t["col_div"]: "${:,.0f}", t["col_muni"]: "${:,.0f}", t["col_cg"]: "${:,.0f}", t["col_roth"]: "${:,.0f}", t["col_magi"]: "${:,.0f}", t["col_tax"]: "${:,.0f}", t["col_outflow"]: "${:,.0f}", t["col_nw"]: "${:,.0f}"}))

# Summary Table
st.divider()
st.subheader(t["summary_h"])
total_tax = df["OUT: Fed Tax"].sum()
total_taxable_yield = df["raw_div"].sum() + df["raw_cg"].sum() + df["raw_rmd"].sum()
tax_per_dollar = total_tax / max(1, total_taxable_yield)

summary_rows = [
    {"Type": t["acc_ira"], "Init": ira_h_init + ira_w_init, "Final": df.iloc[-1]['IRA Bal'], "Yield": df["raw_rmd"].sum(), "Liability": df["raw_rmd"].sum() * tax_per_dollar},
    {"Type": t["acc_roth"], "Init": roth_init, "Final": df.iloc[-1]['Roth Bal'], "Yield": df["raw_roth_yield"].sum(), "Liability": 0.0},
    {"Type": t["acc_broker"], "Init": brokerage_init, "Final": df.iloc[-1]['Brokerage'], "Yield": df["raw_div"].sum() + df["raw_cg"].sum() + df["raw_muni"].sum(), "Liability": (df["raw_div"].sum() + df["raw_cg"].sum()) * tax_per_dollar}
]
df_sum = pd.DataFrame(summary_rows)
totals = {"Type": t["total_label"], "Init": df_sum["Init"].sum(), "Final": df_sum["Final"].sum(), "Yield": df_sum["Yield"].sum(), "Liability": df_sum["Liability"].sum()}
df_final_sum = pd.concat([df_sum, pd.DataFrame([totals])], ignore_index=True)
st.table(df_final_sum.rename(columns={"Type": "Account", "Init": t["sum_init"], "Final": t["sum_final"], "Yield": t["sum_yield"], "Liability": t["sum_liability"]}).style.format({t["sum_init"]: "${:,.0f}", t["sum_final"]: "${:,.0f}", t["sum_yield"]: "${:,.0f}", t["sum_liability"]: "${:,.0f}"}))