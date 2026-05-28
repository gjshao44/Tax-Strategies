import streamlit as st
import pandas as pd
import altair as alt
import json

st.set_page_config(page_title="Comprehensive Retirement Wealth & Tax Optimizer", layout="wide")

# --- 1. LANGUAGE DICTIONARY ---
LANG_MAP = {
    "English": {
        "title": "🛡️ Comprehensive Retirement Wealth & Tax Optimizer",
        "privacy_note": "🔒 Privacy & Data Security Notice: This application runs entirely within your local browser session. No user data, asset values, or personal tax profiles are ever collected, tracked, or stored on any external server. Your financial information remains completely private.",
        "motivation_h": "✍️ Motivation",
        "motivation_body": "This tool provides prospective retirees or current retirees with a tax strategy simulation and individualizes the various levers to convert to Roth; to realize capital gains; to test different growth scenarios. The goal is to achive optimum total wealth, while minimizing the total federal tax paid in the horizon.",
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
* **Explore Strategy Lab:** Navigate to the "Strategy Lab" tab to run automated sensitivity analyses that identify your mathematically optimal annual Roth conversion amount and window.
* **Observe Total Net Worth:** Watch the final column of the roadmap to see how paying taxes early (in Roth conversion, tax free bond, harvesting capital gains) preserves long-term capital.
""",
        "kpi_h": "🚀 {sim_years}-Year Strategic Outlook",
        "kpi_init_nw": "Initial Net Worth",
        "kpi_nw": "Estimated Final Net Worth (Year {sim_years})",
        "kpi_tax": "Total Federal Tax Paid",
        "kpi_roth": "Total Roth Reservoir",
        "kpi_total_outflow": "Total {sim_years}-Yr Outflow",
        "kpi_cap_outflow": "Total living expenses plus all federal taxes paid over {sim_years} years.",        
        "kpi_cap_init": "Your starting capital across all accounts.",
        "kpi_cap_nw": "Total capital remaining across all accounts after {sim_years} years.",
        "kpi_cap_tax": "Cumulative tax burden over the {sim_years}-year period.",
        "kpi_cap_roth": "Final tax-free balance available for heirs or late-life needs.",
        "roadmap_h": "Retirement Roadmap starting",
        "summary_h": "📊 Strategic Account Summary ({sim_years}-Year Cumulative)",
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
        "sum_yield": "Total {sim_years}-Yr Yield/Income",
        "sum_liability": "Total {sim_years}-Yr Tax Liability",
        "total_label": "**TOTAL ASSETS**",
        "comp_header": "⚖️ Strategy vs. Baseline Comparison ({sim_years}-Year Summary)",
        "comp_desc": "Compares your active strategy levers against a baseline scenario with no Roth conversions and no capital gains harvesting over {sim_years} years.",
        "kpi_nw_gain": "Final Net Worth Gain",
        "kpi_tax_saved": "Cumulative Taxes Saved",
        "kpi_tax_extra": "Upfront Tax Cost",
        "kpi_roth_boost": "Final Roth Reservoir Boost",
        "kpi_baseline": "Baseline",
        "kpi_strategy": "Strategy",
        "tab_roadmap": "📈 Detailed Roadmap",
        "tab_lab": "🔬 Strategy Lab",
        "tab_data": "💾 Data Management",
        "lab_roth_h": "Roth Conversion Sensitivity Analysis",
        "lab_roth_desc": "This simulation tests various fixed annual Roth conversion amounts to see their impact on your long-term Total Net Worth. Conversions are assumed to occur annually until RMDs begin or the IRA is depleted. The peak of the curve represents the mathematical optimum balancing today's taxes vs. future RMD taxes. (Simulated over a {lab_horizon}-year minimum horizon).",
        "lab_roth_chart_x": "Annual Conversion Amount",
        "lab_roth_chart_y": "Final Net Worth",
        "lab_roth_optimum": "Based on the simulation, the optimum annual Roth conversion amount is approximately",
        "lab_stop_h": "Roth Window Optimizer (Stop Age)",
        "lab_stop_desc": "Using the optimal amount (${best_amt:,.0f}), this tests which age to stop converting to maximize net worth. Often stopping when Social Security starts (Age 67-70) is ideal to avoid higher tax brackets.",
        "lab_stop_chart_x": "Stop Age",
        "lab_stop_optimum": "The optimum age to stop Roth conversions is"
    },
    "Chinese": {
        "title": "🛡️ 综合退休财富与税务优化工具",
        "privacy_note": "🔒 隐私与数据安全提示：本程序完全在您的本地浏览器会话中运行。任何用户数据、资产数值或个人税务信息均不会被收集、追踪或存储在任何外部服务器上。您的财务信息将完全保持私密。",
        "motivation_h": "✍️ 建立初衷",
        "motivation_body": "本工具为准退休人员或已退休人员提供税务策略模拟。通过量化 Roth 转换、资本利得变现及不同增长场景等杠杆，目标是实现最优的总财富, 同时最小化未来预见的联邦税总支出。",
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
* **观察总净资产 (Total Net Worth):** 关注路线图的最后一列，观察通过早期纳税（如 Roth 转换、税收减免债券、资本利得变现）如何保护长期资本。
""",
        "kpi_h": "🚀 {sim_years}年战略展望",
        "kpi_init_nw": "初始净资产", 
        "kpi_nw": "预计最终净资产 (第{sim_years}年)",
        "kpi_tax": "联邦税总支出",
        "kpi_roth": "Roth 账户储备",
        "kpi_total_outflow": "{sim_years}年总支出",
        "kpi_cap_outflow": "{sim_years}年总生活支出与联邦税收之和",        
        "kpi_cap_init": "您的账户初始总资本", 
        "kpi_cap_nw": "{sim_years}年后所有账户中的剩余总资本",
        "kpi_cap_tax": "{sim_years}年期间累计的税务负担",
        "kpi_cap_roth": "可供继承或后期使用的最终免税余额",
        "roadmap_h": "退休财务路线图 - 始于",
        "summary_h": "📊 战略账户总结 ({sim_years}年累计)",
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
        "sum_yield": "{sim_years}年总收益/收入",
        "sum_liability": "{sim_years}年总税务责任",
        "total_label": "**资产总计**",
        "comp_header": "⚖️ 优化策略 vs. 基准对比 ({sim_years}年累计)",
        "comp_desc": "将您当前的优化策略与“不做任何操作”（不进行 Roth 转换，不进行资本利得变现）的基准方案进行对比，基于{sim_years}年模拟。",
        "kpi_nw_gain": "最终净资产提升",
        "kpi_tax_saved": "累计节省税款",
        "kpi_tax_extra": "前期税务成本",
        "kpi_roth_boost": "免税 Roth 账户增幅",
        "kpi_baseline": "基准方案",
        "kpi_strategy": "优化策略",
        "tab_roadmap": "📈 详细路线图",
        "tab_lab": "🔬 策略实验室",
        "tab_data": "💾 数据管理",
        "lab_roth_h": "Roth 转换敏感性分析",
        "lab_roth_desc": "本模拟测试各种固定的年度 Roth 转换金额，以观察其对长远总净资产的影响。假设转换每年进行，直到 RMD 开始或 IRA 耗尽。曲线的峰值代表了平衡当前税收与未来 RMD 税收的数学最优解。（基于至少 {lab_horizon} 年的模拟周期）。",
        "lab_roth_chart_x": "年度转换金额",
        "lab_roth_chart_y": "最终总净资产",
        "lab_roth_optimum": "根据模拟，最佳年度 Roth 转换金额约为",
        "lab_stop_h": "Roth 转换周期（停止年龄）优化",
        "lab_stop_desc": "使用上述最佳金额 (${best_amt:,.0f})，测试在哪个年龄停止转换可以使净资产最大化。通常在社保开始领取时（67-70岁）停止转换是理想的，以避免进入更高的税率档位。",
        "lab_stop_chart_x": "停止年龄",
        "lab_stop_optimum": "最佳停止 Roth 转换的年龄是"
    }
}

