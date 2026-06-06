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
        "about_expander": "📖 About & How to Use",
        "motivation_h": "✍️ Motivation",
        "motivation_body": "This tool provides prospective retirees or current retirees with a tax strategy simulation and individualizes the various levers to convert to Roth; to realize capital gains; to test different growth scenarios. The goal is to achieve optimum total wealth, while minimizing the total federal tax paid in the horizon.",
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
* **Test Different Growth and Expense Scenarios:** Use the sidebar to test different growth assumptions, inflation rate and annual living expenses.
* **Explore Strategy Lab:** Navigate to the "Strategy Lab" tab to run automated sensitivity analyses that identify your mathematically optimal annual Roth conversion amount and window.
* **Observe Expected Net Worth:** Watch the comparison and roadmap to see how paying taxes early preserves long-term survival-weighted capital.
""",
        "kpi_h": "🚀 {sim_years}-Year Strategy vs. Baseline",
        "kpi_init_nw": "Initial Net Worth",
        "kpi_nw": "Weighted Expected NW",
        "kpi_tax": "Total Federal Tax Paid",
        "kpi_rmd": "Total RMD Amount",
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
        "col_rmd": "INPUT: RMDs",
        "col_outflow": "OUT: Total Outflow",
        "col_magi": "OUT: MAGI",
        "col_tax": "OUT: Fed Tax",
        "col_nw": "Total Net Worth",
        "col_ex_nw": "Expected Net Worth",
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
        "comp_desc": "Compares your active and optimal strategies against baseline (zero Roth conversions or capital gains harvesting)  over {sim_years} years. Success is measured by maximizing survival-weighted Expected Net Worth.",
        "kpi_nw_gain": "Expected Net Worth Gain (Mean)",
        "kpi_tax_saved": "Cumulative Taxes Saved",
        "kpi_tax_extra": "Upfront Tax Cost",
        "kpi_roth_boost": "Final Roth Reservoir Boost",
        "kpi_baseline": "Baseline",
        "kpi_strategy": "Strategy",
        "kpi_optimum": "Optimum",
        "tab_roadmap": "📈 Detailed Roadmap",
        "tab_lab": "🔬 Strategy Lab",
        "tab_data": "💾 Data Management",
        "lab_roth_h": "Roth Conversion Sensitivity Analysis",
        "lab_roth_desc": "Tests how much to convert from IRA to Roth each year. The peak of the curve is the sweet spot — pay manageable taxes now to avoid larger forced withdrawals later. ({lab_horizon}-year horizon, survival-weighted.)",
        "lab_roth_chart_x": "Annual Conversion Amount",
        "lab_roth_chart_y": "Final Net Worth",
        "lab_roth_optimum": "Based on the simulation, the optimum annual Roth conversion amount is approximately",
        "lab_stop_h": "Roth Window Optimizer (Stop Age)",
        "lab_stop_desc": "Using the optimal amount (${best_amt:,.0f}/yr), finds the best age to stop converting. Usually best to keep going until RMDs force you to stop.",
        "lab_stop_chart_x": "Stop Age",
        "lab_stop_optimum": "The optimum age to stop Roth conversions is",
        "lab_pref_h": "⚙️ Optimization Preferences",
        "lab_pref_label": "Optimize for: Spending Now ← → Leaving More Later",
        "lab_pref_help": "Slide left to prioritize having more cash available in early retirement. Slide right to prioritize maximizing what you leave behind. Middle balances both.",
        "lab_pref_early": "Current Goal: Prioritizing **Early Retirement Liquidity**.",
        "lab_pref_late": "Current Goal: Prioritizing **Long-Term Legacy & Security**.",
        "lab_pref_balanced": "Current Goal: **Balanced approach**.",
        "lab_irmaa_label": "Max Medicare Surcharge Allowed",
        "lab_irmaa_help": "Limits how much extra Medicare premium you're willing to pay. 0 = no extra cost. Higher = allows more aggressive conversions that trigger surcharges."
    },
    "Chinese": {
        "title": "🛡️ 综合退休财富与税务优化工具",
        "privacy_note": "🔒 隐私与数据安全提示：本程序完全在您的本地浏览器会话中运行。任何用户数据、资产数值或个人税务信息均不会被收集、追踪或存储在任何外部服务器上。您的财务信息将完全保持私密。",
        "about_expander": "📖 工具介绍与使用说明",
        "motivation_h": "✍️ 建立初衷",
        "motivation_body": "本工具为准退休人员或已退休人员提供税务策略模拟。通过量化 Roth 转换、资本利得变现及不同增长场景等杠杆，目标是实现最优的总财富，同时最小化未来预见的联邦税总支出。",
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
* **探索策略实验室:** 导航到“策略实验室”选项卡，运行自动化敏感性分析，找出数学上最优的年度 Roth 转换金额和时间窗口。
* **观察预期净资产 (Expected Net Worth):** 关注路线图和对比，观察通过早期纳税如何保护长期的生存加权资本。
""",
        "kpi_h": "🚀 {sim_years}年策略 vs. 基准对比",
        "kpi_init_nw": "初始净资产", 
        "kpi_nw": "加权预期净资产",
        "kpi_tax": "联邦税总支出",
        "kpi_rmd": "最低强制提款(RMD)总额",
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
        "sidebar_cash": "💵 现金流、收益与支出",
        "sidebar_ss": "📈 社会安全金",
        "sidebar_levers": "🎚️ 策略杠杆",
        "filing_status": "报税状态",
        "qd_ratio": "符合条件的股息比例 (Qualified %)",
        "col_ss": "社保收入",
        "col_roth": "Roth转换",
        "col_div": "应税股息",
        "col_muni": "免税利息(Muni)",
        "col_cg": "资本利得",
        "col_rmd": "强制提款(RMD)",
        "col_outflow": "总支出(含税)",
        "col_magi": "MAGI(医保判定)",
        "col_tax": "联邦税支出",
        "col_nw": "总净资产",
        "col_ex_nw": "预期净资产",
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
        "comp_desc": "在{sim_years}年周期内，将您的主动策略与最佳路径，同基准线（零罗斯转换或资本利得变现）进行对比。成功标准为最大化生存加权预期净值。",
        "kpi_nw_gain": "预期净资产提升 (平均)",
        "kpi_tax_saved": "累计节省税款",
        "kpi_tax_extra": "前期税务成本",
        "kpi_roth_boost": "免税 Roth 账户增幅",
        "kpi_baseline": "基准方案",
        "kpi_strategy": "优化策略",
        "kpi_optimum": "最优方案",
        "tab_roadmap": "📈 详细路线图",
        "tab_lab": "🔬 策略实验室",
        "tab_data": "💾 数据管理",
        "lab_roth_h": "Roth 转换敏感性分析",
        "lab_roth_desc": "测试每年从 IRA 转入 Roth 的最佳金额。曲线峰值即最优解——现在交适量的税，避免未来更大的强制提款税负。（{lab_horizon}年周期，生存加权。）",
        "lab_roth_chart_x": "年度转换金额",
        "lab_roth_chart_y": "最终总净资产",
        "lab_roth_optimum": "根据模拟，最佳年度 Roth 转换金额约为",
        "lab_stop_h": "Roth 转换周期（停止年龄）优化",
        "lab_stop_desc": "使用最佳金额 (${best_amt:,.0f}/年)，找出最佳停止转换年龄。通常持续转换到 RMD 开始前效果最优。",
        "lab_stop_chart_x": "停止年龄",
        "lab_stop_optimum": "最佳停止 Roth 转换的年龄是",
        "lab_pref_h": "⚙️ 优化偏好设置",
        "lab_pref_label": "优化目标：当前消费 ← → 长期传承",
        "lab_pref_help": "左滑侧重早期退休时有更多可用现金。右滑侧重最大化留给后人的资产。中间为两者平衡。",
        "lab_pref_early": "当前目标：优先考虑 **早期退休流动性**。",
        "lab_pref_late": "当前目标：优先考虑 **长期传承与财务安全**。",
        "lab_pref_balanced": "当前目标：**平衡方案**。",
        "lab_irmaa_label": "允许的最大 Medicare 附加费",
        "lab_irmaa_help": "限制您愿意承受的额外 Medicare 保费。0 = 无额外费用。越高 = 允许更激进的转换（会触发附加费）。"
    }
}

