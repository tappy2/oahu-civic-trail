import streamlit as st
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Oahu Civic Trail - Oregon Trail Edition",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM HIGH-CONTRAST LIGHT / RETRO STYLING ---
st.markdown("""
<style>
    /* High contrast cream & dark navy palette for Oregon Trail feel */
    .stApp {
        background-color: #FBF9F1;
        color: #1A1C20;
        font-family: 'Courier New', Courier, monospace, monospace;
    }
    
    /* Text overrides for readability */
    h1, h2, h3, h4, h5, h6, p, div, label, span {
        color: #1A1C20 !important;
    }
    
    /* Card Container */
    .trail-card {
        background-color: #FFFFFF;
        border: 2px solid #2D3748;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 4px 4px 0px #2D3748;
    }
    
    /* HUD Box */
    .hud-box {
        background-color: #EDF2F7;
        border: 2px solid #2D3748;
        border-radius: 6px;
        padding: 12px;
        font-weight: bold;
        text-align: center;
    }
    
    /* Mini Map Display */
    .mini-map {
        background-color: #1A202C;
        color: #68D391 !important;
        font-family: 'Courier New', monospace;
        padding: 15px;
        border-radius: 6px;
        border: 2px solid #4A5568;
        white-space: pre;
        line-height: 1.25;
        font-size: 0.95rem;
    }
    .mini-map span {
        color: inherit !important;
    }
    
    /* Status Badges */
    .badge-a { background-color: #C6F6D5; color: #22543D !important; border: 1px solid #38A169; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-b { background-color: #EBF8FF; color: #2B6CB0 !important; border: 1px solid #3182CE; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-c { background-color: #FEFCBF; color: #744210 !important; border: 1px solid #D69E2E; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-d { background-color: #FEEBC8; color: #7B341E !important; border: 1px solid #DD6B20; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-f { background-color: #FED7D7; color: #742A2A !important; border: 1px solid #E53E3E; padding: 4px 10px; border-radius: 4px; font-weight: bold; }

    /* Button Customization for High Visibility */
    .stButton > button {
        background-color: #2B6CB0 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #1A365D !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        box-shadow: 2px 2px 0px #1A365D !important;
    }
    .stButton > button:hover {
        background-color: #2C5282 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
def init_game():
    st.session_state.step = "setup_location" # setup_location -> setup_income -> playing -> ended
    st.session_state.home_base = None
    st.session_state.income = 75000
    st.session_state.month = 1
    st.session_state.om_coins = 50
    st.session_state.cip_coins = 300
    st.session_state.public_trust = 70
    st.session_state.road_scores = {"Kaimuki": 80, "Ewa Beach": 80, "Kaneohe": 80, "Kapolei": 80}
    st.session_state.active_issues = []
    st.session_state.rail_cost_overrun = 0
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.last_action_msg = ""
    st.session_state.event_log = [
        "🏁 Simulation Initialized: Welcome to Oahu Civic Trail (Fiscal Year Q1)."
    ]

if 'step' not in st.session_state:
    init_game()

# --- HELPER FUNCTIONS ---
def get_rating_char(score):
    if score >= 90: return "A+", "badge-a"
    elif score >= 80: return "A", "badge-a"
    elif score >= 70: return "B", "badge-b"
    elif score >= 60: return "C", "badge-c"
    elif score >= 50: return "D", "badge-d"
    else: return "F", "badge-f"

def render_ascii_map():
    towns = ["Kaneohe", "Ewa Beach", "Kaimuki", "Kapolei"]
    status = {}
    for t in towns:
        is_home = "👈 YOUR HOME" if st.session_state.home_base and st.session_state.home_base["name"] == t else ""
        has_issue = "🔴 [POTHOLE 311]" if t in st.session_state.active_issues else "🟢 [CLEAR]"
        score = st.session_state.road_scores.get(t, 80)
        grade, _ = get_rating_char(score)
        status[t] = f"{has_issue} (Grade {grade}) {is_home}"

    map_text = f"""
  =================== 🗺️  OAHU DIGITAL TWIN MINI-MAP ===================
  
  [Windward Coast]   Kaneohe:  {status['Kaneohe']}
                           / 
                          / [Likelike Hwy Corridor]
                         /
  [Leeward / West]   Kapolei:   {status['Kapolei']}
                     Ewa Beach: {status['Ewa Beach']}
                         \\
                          \\____ [H-1 Freeway / Rail Line] ____ 
                                                              \\
  [Town / East]                                     Kaimuki: {status['Kaimuki']}
  ========================================================================
    """
    return map_text

def advance_month(action_choice):
    if st.session_state.game_over or st.session_state.game_won:
        return

    m = st.session_state.month
    my_town = st.session_state.home_base["name"]
    
    # 1. Execute Player Action Choice
    if action_choice == 1: # Apply Cold Patch
        if st.session_state.om_coins >= 50:
            st.session_state.om_coins -= 50
            if my_town in st.session_state.active_issues:
                st.session_state.active_issues.remove(my_town)
            st.session_state.road_scores[my_town] = min(100, st.session_state.road_scores[my_town] + 15)
            st.session_state.public_trust = min(100, st.session_state.public_trust + 5)
            msg = f"🔧 Month {m}: Applied temporary O&M Cold-Mix Patch (-50 O&M Coins). Public Trust restored slightly (+5%)."
        else:
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
            msg = f"❌ Month {m}: Insufficient O&M Coins for cold patch! Road condition deteriorated."
            
    elif action_choice == 2: # CIP Repaving Bond
        if st.session_state.public_trust <= 40:
            msg = f"🚫 Month {m}: CIP Bond BLOCKED by Voters! Public Trust is too low ({st.session_state.public_trust}% <= 40%)."
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
        elif st.session_state.cip_coins >= 300:
            st.session_state.cip_coins -= 300
            st.session_state.active_issues = []
            st.session_state.road_scores[my_town] = 100
            st.session_state.public_trust = min(100, st.session_state.public_trust + 20)
            msg = f"🎉 Month {m}: CIP Repaving Bond PASSED (-300 CIP Coins)! {my_town} corridor fully rehabilitated with structural Hot-Mix Asphalt."
        else:
            msg = f"❌ Month {m}: Insufficient CIP Coins to float a repaving bond!"
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
            
    elif action_choice == 3: # File 311 & Wait
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 12)
        if my_town not in st.session_state.active_issues:
            st.session_state.active_issues.append(my_town)
        st.session_state.public_trust -= 8
        msg = f"📝 Month {m}: Submitted HNL 311 report. Ticket is pending behind municipal backlog. Road degraded."
        
    elif action_choice == 4: # Pass / Do nothing
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 8)
        msg = f"⏳ Month {m}: No maintenance action taken."

    st.session_state.event_log.append(msg)
    
    # 2. Add Monthly Tax Replenishment
    tax_om = max(15, int(st.session_state.income * 0.0002))
    st.session_state.om_coins += tax_om
    st.session_state.event_log.append(f"💵 Tax Deposit: Received +{tax_om} O&M tax revenue.")

    # 3. Trigger Random Oahu Weather & Macro-Economic Events
    event_chance = random.random()
    if event_chance < 0.30: # Kona Storm / Heavy Rain
        impacted_town = random.choice(list(st.session_state.road_scores.keys()))
        st.session_state.road_scores[impacted_town] = max(30, st.session_state.road_scores[impacted_town] - 15)
        if impacted_town not in st.session_state.active_issues:
            st.session_state.active_issues.append(impacted_town)
        st.session_state.event_log.append(f"🌀 WEATHER ALERT: Kona Downpour struck {impacted_town}! Rain infiltrated cracks and loosened base course.")
        
    elif event_chance < 0.50: # Honolulu Rail Cost Overrun
        overrun = random.randint(20, 40)
        siphoned = min(st.session_state.cip_coins, overrun)
        st.session_state.cip_coins -= siphoned
        st.session_state.rail_cost_overrun += overrun
        st.session_state.event_log.append(f"🚧 RAIL DEFICIT EMERGENCY: Utility line realignment on Dillingham Blvd siphoned -{siphoned} CIP Coins from your capital pool!")

    elif event_chance < 0.65: # West Coast Diesel & Asphalt Price Hike
        st.session_state.event_log.append("🚢 MARITIME SHOCK: West Coast shipping bottlenecks increased imported cold-mix asphalt prices.")

    # 4. Check End / Game Over Conditions
    st.session_state.month += 1
    
    if st.session_state.public_trust <= 30:
        st.session_state.game_over = True
        st.session_state.step = "ended"
        st.session_state.event_log.append("💀 SYSTEM COLLAPSE: Public Trust dropped to 30%. Voters passed a referendum revoking capital bond authority!")
    elif st.session_state.month > 12:
        st.session_state.step = "ended"
        if st.session_state.road_scores[my_town] >= 75:
            st.session_state.game_won = True
            st.session_state.event_log.append("🏆 FISCAL YEAR SUCCESS: You successfully navigated 12 months of Oahu weather and budget constraints!")
        else:
            st.session_state.game_over = True
            st.session_state.event_log.append("⚠️ FISCAL YEAR END: Your neighborhood roads ended in failing condition due to budget starvation.")

# =============================================================================
# --- APP FLOW SCREENS ---
# =============================================================================

st.title("🌴 OAHU CIVIC TRAIL")
st.caption("Oregon Trail Edition | Socratic Municipal Budget Simulator")

# --- STEP 1: ONBOARDING - CHOOSE LOCATION ---
if st.session_state.step == "setup_location":
    st.markdown("""
    <div class="trail-card">
        <h3>🌴 WELCOME TO OAHU CIVIC TRAIL</h3>
        <p>Most citizens believe potholes exist because city crews are 'lazy'. This simulator deconstructs how municipal money <b>actually</b> flows under Honolulu's hood.</p>
        <p><b>Your Mission:</b> Manage your corridor for a 12-month Fiscal Year. Balance your daily <b>🔵 O&M Wallet</b> (operating cash for temporary patches) against your <b>🟡 CIP Wallet</b> (capital bonds for permanent repaving).</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📍 STEP 1: Choose Your Home Base / Living Area")
    
    loc_col1, loc_col2 = st.columns(2)
    
    with loc_col1:
        st.markdown("""
        **[A] Kaimuki (Town Corridor)**
        * High density, heavy foot traffic, older road beds.
        * *Vulnerability:* Dense underground utility lines require frequent trench repaving.
        """)
        if st.button("Choose [A] Kaimuki"):
            st.session_state.home_base = {"name": "Kaimuki", "corridor": "Waialae / H-1", "vulnerability": "Utility Trenching"}
            st.session_state.step = "setup_income"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        **[B] Ewa Beach (Leeward Hub)**
        * Sprawling commuter region, high vehicle volume.
        * *Vulnerability:* Heavy daily axle load on Fort Weaver Road causes deep rutting.
        """)
        if st.button("Choose [B] Ewa Beach"):
            st.session_state.home_base = {"name": "Ewa Beach", "corridor": "Fort Weaver Rd", "vulnerability": "Heavy Commuter Load"}
            st.session_state.step = "setup_income"
            st.rerun()

    with loc_col2:
        st.markdown("""
        **[C] Kaneohe (Windward Side)**
        * Subtropical climate, high annual rainfall.
        * *Vulnerability:* Severe water intrusion washes away subgrade base courses.
        """)
        if st.button("Choose [C] Kaneohe"):
            st.session_state.home_base = {"name": "Kaneohe", "corridor": "Likelike Hwy", "vulnerability": "Subgrade Water Intrusion"}
            st.session_state.step = "setup_income"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        **[D] Kapolei (Second City)**
        * Fast-growing transit hub, heavy construction equipment.
        * *Vulnerability:* Construction truck traffic accelerates surface cracking.
        """)
        if st.button("Choose [D] Kapolei"):
            st.session_state.home_base = {"name": "Kapolei", "corridor": "Kapolei Pkwy / H-201", "vulnerability": "Construction Truck Load"}
            st.session_state.step = "setup_income"
            st.rerun()