# --- 2. SIDEBAR INPUTS ---
with st.sidebar:
    lang = st.radio("Language / 语言选择", ["English", "Chinese"], horizontal=True)
    t = LANG_MAP[lang]
    
    st.header(t["sidebar_timeline"])
    retire_year = st.number_input("Full Retirement Year", value=int(st.session_state.get("retire_year", 2026)))
    sim_years = st.slider("Simulation Horizon (Years)", 10, 40, value=int(st.session_state.get("sim_years", 15)))
    h_age_at_retire = st.number_input(f"Husband Age in {retire_year}", value=int(st.session_state.get("h_age_at_retire", 64)))
    w_age_at_retire = st.number_input(f"Wife Age in {retire_year}", value=int(st.session_state.get("w_age_at_retire", 64)))

    st.header(t["sidebar_assets"])
    ira_h_init = st.number_input("Husband IRA Balance ($)", value=int(st.session_state.get("ira_h_init", 1500000)))
    ira_w_init = st.number_input("Wife IRA Balance ($)", value=int(st.session_state.get("ira_w_init", 10000)))
    roth_init = st.number_input("Roth IRA Balance ($)", value=int(st.session_state.get("roth_init", 100000)))
    brokerage_init = st.number_input("Taxable Brokerage Balance ($)", value=int(st.session_state.get("brokerage_init", 1000000)))

    st.header(t["sidebar_levers"])
    status_options = ["MFJ", "Single", "MFS"]
    saved_status = st.session_state.get("tax_status", "MFJ")
    status_idx = status_options.index(saved_status) if saved_status in status_options else 0
    tax_status = st.selectbox(t["filing_status"], status_options, index=status_idx)
    roth_conv = st.slider("Annual Roth Conversion ($)", 0, 200000, value=int(st.session_state.get("roth_conv", 40000)), step=5000)
    annual_ltcg = st.slider("Annual Cap Gains Realized ($)", 0, 1000000, value=int(st.session_state.get("annual_ltcg", 20000)), step=10000)

    st.header(t["sidebar_cash"])
    annual_expense = st.number_input("Annual Living Expense (Today's $)", value=int(st.session_state.get("annual_expense", 100000)))
    qd_perc_raw = st.slider(t["qd_ratio"], 0, 100, value=int(st.session_state.get("qd_perc_raw", 80)))
    qd_perc = qd_perc_raw / 100
    taxable_div_in = st.number_input("Annual Taxable Dividends", value=int(st.session_state.get("taxable_div_in", 33000)))
    muni_int_in = st.number_input("Annual Tax-Free Muni Interest", value=int(st.session_state.get("muni_int_in", 37000)))
    last_salary = st.number_input("Final Salary (Retirement Year)", value=int(st.session_state.get("last_salary", 0)))
    
    st.header(t["sidebar_ss"])
    ss_h_monthly = st.number_input("H Monthly SS ($)", value=int(st.session_state.get("ss_h_monthly", 4000)))
    ss_h_start = st.number_input("H Start Year", value=int(st.session_state.get("ss_h_start", 2029)))
    ss_w_monthly = st.number_input("W Monthly SS ($)", value=int(st.session_state.get("ss_w_monthly", 3000)))
    ss_w_start = st.number_input("W Start Year", value=int(st.session_state.get("ss_w_start", 2029)))

    st.header(t["sidebar_growth"])
    ira_growth_raw = st.slider("IRA Growth Rate (%)", 1.0, 10.0, value=float(st.session_state.get("ira_growth_raw", 4.0)))
    ira_growth = ira_growth_raw / 100
    roth_growth_raw = st.slider("Roth Growth Rate (%)", 1.0, 10.0, value=float(st.session_state.get("roth_growth_raw", 5.0)))
    roth_growth = roth_growth_raw / 100
    broker_growth_raw = st.slider("Brokerage Growth Rate (%)", 1.0, 10.0, value=float(st.session_state.get("broker_growth_raw", 3.0)))
    broker_growth = broker_growth_raw / 100
    inflation_rate_raw = st.slider("Inflation Rate (%)", 0.0, 5.0, value=float(st.session_state.get("inflation_rate_raw", 2.5)))
    inflation_rate = inflation_rate_raw / 100