# --- 2. SIDEBAR INPUTS ---
with st.sidebar:
    lang = st.radio("Language / 语言选择", ["English", "Chinese"], horizontal=True)
    t = LANG_MAP[lang]

    st.header(t["sidebar_levers"])
    status_options = ["MFJ", "Single", "MFS"]
    saved_status = st.session_state.get("tax_status", "MFJ")
    status_idx = status_options.index(saved_status) if saved_status in status_options else 0
    tax_status = st.selectbox(t["filing_status"], status_options, index=status_idx)
    sim_years = st.slider("Simulation Horizon (Years)", 20, 40, value=int(st.session_state.get("sim_years", 20)))
    roth_conv = st.slider("Annual Roth Conversion ($)", 0, 200000, value=int(st.session_state.get("roth_conv", 40000)), step=5000)
    annual_ltcg = st.slider("Annual Cap Gains Realized ($)", 0, 1000000, value=int(st.session_state.get("annual_ltcg", 20000)), step=10000)

    st.header(t["sidebar_cash"])
    annual_expense = st.number_input("Annual Living Expense (Today's $)", value=int(st.session_state.get("annual_expense", 100000)))
    qd_perc_raw = st.slider(t["qd_ratio"], 0, 100, value=int(st.session_state.get("qd_perc_raw", 80)))
    qd_perc = qd_perc_raw / 100
    taxable_div_in = st.number_input("Annual Taxable Dividends", value=int(st.session_state.get("taxable_div_in", 33000)))
    muni_int_in = st.number_input("Annual Tax-Free Muni Interest", value=int(st.session_state.get("muni_int_in", 37000)))
    last_salary = st.number_input("Final Salary (Retirement Year)", value=int(st.session_state.get("last_salary", 0)))

    with st.expander(t["sidebar_timeline"], expanded=False):
        retire_year = st.number_input("Full Retirement Year", value=int(st.session_state.get("retire_year", 2026)))
        h_age_at_retire = st.number_input(f"Husband Age in {retire_year}", value=int(st.session_state.get("h_age_at_retire", 64)))
        w_age_at_retire = st.number_input(f"Wife Age in {retire_year}", value=int(st.session_state.get("w_age_at_retire", 64)))

    with st.expander(t["sidebar_assets"], expanded=False):
        ira_h_init = st.number_input("Husband IRA Balance ($)", value=int(st.session_state.get("ira_h_init", 1500000)))
        ira_w_init = st.number_input("Wife IRA Balance ($)", value=int(st.session_state.get("ira_w_init", 10000)))
        roth_init = st.number_input("Roth IRA Balance ($)", value=int(st.session_state.get("roth_init", 100000)))
        brokerage_init = st.number_input("Taxable Brokerage Balance ($)", value=int(st.session_state.get("brokerage_init", 1000000)))

    with st.expander(t["sidebar_ss"], expanded=False):
        ss_h_monthly = st.number_input("H Monthly SS ($)", value=int(st.session_state.get("ss_h_monthly", 4000)))
        ss_h_start = st.number_input("H Start Year", value=int(st.session_state.get("ss_h_start", 2029)))
        ss_w_monthly = st.number_input("W Monthly SS ($)", value=int(st.session_state.get("ss_w_monthly", 3000)))
        ss_w_start = st.number_input("W Start Year", value=int(st.session_state.get("ss_w_start", 2029)))

    with st.expander(t["sidebar_growth"], expanded=False):
        ira_growth_raw = st.slider("IRA Growth Rate (%)", 1.0, 10.0, value=float(st.session_state.get("ira_growth_raw", 4.0)))
        ira_growth = ira_growth_raw / 100
        roth_growth_raw = st.slider("Roth Growth Rate (%)", 1.0, 10.0, value=float(st.session_state.get("roth_growth_raw", 5.0)))
        roth_growth = roth_growth_raw / 100
        broker_growth_raw = st.slider("Brokerage Growth Rate (%)", 1.0, 10.0, value=float(st.session_state.get("broker_growth_raw", 3.0)))
        broker_growth = broker_growth_raw / 100
        inflation_rate_raw = st.slider("Inflation Rate (%)", 0.0, 5.0, value=float(st.session_state.get("inflation_rate_raw", 2.5)))
        inflation_rate = inflation_rate_raw / 100

    st.sidebar.markdown("<br>" * 10, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # 2. Display the Copyright Notice
    st.sidebar.caption("© 2026 G. Shao (github gjshao44). All rights reserved.")

    # 3. Add scannable links to your policy files
    # Note: If hosting publicly, replace these names with your live GitHub or website URLs
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; opacity: 0.7;">
            <a href="https://github.com/gjshao44/Tax-Strategies/blob/main/TERMS.md" target="_blank" style="color: inherit; text-decoration: none; margin-right: 10px;">Terms of Service</a> | 
            <a href="https://github.com/gjshao44/Tax-Strategies/blob/main/PRIVACY.md" target="_blank" style="color: inherit; text-decoration: none; margin-left: 10px;">Privacy Policy</a>
        </div>
        """,
        unsafe_allow_html=True
)
# --- 3. CORE CALCULATORS ---
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

def get_survival_prob(age):
    # Simplified lookup based on actuarial trends (prob of survival for one individual)
    # Returns 1.0 until age 65, then declines
    if age < 65: return 1.0
    if age >= 100: return 0.05
    # Approximate mortality curve (roughly 1% drop per year starting at 65)
    return max(0.05, 1.0 - (age - 65) * 0.02)

# --- 4. CALCULATION ENGINE ---
@st.cache_data
def get_optimal_conversion(core_args, lab_horizon, legacy_weight, max_irmaa_limit=5):
    mid_weight = 1.0 - legacy_weight
    total_ira_init = core_args["ira_h_init"] + core_args["ira_w_init"]
    
    # Dynamically scale upper bound based on IRA size
    upper_bound = min(500000, max(200000, int((total_ira_init * 0.1) // 10000 * 10000)))
    upper_bound = min(upper_bound, total_ira_init)
    upper_bound = max(10000, int(upper_bound // 10000 * 10000))
    
    test_amounts = list(range(0, upper_bound + 1, 10000))
    
    best_score = -1e18
    best_amt = 0
    mid_idx = int(lab_horizon * 0.33)
    end_idx = int(lab_horizon * 0.95)
    
    for amt in test_amounts:
        df_sim = calculate_roadmap(**core_args, conv_override=amt, horizon_override=lab_horizon)
        score = (df_sim.iloc[mid_idx]['Expected Net Worth'] * mid_weight) + (df_sim.iloc[end_idx]['Expected Net Worth'] * legacy_weight)
        
        # Apply IRMAA constraint penalty
        max_tier_reached = df_sim['irmaa_tier'].max()
        penalty = 1e15 * max(0, max_tier_reached - max_irmaa_limit)
        score -= penalty
        
        if score > best_score:
            best_score = score
            best_amt = amt
    return best_amt

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
        
        # Survival Probabilities
        prob_h = get_survival_prob(age_h)
        prob_w = get_survival_prob(age_w)
        joint_survival = 1 - ((1 - prob_h) * (1 - prob_w))

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

        # Save surplus cash to the Brokerage account
        surplus = max(0, available_cash - target_expense)
        cur_brokerage += surplus

        # Deduct RMDs and other withdrawals from the Traditional IRA
        ira_total = cur_ira_h + cur_ira_w
        amt_to_deduct = total_rmd + ira_withdrawn + active_conversion
        if amt_to_deduct > ira_total:
            amt_to_deduct = ira_total
            
        if ira_total > 0:
            h_ratio = cur_ira_h / ira_total
            w_ratio = cur_ira_w / ira_total
            cur_ira_h -= h_ratio * amt_to_deduct
            cur_ira_w -= w_ratio * amt_to_deduct
        
        cur_ira_h = max(0, cur_ira_h) * (1 + ira_growth)
        cur_ira_w = max(0, cur_ira_w) * (1 + ira_growth)
        yearly_roth_growth = cur_roth * roth_growth
        cur_roth = (cur_roth + active_conversion + yearly_roth_growth)
        cur_brokerage *= (1 + broker_growth)
        
        total_nw = cur_ira_h + cur_ira_w + cur_roth + cur_brokerage
        
        rows.append({
            "Year": year, "Ages": f"{age_h}/{age_w}", "INPUT: SS": total_ss, 
            "raw_div": taxable_div_in, "raw_muni": muni_int_in, "raw_cg": sim_annual_ltcg,
            "LEVER: Roth": active_conversion, "INPUT: RMDs": total_rmd, "OUT: MAGI": magi, "OUT: Fed Tax": fed_tax,
            "raw_outflow": target_expense, "Roth Bal": cur_roth, "IRA Bal": cur_ira_h + cur_ira_w, 
            "Brokerage": cur_brokerage, "Total Net Worth": total_nw,
            "Expected Net Worth": total_nw * joint_survival,
            "IRMAA": "✅ Safe" if irmaa_tier == 0 else f"🚩 Tier {irmaa_tier}",
            "irmaa_tier": irmaa_tier,
            "🚨 Important Events": ", ".join(ev), "raw_roth_yield": yearly_roth_growth, "raw_rmd": total_rmd
        })
    return pd.DataFrame(rows)

# --- 5. UI DISPLAY ---
st.title(t["title"])
st.info(t["privacy_note"])

core_args = {
    "ira_h_init": ira_h_init, "ira_w_init": ira_w_init, "roth_init": roth_init, "brokerage_init": brokerage_init,
    "retire_year": retire_year, "sim_years": sim_years, "h_age_at_retire": h_age_at_retire, "w_age_at_retire": w_age_at_retire,
    "tax_status": tax_status, "roth_conv": roth_conv, "annual_ltcg": annual_ltcg, "annual_expense": annual_expense, "qd_perc": qd_perc,
    "taxable_div_in": taxable_div_in, "muni_int_in": muni_int_in, "last_salary": last_salary,
    "ss_h_monthly": ss_h_monthly, "ss_h_start": ss_h_start, "ss_w_monthly": ss_w_monthly, "ss_w_start": ss_w_start,
    "ira_growth": ira_growth, "roth_growth": roth_growth, "broker_growth": broker_growth, "inflation_rate": inflation_rate,
    "lang": lang
}

lab_horizon = max(20, sim_years)
legacy_weight_val = st.session_state.get("lab_legacy_weight", 0.80)
max_irmaa_limit_val = st.session_state.get("lab_max_irmaa", 5)
best_amt_for_calc = get_optimal_conversion(core_args, lab_horizon, legacy_weight_val, max_irmaa_limit_val)
st.session_state['best_amt'] = best_amt_for_calc

tab_roadmap, tab_lab, tab_data = st.tabs([t["tab_roadmap"], t["tab_lab"], t["tab_data"]])

with tab_roadmap:
    with st.expander("📖 " + t["motivation_h"] + " & " + t["meth_h"], expanded=False):
        st.subheader(t["motivation_h"])
        st.write(t["motivation_body"])

        st.subheader(t["meth_h"])
        st.markdown(t["meth_body"])

        st.subheader(t["use_h"])
        st.markdown(t["use_body"])
        

    # --- 1. CALCULATE THREE SCENARIOS ---
    df_baseline = calculate_roadmap(**core_args, conv_override=0, ltcg_override=0)
    df_active = calculate_roadmap(**core_args) # Uses your sidebar settings

    # Retrieve the Optimum from the Lab
    df_optimal = calculate_roadmap(**core_args, conv_override=best_amt_for_calc)

    # --- 2. EXTRACT METRICS ---
    mid_idx = int(sim_years * 0.33)
    end_idx = int(sim_years * 0.95)
    mid_w = 1.0 - legacy_weight_val
    end_w = legacy_weight_val

    def _weighted_score(df):
        return df.iloc[mid_idx]['Expected Net Worth'] * mid_w + df.iloc[end_idx]['Expected Net Worth'] * end_w

    nw_base, nw_strat, nw_opt = _weighted_score(df_baseline), _weighted_score(df_active), _weighted_score(df_optimal)
    tax_base, tax_strat, tax_opt = df_baseline['OUT: Fed Tax'].sum(), df_active['OUT: Fed Tax'].sum(), df_optimal['OUT: Fed Tax'].sum()
    roth_base, roth_strat, roth_opt = df_baseline.iloc[-1]['Roth Bal'], df_active.iloc[-1]['Roth Bal'], df_optimal.iloc[-1]['Roth Bal']

    # --- 3. UNIFIED KPI DASHBOARD ---
    st.subheader(t["kpi_h"].format(sim_years=sim_years))
    st.caption(t["comp_desc"].format(sim_years=sim_years))
    init_nw = ira_h_init + ira_w_init + roth_init + brokerage_init
    total_outflow = df_active['raw_outflow'].sum()
    total_rmd = df_active['INPUT: RMDs'].sum()

    def _kpi_card(label, value, color, comparison=None):
        comp_html = ""
        if comparison:
            comp_html = f'<span style="font-size: 0.75rem; color: #888888;">{comparison}</span>'
        return f"""
        <div style="background-color: rgba({color}, 0.08); border: 1px solid rgba({color}, 0.3); padding: 12px 8px; border-radius: 8px; text-align: center; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <h4 style="margin: 0; color: #888888; font-size: 0.8rem; font-weight: normal;">{label}</h4>
            <p style="margin: 4px 0 2px 0; font-size: 1.4rem; font-weight: bold; color: rgba({color}, 1);">{value}</p>
            {comp_html}
        </div>
        """

    ira_pct = (ira_h_init + ira_w_init) / max(1, init_nw) * 100
    roth_pct = roth_init / max(1, init_nw) * 100
    broker_pct = brokerage_init / max(1, init_nw) * 100
    total_living = df_active['raw_outflow'].sum() - df_active['OUT: Fed Tax'].sum()
    total_tax_paid = df_active['OUT: Fed Tax'].sum()
    rmd_pct_of_ira = total_rmd / max(1, ira_h_init + ira_w_init) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(_kpi_card(t["kpi_init_nw"], f"${init_nw:,.0f}", "155, 89, 182",
            f"IRA {ira_pct:.0f}% | Roth {roth_pct:.0f}% | Taxable {broker_pct:.0f}%"), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card(t["kpi_nw"], f"${nw_strat:,.0f}", "46, 204, 113",
            f"Base: ${nw_base:,.0f} | Opt: ${nw_opt:,.0f}"), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_card(t["kpi_total_outflow"].format(sim_years=sim_years), f"${total_outflow:,.0f}", "149, 165, 166",
            f"Living: ${total_living:,.0f} | Tax: ${total_tax_paid:,.0f}"), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi_card(t["kpi_tax"], f"${tax_strat:,.0f}", "243, 156, 18",
            f"Base: ${tax_base:,.0f} | Opt: ${tax_opt:,.0f}"), unsafe_allow_html=True)
    with c5:
        st.markdown(_kpi_card(t["kpi_rmd"], f"${total_rmd:,.0f}", "230, 126, 34",
            f"{rmd_pct_of_ira:.0f}% of initial IRA balance"), unsafe_allow_html=True)
    with c6:
        st.markdown(_kpi_card(t["kpi_roth"], f"${roth_strat:,.0f}", "52, 152, 219",
            f"Base: ${roth_base:,.0f} | Opt: ${roth_opt:,.0f}"), unsafe_allow_html=True)

    # --- SUMMARY TABLE ---
    st.divider()
    st.subheader(t["summary_h"].format(sim_years=sim_years))
    total_tax = df_active["OUT: Fed Tax"].sum()
    total_taxable_yield = df_active["raw_div"].sum() + df_active["raw_cg"].sum() + df_active["raw_rmd"].sum()
    tax_per_dollar = total_tax / max(1, total_taxable_yield)

    summary_rows = [
        {"Type": t["acc_ira"], "Init": ira_h_init + ira_w_init, "Final": df_active.iloc[-1]['IRA Bal'], "Yield": df_active["raw_rmd"].sum(), "Liability": df_active["raw_rmd"].sum() * tax_per_dollar},
        {"Type": t["acc_roth"], "Init": roth_init, "Final": df_active.iloc[-1]['Roth Bal'], "Yield": df_active["raw_roth_yield"].sum(), "Liability": 0.0},
        {"Type": t["acc_broker"], "Init": brokerage_init, "Final": df_active.iloc[-1]['Brokerage'], "Yield": df_active["raw_div"].sum() + df_active["raw_cg"].sum() + df_active["raw_muni"].sum(), "Liability": (df_active["raw_div"].sum() + df_active["raw_cg"].sum()) * tax_per_dollar}
    ]
    df_sum_table = pd.DataFrame(summary_rows)
    totals_row = {"Type": t["total_label"], "Init": df_sum_table["Init"].sum(), "Final": df_sum_table["Final"].sum(), "Yield": df_sum_table["Yield"].sum(), "Liability": df_sum_table["Liability"].sum()}
    df_final_sum_display = pd.concat([df_sum_table, pd.DataFrame([totals_row])], ignore_index=True)

    yield_col = t["sum_yield"].format(sim_years=sim_years)
    tax_col = t["sum_liability"].format(sim_years=sim_years)

    df_final_sum_renamed = df_final_sum_display.rename(columns={"Type": "Account", "Init": t["sum_init"], "Final": t["sum_final"], "Yield": yield_col, "Liability": tax_col})
    st.table(df_final_sum_renamed.style.format({t["sum_init"]: "${:,.0f}", t["sum_final"]: "${:,.0f}", yield_col: "${:,.0f}", tax_col: "${:,.0f}"}))

    # --- YEAR-BY-YEAR ROADMAP (expandable) ---
    st.subheader(f"📋 {t['roadmap_h']} {retire_year}")
    with st.expander("Click to expand year-by-year detail", expanded=False):
        show_all_cols = st.checkbox("Show all columns", value=False, key="roadmap_all_cols")

        col_map = {
            "INPUT: SS": t["col_ss"], "raw_div": t["col_div"], "raw_muni": t["col_muni"],
            "raw_cg": t["col_cg"], "LEVER: Roth": t["col_roth"], "INPUT: RMDs": t["col_rmd"], "OUT: MAGI": t["col_magi"],
            "OUT: Fed Tax": t["col_tax"], "raw_outflow": t["col_outflow"],
            "Total Net Worth": t["col_nw"], "Expected Net Worth": t["col_ex_nw"],
            "🚨 Important Events": t["col_events"]
        }

        if show_all_cols:
            display_cols = ['Year', 'Ages', 'INPUT: SS', 'raw_div', 'raw_muni', 'raw_cg', 'LEVER: Roth', 'INPUT: RMDs', 'OUT: MAGI', 'OUT: Fed Tax', 'raw_outflow', 'Total Net Worth', 'Expected Net Worth', 'IRMAA', '🚨 Important Events']
            fmt = {t["col_ss"]: "${:,.0f}", t["col_div"]: "${:,.0f}", t["col_muni"]: "${:,.0f}", t["col_cg"]: "${:,.0f}", t["col_roth"]: "${:,.0f}", t["col_rmd"]: "${:,.0f}", t["col_magi"]: "${:,.0f}", t["col_tax"]: "${:,.0f}", t["col_outflow"]: "${:,.0f}", t["col_nw"]: "${:,.0f}", t["col_ex_nw"]: "${:,.0f}"}
        else:
            display_cols = ['Year', 'Ages', 'LEVER: Roth', 'INPUT: RMDs', 'OUT: Fed Tax', 'raw_outflow', 'Expected Net Worth', 'IRMAA', '🚨 Important Events']
            fmt = {t["col_roth"]: "${:,.0f}", t["col_rmd"]: "${:,.0f}", t["col_tax"]: "${:,.0f}", t["col_outflow"]: "${:,.0f}", t["col_ex_nw"]: "${:,.0f}"}

        st.table(df_active[display_cols].rename(columns=col_map).style.format(fmt))

with tab_lab:
    # 1. Enforce a minimum of 20 years for the Strategy Lab to allow the algorithm sufficient runway,
    # otherwise follow the user's simulation horizon.
    st.subheader(t["lab_pref_h"])
    col_pref1, col_pref2 = st.columns(2)
    with col_pref1:
        legacy_weight = st.slider(
            t["lab_pref_label"],
            min_value=0.0,
            max_value=1.0,
            value=0.80,
            step=0.05,
            help=t["lab_pref_help"],
            key="lab_legacy_weight"
        )
        if legacy_weight < 0.3:
            st.caption("← Prioritizing **spending power now**")
        elif legacy_weight > 0.7:
            st.caption("→ Prioritizing **leaving more later**")
        else:
            st.caption("↔ Balanced between spending now and leaving later")
    with col_pref2:
        irmaa_monthly = {0: "$0", 1: "$80", 2: "$200", 3: "$320", 4: "$440", 5: "$480+"}
        max_irmaa_limit = st.slider(
            t["lab_irmaa_label"],
            min_value=0,
            max_value=5,
            value=5,
            step=1,
            help=t["lab_irmaa_help"],
            key="lab_max_irmaa"
        )
        surcharge_str = irmaa_monthly[max_irmaa_limit]
        if max_irmaa_limit == 0:
            st.caption(f"Max Medicare surcharge: **{surcharge_str}/mo per person** (no extra cost)")
        elif max_irmaa_limit == 5:
            st.caption(f"Max Medicare surcharge: **no limit** (all tiers allowed)")
        else:
            st.caption(f"Max Medicare surcharge: **{surcharge_str}/mo per person**")
    mid_weight = 1.0 - legacy_weight
    st.divider()
    
    st.subheader(t["lab_roth_h"], help=t["lab_roth_desc"].format(lab_horizon=lab_horizon))
    
    total_ira_init = ira_h_init + ira_w_init
    # Dynamically scale upper bound based on IRA size
    lab_upper_bound = min(500000, max(200000, int((total_ira_init * 0.1) // 10000 * 10000)))
    lab_upper_bound = min(lab_upper_bound, total_ira_init)
    lab_upper_bound = max(10000, int(lab_upper_bound // 10000 * 10000))
    
    test_amounts = list(range(0, lab_upper_bound + 1, 10000))
    lab_results = []
    
    mid_idx = int(lab_horizon * 0.33)
    end_idx = int(lab_horizon * 0.95)
    
    with st.spinner(f"Analyzing Roth Conversion amounts over {lab_horizon} years..."):
        for amt in test_amounts:
            res_df_sim = calculate_roadmap(**core_args, conv_override=amt, horizon_override=lab_horizon)
            
            mid_nw = res_df_sim.iloc[mid_idx]['Expected Net Worth']
            end_nw = res_df_sim.iloc[end_idx]['Expected Net Worth']
            weighted_score = (mid_nw * mid_weight) + (end_nw * legacy_weight)
            
            max_tier_reached = res_df_sim['irmaa_tier'].max()
            penalty = 1e15 * max(0, max_tier_reached - max_irmaa_limit)
            score = weighted_score - penalty
            
            lab_results.append({
                "amt": amt,
                "ex_nw": score,
                "raw_nw": weighted_score,
                "mid_nw": mid_nw,
                "end_nw": end_nw,
                "max_irmaa": max_tier_reached
            })
    
    res_df = pd.DataFrame(lab_results)
    best_amt = res_df.loc[res_df["ex_nw"].idxmax(), "amt"]
    best_row = res_df.loc[res_df["ex_nw"].idxmax()]
    
    # Chart 1: Roth Conversion with continuous line + colored points
    line = alt.Chart(res_df).mark_line(color='#bdc3c7', strokeWidth=3).encode(
        x=alt.X('amt:Q', title=t["lab_roth_chart_x"]),
        y=alt.Y('raw_nw:Q', title="Weighted Expected Net Worth ($)", scale=alt.Scale(zero=False))
    )
    points = alt.Chart(res_df).mark_point(size=60, filled=True).encode(
        x=alt.X('amt:Q'),
        y=alt.Y('raw_nw:Q'),
        color=alt.condition(
            f"datum.max_irmaa <= {max_irmaa_limit}",
            alt.value('#2ecc71'),  # Green if within limit
            alt.value('#e74c3c')   # Red if violating
        ),
        tooltip=[
            alt.Tooltip('amt:Q', title=t["lab_roth_chart_x"]),
            alt.Tooltip('raw_nw:Q', title="Expected Net Worth", format="$,.0f"),
            alt.Tooltip('max_irmaa:N', title="Max IRMAA Tier")
        ]
    )
    rule1 = alt.Chart(pd.DataFrame({'amt': [best_amt]})).mark_rule(color='red', strokeDash=[5,5]).encode(x='amt:Q')
    st.altair_chart(line + points + rule1, width='stretch')
    st.caption("🟢 Green = within Medicare surcharge limit | 🔴 Red = exceeds limit | ┆ Dashed line = optimum")
    st.success(f"💡 **{t['lab_roth_optimum']} ${best_amt:,.0f}**")
    
    c1, c2 = st.columns(2)
    c1.metric(f"🎯 Liquidity Milestone (Year {mid_idx})", f"${best_row['mid_nw']:,.0f}")
    c2.metric(f"🛡️ Legacy Security (Year {end_idx})", f"${best_row['end_nw']:,.0f}")

    st.divider()

    # Chart 2: Stop Age Optimizer
    st.subheader(t["lab_stop_h"], help=t["lab_stop_desc"].format(best_amt=best_amt))
    
    # We maintain a sensible range for age optimization regardless of horizon
    test_ages = list(range(65, 95))
    age_results = []
    
    with st.spinner("Optimizing Stop Age..."):
        for age in test_ages:
            res_age_df = calculate_roadmap(**core_args, conv_override=best_amt, conv_stop_age_override=age, horizon_override=lab_horizon)
            
            mid_nw = res_age_df.iloc[mid_idx]['Expected Net Worth']
            end_nw = res_age_df.iloc[end_idx]['Expected Net Worth']
            weighted_score = (mid_nw * 0.2) + (end_nw * 0.8)
            
            max_tier_reached = res_age_df['irmaa_tier'].max()
            penalty = 1e15 * max(0, max_tier_reached - max_irmaa_limit)
            score = weighted_score - penalty
            
            age_results.append({
                "age": age,
                "ex_nw": score,
                "raw_nw": weighted_score,
                "max_irmaa": max_tier_reached
            })
            
    res_age_df = pd.DataFrame(age_results)
    best_age = res_age_df.loc[res_age_df["ex_nw"].idxmax(), "age"]
    
    line2 = alt.Chart(res_age_df).mark_line(color='#bdc3c7', strokeWidth=3).encode(
        x=alt.X('age:Q', title=t["lab_stop_chart_x"], scale=alt.Scale(zero=False)),
        y=alt.Y('raw_nw:Q', title="Weighted Expected Net Worth ($)", scale=alt.Scale(zero=False))
    )
    points2 = alt.Chart(res_age_df).mark_point(size=60, filled=True).encode(
        x=alt.X('age:Q'),
        y=alt.Y('raw_nw:Q'),
        color=alt.condition(
            f"datum.max_irmaa <= {max_irmaa_limit}",
            alt.value('#3498db'),  # Blue if within limit
            alt.value('#e74c3c')   # Red if violating
        ),
        tooltip=[
            alt.Tooltip('age:Q', title=t["lab_stop_chart_x"]),
            alt.Tooltip('raw_nw:Q', title="Expected Net Worth", format="$,.0f"),
            alt.Tooltip('max_irmaa:N', title="Max IRMAA Tier")
        ]
    )
    rule2 = alt.Chart(pd.DataFrame({'age': [best_age]})).mark_rule(color='red', strokeDash=[5,5]).encode(x='age:Q')
    st.altair_chart(line2 + points2 + rule2, width='stretch')
    st.caption("🔵 Blue = within Medicare surcharge limit | 🔴 Red = exceeds limit | ┆ Dashed line = optimum")
    st.warning(f"🛑 **{t['lab_stop_optimum']} {best_age}**")

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
        "inflation_rate_raw": inflation_rate_raw,
        "lab_legacy_weight": legacy_weight_val,
        "lab_max_irmaa": max_irmaa_limit_val
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
                for key, value in loaded_profile.items():
                    st.session_state[key] = value
                # Add a brief success message, then immediately trigger a rerun
                st.success("✅ Profile loaded successfully! Refreshing...")
                st.rerun()  # <--- This forces Streamlit to restart top-to-bottom with the new state            
            except Exception as e:
                st.error(f"Error parsing profile file: {e}")