# --- STEP 2: SETUP HOUSEHOLD INCOME & BUDGET ---
elif st.session_state.step == "setup_income":
    st.markdown(f"""
    <div class="trail-card">
        <h3>📍 Selected Home Base: {st.session_state.home_base['name']} ({st.session_state.home_base['corridor']})</h3>
        <p><b>Primary Vulnerability:</b> {st.session_state.home_base['vulnerability']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💵 STEP 2: Choose Household Income Profile")
    st.write("Your household income determines your annual road-tax contribution tokens:")
    
    inc_col1, inc_col2 = st.columns(2)
    
    with inc_col1:
        if st.button("💼 Civil Servant / Public Worker ($65,000/yr)"):
            st.session_state.income = 65000
            st.session_state.om_coins = 50
            st.session_state.cip_coins = 300
            st.session_state.step = "playing"
            st.rerun()
            
        if st.button("🏫 Teacher / Educator ($75,000/yr)"):
            st.session_state.income = 75000
            st.session_state.om_coins = 60
            st.session_state.cip_coins = 350
            st.session_state.step = "playing"
            st.rerun()

    with inc_col2:
        if st.button("🛠️ Local Small Business Owner ($95,000/yr)"):
            st.session_state.income = 95000
            st.session_state.om_coins = 80
            st.session_state.cip_coins = 450
            st.session_state.step = "playing"
            st.rerun()

    st.divider()
    custom_inc = st.number_input("Or enter custom household income ($):", value=75000, step=5000)
    if st.button("Start Trail with Custom Income"):
        st.session_state.income = custom_inc
        st.session_state.om_coins = max(40, int(custom_inc * 0.0008))
        st.session_state.cip_coins = max(250, int(custom_inc * 0.004))
        st.session_state.step = "playing"
        st.rerun()

# --- STEP 3: MAIN GAMEPLAY SCREEN ---
elif st.session_state.step == "playing":
    my_town = st.session_state.home_base["name"]
    score = st.session_state.road_scores[my_town]
    grade, badge_class = get_rating_char(score)
    
    # --- HUD STATS ROW ---
    st.markdown("### 📊 FISCAL YEAR HUD")
    hud1, hud2, hud3, hud4 = st.columns(4)
    
    with hud1:
        st.markdown(f"""
        <div class="hud-box">
            📅 Month: {st.session_state.month} / 12<br>
            <small>Home: {my_town}</small>
        </div>
        """, unsafe_allow_html=True)
        
    with hud2:
        st.markdown(f"""
        <div class="hud-box">
            🔵 O&M Wallet: {st.session_state.om_coins} Coins<br>
            <small>Operating Cash</small>
        </div>
        """, unsafe_allow_html=True)

    with hud3:
        st.markdown(f"""
        <div class="hud-box">
            🟡 CIP Wallet: {st.session_state.cip_coins} Coins<br>
            <small>Capital Bonds</small>
        </div>
        """, unsafe_allow_html=True)

    with hud4:
        st.markdown(f"""
        <div class="hud-box">
            ❤️ Public Trust: {st.session_state.public_trust}%<br>
            <small>Req > 40% for Bonds</small>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # --- MINI MAP & STATUS ---
    st.markdown(f'<div class="mini-map">{render_ascii_map()}</div>', unsafe_allow_html=True)
    st.write("")
    
    st.markdown(f"""
    <div class="trail-card">
        <h4>🛣️ Neighborhood Corridor Condition: <span class="{badge_class}">Grade {grade} ({score}/100)</span></h4>
        <p><b>Primary Corridor:</b> {st.session_state.home_base['corridor']} | <b>Vulnerability:</b> {st.session_state.home_base['vulnerability']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- OREGON TRAIL PROMPTS & DECISION CHOICE ---
    st.subheader(f"🎮 Month {st.session_state.month} - Choose Your Action:")
    
    opt_col1, opt_col2 = st.columns(2)
    
    with opt_col1:
        st.markdown("""
        **[Option 1] 🔧 Apply Temporary O&M Cold Patch**
        * *Cost:* 50 Blue O&M Coins
        * *Effect:* Quick 'throw-and-go' fix. Stops immediate road decay and restores Public Trust slightly (+5%).
        """)
        if st.button("Select [1] Apply Cold Patch"):
            advance_month(1)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        **[Option 2] 🏗️ Propose District CIP Repaving Bond**
        * *Cost:* 300 Gold CIP Coins
        * *Effect:* Permanent Hot-Mix Asphalt repaving. Fully restores corridor to **Grade A+**.
        * *Constraint:* Requires **Public Trust > 40%** to pass voter approval.
        """)
        if st.button("Select [2] Issue Repaving Bond"):
            advance_month(2)
            st.rerun()

    with opt_col2:
        st.markdown("""
        **[Option 3] 📝 File HNL 311 Report & Wait**
        * *Cost:* 0 Coins
        * *Effect:* Submits a pothole ticket. Ticket sits behind 45-day municipal backlog while road condition drops.
        """)
        if st.button("Select [3] File 311 Ticket"):
            advance_month(3)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        **[Option 4] ⏩ Pass Turn / Observe System**
        * *Cost:* 0 Coins
        * *Effect:* Advance to next month without taking maintenance action.
        """)
        if st.button("Select [4] Pass Turn"):
            advance_month(4)
            st.rerun()

    st.divider()
    
    # --- CHRONOLOGICAL EVENT LOG TICKER ---
    st.subheader("📜 Live System Event Ticker")
    log_text = "\n".join(reversed(st.session_state.event_log))
    st.text_area("Chronological System Ledger", value=log_text, height=220, disabled=True)

# --- STEP 4: GAME ENDED / SUMMARY SCREEN ---
elif st.session_state.step == "ended":
    my_town = st.session_state.home_base["name"]
    score = st.session_state.road_scores[my_town]
    grade, badge_class = get_rating_char(score)
    
    if st.session_state.game_won:
        st.balloons()
        st.markdown(f"""
        <div class="trail-card">
            <h2>🏆 VICTORY! Fiscal Year Complete</h2>
            <h3>Final Neighborhood Grade: <span class="{badge_class}">Grade {grade} ({score}/100)</span></h3>
            <p>You successfully navigated 12 months of Oahu weather, inflation shocks, and Rail cost overruns!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="trail-card">
            <h2>💀 SYSTEM COLLAPSE!</h2>
            <h3>Final Neighborhood Grade: <span class="{badge_class}">Grade {grade} ({score}/100)</span></h3>
            <p>Your road system degraded into failing condition or Public Trust eroded below safety thresholds.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📜 Final Ledger Ticker")
    log_text = "\n".join(reversed(st.session_state.event_log))
    st.text_area("Final Fiscal Summary", value=log_text, height=250, disabled=True)
    
    if st.button("🔄 Play Again / Restart Simulation"):
        init_game()
        st.rerun()

# --- FOOTER / PODCAST BLURB ---
st.divider()
st.markdown("""
<div class="trail-card">
    <h3>🎙️ About the Problem Solvers Podcast</h3>
    <p>Join <b>Tappy</b> and <b>Pua</b> on <b>Problem Solvers</b> as we deconstruct complex civic, technical, and economic challenges from first principles.</p>
    <p><b>The Socratic Lesson:</b> Potholes aren't caused by 'lazy crews'—they exist because cities run daily 311 work orders (O&M) and long-term capital bonds (CIP) on separate, decoupled ledgers. Stop asking <i>'Who is to blame?'</i> and start asking <i>'What is the actual system problem we need to define first?'</i></p>
</div>
""", unsafe_allow_html=True)