# --- 3. CORE TAX CALCULATOR ---
def calculate_comprehensive_tax(ordinary_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, status, year_idx):
    ord_tax = 0
    if status == "MFJ":
        brackets = [(23200, 0.10), (94300, 0.12), (201050, 0.22), (383900, 0.24)]
        top_rate = 0.32
    else: 
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

    if status == "MFJ":
        zero_limit = 94050 * inf_factor
        fifteen_limit = 583750 * inf_factor
    else: 
        zero_limit = 47025 * inf_factor
        fifteen_limit = 291850 * inf_factor
    
    ltcg_in_zero = max(0, min(qd_ltcg_total, zero_limit - ordinary_taxable))
    ltcg_in_fifteen = max(0, min(qd_ltcg_total - ltcg_in_zero, fifteen_limit - max(ordinary_taxable, zero_limit)))
    ltcg_in_twenty = max(0, qd_ltcg_total - ltcg_in_zero - ltcg_in_fifteen)
    
    ltcg_tax = (ltcg_in_fifteen * 0.15) + (ltcg_in_twenty * 0.20)

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

def get_irmaa_surcharge(magi, inf_factor, num_spouses_medicare):
    base_irmaa = 218000 * inf_factor
    t1, t2, t3, t4, t5 = base_irmaa, base_irmaa * (272/218), base_irmaa * (340/218), base_irmaa * (408/218), base_irmaa * (750/218)
    if magi > t5: return 5, 480 * 12 * num_spouses_medicare * inf_factor
    if magi > t4: return 4, 440 * 12 * num_spouses_medicare * inf_factor
    if magi > t3: return 3, 320 * 12 * num_spouses_medicare * inf_factor
    if magi > t2: return 2, 200 * 12 * num_spouses_medicare * inf_factor
    if magi > t1: return 1, 80 * 12 * num_spouses_medicare * inf_factor
    return 0, 0

# --- 4. CALCULATION ENGINE (WITH CACHE) ---
@st.cache_data
def calculate_roadmap(
    ira_h_init, ira_w_init, roth_init, brokerage_init,
    retire_year, sim_years, h_age_at_retire, w_age_at_retire,
    tax_status, roth_conv, annual_ltcg, annual_expense, qd_perc,
    taxable_div_in, muni_int_in, last_salary,
    ss_h_monthly, ss_h_start, ss_w_monthly, ss_w_start,
    ira_growth, roth_growth, broker_growth, inflation_rate,
    lang,
    conv_override=None, ltcg_override=None, horizon_override=None, 
    ss_start_h=None, ss_start_w=None, conv_stop_age_override=None
):
    t_internal = LANG_MAP[lang]
    rows = []
    cur_ira_h, cur_ira_w = ira_h_init, ira_w_init
    cur_roth, cur_brokerage = roth_init, brokerage_init
    oom_triggered = False    
    conversion_already_stopped = False

    sim_roth_conv = conv_override if conv_override is not None else roth_conv
    sim_annual_ltcg = ltcg_override if ltcg_override is not None else annual_ltcg
    sim_horizon = horizon_override if horizon_override is not None else sim_years
    actual_ss_h_start = ss_start_h if ss_start_h is not None else ss_h_start
    actual_ss_w_start = ss_start_w if ss_start_w is not None else ss_w_start

    birth_year_h = 2026 - h_age_at_retire
    birth_year_w = 2026 - w_age_at_retire
    rmd_age_h = 75 if birth_year_h >= 1960 else 73
    rmd_age_w = 75 if birth_year_w >= 1960 else 73

    sim_conv_stop_age = conv_stop_age_override if conv_stop_age_override is not None else min(rmd_age_h, rmd_age_w)

    for i in range(sim_horizon):
        year = retire_year + i
        age_h, age_w = h_age_at_retire + i, w_age_at_retire + i
        inf_factor = (1 + inflation_rate) ** i
        ev = []
        
        if year == retire_year: ev.append(t_internal["event_retire"])
        if age_h == 65: ev.append(t_internal["event_hmed"])
        if age_w == 65: ev.append(t_internal["event_wmed"])
        if age_h == rmd_age_h: ev.append(t_internal["event_hrmd"])
        if age_w == rmd_age_w: ev.append(t_internal["event_wrmd"])

        active_conversion = min(sim_roth_conv, cur_ira_h + cur_ira_w)
        stop_reason = ""
        
        if age_h >= sim_conv_stop_age or age_w >= sim_conv_stop_age:
            active_conversion = 0
            stop_reason = "Target Age Reached" if conv_stop_age_override else "RMD Start"
        elif (cur_ira_h + cur_ira_w) <= 1000 and sim_roth_conv > 0:
            active_conversion = 0
            stop_reason = "IRA Depleted"

        if active_conversion == 0 and not conversion_already_stopped and sim_roth_conv > 0:
            ev.append(f"{t_internal['event_roth_stop']} ({stop_reason})")
            conversion_already_stopped = True

        divisor_h = get_rmd_divisor(age_h)
        divisor_w = get_rmd_divisor(age_w)
        rmd_h = (cur_ira_h / divisor_h) if divisor_h > 0 else 0
        rmd_w = (cur_ira_w / divisor_w) if divisor_w > 0 else 0
        total_rmd = rmd_h + rmd_w
        salary = last_salary if year == retire_year else 0
        h_ss = (ss_h_monthly * 12 * inf_factor) if year >= actual_ss_h_start else 0
        w_ss = max((ss_w_monthly * 12 * inf_factor), (h_ss * 0.5)) if year >= actual_ss_w_start else 0
        total_ss = h_ss + w_ss
        
        qual_div = taxable_div_in * qd_perc
        ord_div = taxable_div_in * (1 - qd_perc)
        
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
        
        num_spouses_medicare = (1 if age_h >= 65 else 0) + (1 if age_w >= 65 else 0)
        irmaa_tier, irmaa_surcharge = get_irmaa_surcharge(magi, inf_factor, num_spouses_medicare)

        base_deduct = 32200 if tax_status == "MFJ" else 16100
        extra_deduct = 0
        if tax_status == "MFJ":
            if age_h >= 65: extra_deduct += 1650
            if age_w >= 65: extra_deduct += 1650
        else:
            if age_h >= 65: extra_deduct += 1950 
        
        deduct = (base_deduct + extra_deduct) * inf_factor
        ord_taxable = max(0, ordinary_gross - deduct)
        
        fed_tax = calculate_comprehensive_tax(ord_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, tax_status, i)
        
        target_expense = (annual_expense * inf_factor) + fed_tax + irmaa_surcharge       
        available_cash = total_ss + salary + taxable_div_in + sim_annual_ltcg + muni_int_in + total_rmd
        shortfall = max(0, target_expense - available_cash)
        
        if shortfall > (cur_brokerage + (cur_ira_h + cur_ira_w) + cur_roth) and not oom_triggered:
            ev.append(t_internal["event_oom"])
            oom_triggered = True

        from_broker = min(cur_brokerage, shortfall)
        cur_brokerage -= from_broker
        shortfall -= from_broker
        
        ira_withdrawn = 0
        if shortfall > 0 and (cur_ira_h + cur_ira_w) > 0:
            gross_needed = shortfall
            for _ in range(5):
                test_ord = ord_taxable + gross_needed
                test_magi = magi + gross_needed
                
                test_fed_tax = calculate_comprehensive_tax(test_ord, qd_ltcg_total, test_magi, inf_factor, taxable_ss, tax_status, i)
                _, test_irmaa_sur = get_irmaa_surcharge(test_magi, inf_factor, num_spouses_medicare)
                
                extra_tax = test_fed_tax - fed_tax
                extra_irmaa = test_irmaa_sur - irmaa_surcharge
                gross_needed = shortfall + extra_tax + extra_irmaa
                
                if gross_needed >= (cur_ira_h + cur_ira_w):
                    gross_needed = cur_ira_h + cur_ira_w
                    break
                    
            ira_withdrawn = gross_needed
            ord_taxable += ira_withdrawn
            magi += ira_withdrawn
            fed_tax = calculate_comprehensive_tax(ord_taxable, qd_ltcg_total, magi, inf_factor, taxable_ss, tax_status, i)
            irmaa_tier, irmaa_surcharge = get_irmaa_surcharge(magi, inf_factor, num_spouses_medicare)
            target_expense = (annual_expense * inf_factor) + fed_tax + irmaa_surcharge
            shortfall = max(0, target_expense - available_cash - from_broker - ira_withdrawn)

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
            "Brokerage": cur_brokerage, "Total Net Worth": cur_ira_h + cur_ira_w + cur_roth + cur_brokerage,
            "IRMAA": "✅ Safe" if irmaa_tier == 0 else f"🚩 Tier {irmaa_tier}",
            "🚨 Important Events": ", ".join(ev), "raw_roth_yield": yearly_roth_growth, "raw_rmd": total_rmd
        })
    return pd.DataFrame(rows)

# --- 5. UI DISPLAY ---
st.title(t["title"])
st.info(t["privacy_note"])

# Bundle all reactive inputs for structural mapping to cached calculator argument signature
core_args = {
    "ira_h_init": ira_h_init, "ira_w_init": ira_w_init, "roth_init": roth_init, "brokerage_init": brokerage_init,
    "retire_year": retire_year, "sim_years": sim_years, "h_age_at_retire": h_age_at_retire, "w_age_at_retire": w_age_at_retire,
    "tax_status": tax_status, "roth_conv": roth_conv, "annual_ltcg": annual_ltcg, "annual_expense": annual_expense, "qd_perc": qd_perc,
    "taxable_div_in": taxable_div_in, "muni_int_in": muni_int_in, "last_salary": last_salary,
    "ss_h_monthly": ss_h_monthly, "ss_h_start": ss_h_start, "ss_w_monthly": ss_w_monthly, "ss_w_start": ss_w_start,
    "ira_growth": ira_growth, "roth_growth": roth_growth, "broker_growth": broker_growth, "inflation_rate": inflation_rate,
    "lang": lang
}

tab_roadmap, tab_lab, tab_data = st.tabs([t["tab_roadmap"], t["tab_lab"], t["tab_data"]])

with tab_roadmap:
    st.subheader(t["motivation_h"])
    st.write(t["motivation_body"])

    st.subheader(t["meth_h"])
    st.markdown(t["meth_body"])

    st.subheader(t["use_h"])
    st.markdown(t["use_body"])

    df_baseline = calculate_roadmap(**core_args, conv_override=0, ltcg_override=0)
    df = calculate_roadmap(**core_args)

    st.subheader(t["comp_header"].format(sim_years=sim_years))
    st.write(t["comp_desc"].format(sim_years=sim_years))

    nw_base = df_baseline.iloc[-1]['Total Net Worth']
    nw_strat = df.iloc[-1]['Total Net Worth']
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
            tax_color = "#f39c12"  
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
        border_roth = "rgba(52, 152, 219, 0.3)" if roth_boost >= 0 else "rgba(231, 76, 60, 0.08)"
        st.markdown(f"""
        <div style="background-color: {bg_roth}; border: 1px solid {border_roth}; padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0; color: #888888; font-size: 0.9rem; font-weight: normal;">{t["kpi_roth_boost"]}</h4>
            <p style="margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold; color: {color_roth};">{sign_roth}${roth_boost:,.0f}</p>
            <span style="font-size: 0.8rem; color: #888888;">{t["kpi_baseline"]}: ${roth_base:,.0f} vs {t["kpi_strategy"]}: ${roth_strat:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- ACTIVE STRATEGY DETAILS ---
    st.subheader(t["kpi_h"].format(sim_years=sim_years))
    k0, k1, k2, k3, k4 = st.columns(5)
    k0.metric(t["kpi_init_nw"], f"${(ira_h_init + ira_w_init + roth_init + brokerage_init):,.0f}", help=t["kpi_cap_init"])
    k1.metric(t["kpi_nw"].format(sim_years=sim_years), f"${df.iloc[-1]['Total Net Worth']:,.0f}", help=t["kpi_cap_nw"].format(sim_years=sim_years))
    k2.metric(t["kpi_total_outflow"].format(sim_years=sim_years), f"${df['raw_outflow'].sum():,.0f}", help=t["kpi_cap_outflow"].format(sim_years=sim_years))
    k3.metric(t["kpi_tax"], f"${df['OUT: Fed Tax'].sum():,.0f}", help=t["kpi_cap_tax"].format(sim_years=sim_years))
    k4.metric(t["kpi_roth"], f"${df.iloc[-1]['Roth Bal']:,.0f}", help=t["kpi_cap_roth"])

    st.divider()
    st.subheader(f"{t['roadmap_h']} {retire_year}")
    col_map = {"INPUT: SS": t["col_ss"], "raw_div": t["col_div"], "raw_muni": t["col_muni"], "raw_cg": t["col_cg"], "LEVER: Roth": t["col_roth"], "OUT: MAGI": t["col_magi"], "OUT: Fed Tax": t["col_tax"], "raw_outflow": t["col_outflow"], "Total Net Worth": t["col_nw"], "🚨 Important Events": t["col_events"]}
    st.table(df[['Year', 'Ages', 'INPUT: SS', 'raw_div', 'raw_muni', 'raw_cg', 'LEVER: Roth', 'OUT: MAGI', 'OUT: Fed Tax', 'raw_outflow', 'Total Net Worth', 'IRMAA', '🚨 Important Events']].rename(columns=col_map).style.format({t["col_ss"]: "${:,.0f}", t["col_div"]: "${:,.0f}", t["col_muni"]: "${:,.0f}", t["col_cg"]: "${:,.0f}", t["col_roth"]: "${:,.0f}", t["col_magi"]: "${:,.0f}", t["col_tax"]: "${:,.0f}", t["col_outflow"]: "${:,.0f}", t["col_nw"]: "${:,.0f}"}))

    # Summary Table
    st.divider()
    st.subheader(t["summary_h"].format(sim_years=sim_years))
    total_tax = df["OUT: Fed Tax"].sum()
    total_taxable_yield = df["raw_div"].sum() + df["raw_cg"].sum() + df["raw_rmd"].sum()
    tax_per_dollar = total_tax / max(1, total_taxable_yield)

    summary_rows = [
        {"Type": t["acc_ira"], "Init": ira_h_init + ira_w_init, "Final": df.iloc[-1]['IRA Bal'], "Yield": df["raw_rmd"].sum(), "Liability": df["raw_rmd"].sum() * tax_per_dollar},
        {"Type": t["acc_roth"], "Init": roth_init, "Final": df.iloc[-1]['Roth Bal'], "Yield": df["raw_roth_yield"].sum(), "Liability": 0.0},
        {"Type": t["acc_broker"], "Init": brokerage_init, "Final": df.iloc[-1]['Brokerage'], "Yield": df["raw_div"].sum() + df["raw_cg"].sum() + df["raw_muni"].sum(), "Liability": (df["raw_div"].sum() + df["raw_cg"].sum()) * tax_per_dollar}
    ]
    df_sum_table = pd.DataFrame(summary_rows)
    totals_row = {"Type": t["total_label"], "Init": df_sum_table["Init"].sum(), "Final": df_sum_table["Final"].sum(), "Yield": df_sum_table["Yield"].sum(), "Liability": df_sum_table["Liability"].sum()}
    df_final_sum_display = pd.concat([df_sum_table, pd.DataFrame([totals_row])], ignore_index=True)

    yield_col = t["sum_yield"].format(sim_years=sim_years)
    tax_col = t["sum_liability"].format(sim_years=sim_years)
    
    df_final_sum_renamed = df_final_sum_display.rename(columns={"Type": "Account", "Init": t["sum_init"], "Final": t["sum_final"], "Yield": yield_col, "Liability": tax_col})
    st.table(df_final_sum_renamed.style.format({t["sum_init"]: "${:,.0f}", t["sum_final"]: "${:,.0f}", yield_col: "${:,.0f}", tax_col: "${:,.0f}"}))

with tab_lab:
    lab_horizon = max(sim_years, 30)
    st.subheader(t["lab_roth_h"])
    st.write(t["lab_roth_desc"].format(lab_horizon=lab_horizon))
    
    # Optimization parameters
    total_ira_init = ira_h_init + ira_w_init
    lab_upper_bound = min(200000, int((total_ira_init // 10000 + 1) * 10000))
    lab_upper_bound = max(10000, lab_upper_bound) 
    test_amounts = list(range(0, lab_upper_bound + 1, 10000))
    lab_results = []
    
    with st.spinner("Analyzing Roth efficiency..."):
        for amt in test_amounts:
            res_df_sim = calculate_roadmap(**core_args, conv_override=amt, horizon_override=lab_horizon)
            lab_results.append({
                "amt": amt,
                "nw": res_df_sim.iloc[-1]['Total Net Worth'],
                "tax": res_df_sim['OUT: Fed Tax'].sum()
            })
    
    res_df = pd.DataFrame(lab_results)
    
    # Pre-calculate optimum amount for drawing target indicators
    best_idx = res_df["nw"].idxmax()
    best_amt = res_df.loc[best_idx, "amt"]
    
    col_nw, col_tax = st.columns(2)
    with col_nw:
        st.write(f"**{t['lab_roth_chart_y']} (Objective)**")
        base_nw = alt.Chart(res_df).encode(
            x=alt.X('amt:Q', title=t["lab_roth_chart_x"]),
            y=alt.Y('nw:Q', title=t["lab_roth_chart_y"], scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('amt:Q', title=t["lab_roth_chart_x"], format='$,.0f'), alt.Tooltip('nw:Q', title=t["lab_roth_chart_y"], format='$,.0f')]
        )
        line_nw = base_nw.mark_line(color='#2ecc71', strokeWidth=3)
        rule_nw = alt.Chart(pd.DataFrame({'best_amt': [best_amt]})).mark_rule(
            color='#e74c3c', strokeDash=[4, 4], strokeWidth=2
        ).encode(x='best_amt:Q')
        st.altair_chart((line_nw + rule_nw).properties(height=300), width="stretch")
        
    with col_tax:
        st.write("**Cumulative Taxes Paid (Trade-off Cost)**")
        base_tax = alt.Chart(res_df).encode(
            x=alt.X('amt:Q', title=t["lab_roth_chart_x"]),
            y=alt.Y('tax:Q', title="Total Tax", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('amt:Q', title=t["lab_roth_chart_x"], format='$,.0f'), alt.Tooltip('tax:Q', title="Total Tax", format='$,.0f')]
        )
        line_tax = base_tax.mark_line(color='#3498db', strokeWidth=3)
        rule_tax = alt.Chart(pd.DataFrame({'best_amt': [best_amt]})).mark_rule(
            color='#e74c3c', strokeDash=[4, 4], strokeWidth=2
        ).encode(x='best_amt:Q')
        st.altair_chart((line_tax + rule_tax).properties(height=300), width="stretch")
    
    st.success(f"💡 **{t['lab_roth_optimum']} ${best_amt:,.0f}**")

    if best_amt > 0:
        st.divider()
        st.subheader(t["lab_stop_h"])
        st.write(t["lab_stop_desc"].format(best_amt=best_amt))
        
        by_h = 2026 - h_age_at_retire
        rmd_a_h = 75 if by_h >= 1960 else 73
        
        test_ages = list(range(h_age_at_retire, rmd_a_h + 1))
        if len(test_ages) > 1:
            stop_results = []
            with st.spinner("Analyzing conversion window..."):
                for sa in test_ages:
                    res_df_stop = calculate_roadmap(**core_args, conv_override=best_amt, horizon_override=lab_horizon, conv_stop_age_override=sa)
                    stop_results.append({"age": sa, "nw": res_df_stop.iloc[-1]['Total Net Worth']})
            
            stop_df = pd.DataFrame(stop_results)
            
            # Pre-calculate optimum stop age for drawing target indicator
            best_sa_idx = stop_df["nw"].idxmax()
            best_sa = stop_df.loc[best_sa_idx, "age"]
            
            base_stop = alt.Chart(stop_df).encode(
                x=alt.X('age:Q', title=t["lab_stop_chart_x"], axis=alt.Axis(format='d')),
                y=alt.Y('nw:Q', title=t["lab_roth_chart_y"], scale=alt.Scale(zero=False)),
                tooltip=[alt.Tooltip('age:Q', title=t["lab_stop_chart_x"]), alt.Tooltip('nw:Q', title=t["lab_roth_chart_y"], format='$,.0f')]
            )
            line_stop = base_stop.mark_line(color='#2ecc71', strokeWidth=3)
            rule_stop = alt.Chart(pd.DataFrame({'best_sa': [best_sa]})).mark_rule(
                color='#e74c3c', strokeDash=[4, 4], strokeWidth=2
            ).encode(x='best_sa:Q')
            st.altair_chart((line_stop + rule_stop).properties(height=300), width="stretch")
            
            st.success(f"💡 **{t['lab_stop_optimum']} {best_sa}**")

with tab_data:
    st.subheader(t["tab_data"])
    
    # Create the data payload matching current state settings
    current_profile = {
        "retire_year": retire_year,
        "sim_years": sim_years,
        "h_age_at_retire": h_age_at_retire,
        "w_age_at_retire": w_age_at_retire,
        "ira_h_init": ira_h_init,
        "ira_w_init": ira_w_init,
        "roth_init": roth_init,
        "brokerage_init": brokerage_init,
        "tax_status": tax_status,
        "roth_conv": roth_conv,
        "annual_ltcg": annual_ltcg,
        "annual_expense": annual_expense,
        "qd_perc_raw": qd_perc_raw,
        "taxable_div_in": taxable_div_in,
        "muni_int_in": muni_int_in,
        "last_salary": last_salary,
        "ss_h_monthly": ss_h_monthly,
        "ss_h_start": ss_h_start,
        "ss_w_monthly": ss_w_monthly,
        "ss_w_start": ss_w_start,
        "ira_growth_raw": ira_growth_raw,
        "roth_growth_raw": roth_growth_raw,
        "broker_growth_raw": broker_growth_raw,
        "inflation_rate_raw": inflation_rate_raw
    }
    
    json_string = json.dumps(current_profile, indent=4)
    
    col_save, col_load = st.columns(2)
    
    with col_save:
        st.write("### 💾 Export Profile")
        st.caption("Save your current retirement asset values and strategies to your computer.")
        st.download_button(
            label="📥 Download Profile (.json)",
            data=json_string,
            file_name="retirement_profile.json",
            mime="application/json"
        )
        
    with col_load:
        st.write("### 📂 Import Profile")
        st.caption("Upload a previously saved profile file to automatically populate all inputs.")
        uploaded_file = st.file_uploader("Choose a profile JSON file", type=["json"])
        
        if uploaded_file is not None:
            try:
                loaded_profile = json.load(uploaded_file)
                
                # Push values seamlessly into session state keys
                for key, value in loaded_profile.items():
                    st.session_state[key] = value
                
                st.success("✅ Profile loaded successfully! Refreshing components...")
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing profile file: {e}")