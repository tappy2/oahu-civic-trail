import streamlit as st
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Oahu Civic Trail v4 - Oregon Trail Edition",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- COMPACT HIGH-CONTRAST LIGHT STYLING (ZERO-SCROLL DESIGN) ---
st.markdown("""
<style>
    /* Remove default Streamlit top/bottom padding for zero-scroll fit */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 98% !important;
    }
    
    .stApp {
        background-color: #FBF9F1;
        color: #1A1C20;
        font-family: 'Courier New', Courier, monospace;
    }
    
    h1, h2, h3, h4, h5, h6, p, div, label, span {
        color: #1A1C20 !important;
    }
    
    /* Compact HUD Boxes */
    .hud-box {
        background-color: #EDF2F7;
        border: 2px solid #2D3748;
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: bold;
        text-align: center;
        font-size: 0.9rem;
    }
    
    /* Condensed Mini-Map Bar */
    .map-bar {
        background-color: #FFFDF5;
        color: #1A202C !important;
        font-family: 'Courier New', monospace;
        padding: 8px 12px;
        border-radius: 6px;
        border: 2px solid #2D3748;
        box-shadow: 2px 2px 0px #2D3748;
        font-size: 0.88rem;
        margin-bottom: 10px;
    }
    
    /* Event Ticker Card */
    .ticker-card {
        background-color: #FFFFFF;
        border: 2px solid #2D3748;
        border-radius: 6px;
        padding: 12px;
        box-shadow: 3px 3px 0px #2D3748;
        height: 280px;
        overflow-y: auto;
    }
    
    /* Status Badges */
    .badge-a { background-color: #C6F6D5; color: #22543D !important; border: 1px solid #38A169; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-b { background-color: #EBF8FF; color: #2B6CB0 !important; border: 1px solid #3182CE; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-c { background-color: #FEFCBF; color: #744210 !important; border: 1px solid #D69E2E; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-d { background-color: #FEEBC8; color: #7B341E !important; border: 1px solid #DD6B20; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-f { background-color: #FED7D7; color: #742A2A !important; border: 1px solid #E53E3E; padding: 2px 6px; border-radius: 4px; font-weight: bold; }

    /* Compact Button Styling */
    .stButton > button {
        background-color: #2B6CB0 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #1A365D !important;
        border-radius: 5px !important;
        padding: 6px 12px !important;
        box-shadow: 2px 2px 0px #1A365D !important;
        width: 100%;
        font-size: 0.85rem !important;
    }
    .stButton > button:hover {
        background-color: #2C5282 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
def init_game():
    st.session_state.step = "setup_location"
    st.session_state.home_base = None
    st.session_state.income = 75000
    st.session_state.month = 1
    st.session_state.om_coins = 50
    st.session_state.cip_coins = 300
    st.session_state.public_trust = 70
    st.session_state.road_scores = {"Kaimuki": 80, "Ewa Beach": 80, "Kaneohe": 80, "Kapolei": 80}
    st.session_state.active_issues = []
    st.session_state.active_patches = {} # tracks patches per town
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.latest_event = "🏁 Fiscal Year Q1 Initialized. Choose your first action."
    st.session_state.event_log = [
        "🏁 Fiscal Year Q1 Initialized: Welcome to Oahu Civic Trail v4."
    ]

if 'step' not in st.session_state:
    init_game()

def get_rating_char(score):
    if score >= 90: return "A+", "badge-a"
    elif score >= 80: return "A", "badge-a"
    elif score >= 70: return "B", "badge-b"
    elif score >= 60: return "C", "badge-c"
    elif score >= 50: return "D", "badge-d"
    else: return "F", "badge-f"

def render_condensed_map():
    towns = ["Kaimuki", "Ewa Beach", "Kaneohe", "Kapolei"]
    items = []
    for t in towns:
        score = st.session_state.road_scores.get(t, 80)
        grade, badge_cls = get_rating_char(score)
        is_home = "📍[YOUR HOME]" if st.session_state.home_base and st.session_state.home_base["name"] == t else ""
        has_311 = "🔴 311 ACTIVE" if t in st.session_state.active_issues else "🟢 OK"
        items.append(f"<b>{t}</b> {is_home}: <span class='{badge_cls}'>Grade {grade}</span> ({has_311})")
    
    return " &nbsp;|&nbsp; ".join(items)

def advance_month(action_choice):
    if st.session_state.game_over or st.session_state.game_won:
        return

    m = st.session_state.month
    my_town = st.session_state.home_base["name"]
    
    # 1. Execute Action Choice
    if action_choice == 1: # DFM Work Order (Cold Patch)
        if st.session_state.om_coins >= 50:
            st.session_state.om_coins -= 50
            if my_town in st.session_state.active_issues:
                st.session_state.active_issues.remove(my_town)
            st.session_state.active_patches[my_town] = True
            st.session_state.road_scores[my_town] = min(100, st.session_state.road_scores[my_town] + 15)
            st.session_state.public_trust = min(100, st.session_state.public_trust + 5)
            msg = f"🔧 Month {m}: Dispatched DFM Crew for Cold Patch (-50 O&M). Pothole filled; Public Trust +5%."
        else:
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
            msg = f"❌ Month {m}: Insufficient O&M Coins for DFM work order! Road degraded."
            
    elif action_choice == 2: # CIP Contract RFP (Hot Mix)
        if st.session_state.public_trust <= 40:
            msg = f"🚫 Month {m}: CIP Bond RFP BLOCKED by Voters! Public Trust is too low ({st.session_state.public_trust}% <= 40%)."
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
        elif st.session_state.cip_coins >= 300:
            st.session_state.cip_coins -= 300
            st.session_state.active_issues = []
            st.session_state.road_scores[my_town] = 100
            st.session_state.public_trust = min(100, st.session_state.public_trust + 20)
            msg = f"🎉 Month {m}: CIP Repaving RFP Awarded (-300 CIP)! {my_town} corridor rehabilitated with Hot-Mix Asphalt."
        else:
            msg = f"❌ Month {m}: Insufficient CIP Coins to fund repaving RFP!"
            st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 10)
            
    elif action_choice == 3: # File 311 & Wait
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 12)
        if my_town not in st.session_state.active_issues:
            st.session_state.active_issues.append(my_town)
        st.session_state.public_trust -= 8
        msg = f"📝 Month {m}: Filed HNL 311 Ticket. Request placed in 45-day DFM backlog. Road degraded."
        
    elif action_choice == 4: # Pass Turn
        st.session_state.road_scores[my_town] = max(30, st.session_state.road_scores[my_town] - 8)
        msg = f"⏳ Month {m}: No maintenance action taken."

    st.session_state.event_log.append(msg)
    
    # 2. Tax Replenishment
    tax_om = max(15, int(st.session_state.income * 0.0002))
    st.session_state.om_coins += tax_om
    st.session_state.event_log.append(f"💵 Tax Allocation: Received +{tax_om} O&M operating revenue.")

    # 3. Dynamic Weather / Tax / Macro Events (Driving Player Choices)
    event_chance = random.random()
    
    if event_chance < 0.28: # Hurricane Rain / Kona Storm
        impacted_town = random.choice(list(st.session_state.road_scores.keys()))
        was_patched = st.session_state.active_patches.get(impacted_town, False)
        st.session_state.active_patches[impacted_town] = False
        st.session_state.road_scores[impacted_town] = max(30, st.session_state.road_scores[impacted_town] - 18)
        if impacted_town not in st.session_state.active_issues:
            st.session_state.active_issues.append(impacted_town)
        
        event_msg = f"🌀 HURRICANE RAINS & KONA STORM: Severe downpour flooded {impacted_town}!"
        if was_patched:
            event_msg += " Previous month's cold patch WASHED AWAY, causing subgrade erosion!"
        else:
            event_msg += " Water intruded into base course, creating deep potholes!"
            
        st.session_state.latest_event = event_msg
        st.session_state.event_log.append(event_msg)

    elif event_chance < 0.48: # Rail Windfall / Tax Realignment
        if random.random() < 0.5: # Rail Deficit
            siphoned = min(st.session_state.cip_coins, 40)
            st.session_state.cip_coins -= siphoned
            event_msg = f"🚧 RAIL DEFICIT EMERGENCY: Transit utility realignment siphoned -{siphoned} CIP Coins from your capital pool!"
        else: # Rail Windfall / Federal Grant Match
            windfall = 50
            st.session_state.cip_coins += windfall
            event_msg = f"🎉 RAIL WINDFALL & FEDERAL GRANT: Honolulu received a federal transit match! +{windfall} CIP Coins added to capital pool!"
            
        st.session_state.latest_event = event_msg
        st.session_state.event_log.append(event_msg)

    elif event_chance < 0.65: # Maritime Supply Chain & Asphalt Hike
        event_msg = "🚢 MARITIME SUPPLY CHAIN SPIKE: West Coast diesel & imported asphalt costs surged!"
        st.session_state.latest_event = event_msg
        st.session_state.event_log.append(event_msg)
    else:
        st.session_state.latest_event = msg

    # 4. Check End Conditions
    st.session_state.month += 1
    
    if st.session_state.public_trust <= 30:
        st.session_state.game_over = True
        st.session_state.step = "ended"
        st.session_state.event_log.append("💀 SYSTEM COLLAPSE: Public Trust dropped to 30%. Voters revoking capital bond authority!")
    elif st.session_state.month > 12:
        st.session_state.step = "ended"
        if st.session_state.road_scores[my_town] >= 75:
            st.session_state.game_won = True
            st.session_state.event_log.append("🏆 FISCAL YEAR SUCCESS: Navigated 12 months of weather, tax shifts, and budget constraints!")
        else:
            st.session_state.game_over = True
            st.session_state.event_log.append("⚠️ FISCAL YEAR END: Neighborhood roads ended in failing condition due to budget starvation.")

# =============================================================================
# --- MAIN APP LAYOUT (ZERO-SCROLL COMPACT DESIGN) ---
# =============================================================================

st.markdown("### 🌴 OAHU CIVIC TRAIL v4 <small style='font-size:0.8rem; font-weight:normal;'>| Oregon Trail Edition for Maker Mixer</small>", unsafe_allow_html=True)

# --- STEP 1: SETUP LOCATION ---
if st.session_state.step == "setup_location":
    st.info(" Most citizens believe potholes exist because city crews are 'lazy'. This simulator deconstructs how municipal money **actually** flows under Honolulu's hood.")
    st.subheader("📍 STEP 1: Choose Your Home Base")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**[A] Kaimuki (Town)**: Dense underground utility lines require frequent trench repaving.")
        if st.button("Choose [A] Kaimuki"):
            st.session_state.home_base = {"name": "Kaimuki", "corridor": "Waialae Ave / H-1", "vulnerability": "Utility Trenching"}
            st.session_state.step = "setup_income"
            st.rerun()
            
        st.markdown("**[B] Ewa Beach (Leeward)**: Heavy daily axle load on Fort Weaver Road causes deep rutting.")
        if st.button("Choose [B] Ewa Beach"):
            st.session_state.home_base = {"name": "Ewa Beach", "corridor": "Fort Weaver Rd", "vulnerability": "Heavy Commuter Load"}
            st.session_state.step = "setup_income"
            st.rerun()

    with c2:
        st.markdown("**[C] Kaneohe (Windward)**: Severe subtropical rain washes away subgrade base courses.")
        if st.button("Choose [C] Kaneohe"):
            st.session_state.home_base = {"name": "Kaneohe", "corridor": "Likelike Hwy", "vulnerability": "Subgrade Water Intrusion"}
            st.session_state.step = "setup_income"
            st.rerun()

        st.markdown("**[D] Kapolei (Second City)**: Construction truck traffic accelerates surface cracking.")
        if st.button("Choose [D] Kapolei"):
            st.session_state.home_base = {"name": "Kapolei", "corridor": "Kapolei Pkwy", "vulnerability": "Construction Truck Load"}
            st.session_state.step = "setup_income"
            st.rerun()

# --- STEP 2: SETUP INCOME ---
elif st.session_state.step == "setup_income":
    st.write(f"📍 **Selected Home Base:** {st.session_state.home_base['name']} ({st.session_state.home_base['corridor']})")
    st.subheader("💵 STEP 2: Choose Household Income Profile")
    st.caption("All taxes pool into the City Highway Fund, but income establishes your neighborhood's Civic Priority Token balance:")
    
    i1, i2 = st.columns(2)
    with i1:
        if st.button("💼 Civil Servant ($65,000/yr) -> 50 O&M / 300 CIP"):
            st.session_state.income = 65000
            st.session_state.om_coins = 50
            st.session_state.cip_coins = 300
            st.session_state.step = "playing"
            st.rerun()
            
        if st.button("🏫 Educator / Teacher ($75,000/yr) -> 60 O&M / 350 CIP"):
            st.session_state.income = 75000
            st.session_state.om_coins = 60
            st.session_state.cip_coins = 350
            st.session_state.step = "playing"
            st.rerun()

    with i2:
        if st.button("🛠️ Small Business Owner ($95,000/yr) -> 80 O&M / 450 CIP"):
            st.session_state.income = 95000
            st.session_state.om_coins = 80
            st.session_state.cip_coins = 450
            st.session_state.step = "playing"
            st.rerun()

# --- STEP 3: MAIN GAMEPLAY (ZERO-SCROLL COMPACT DASHBOARD) ---
elif st.session_state.step == "playing":
    my_town = st.session_state.home_base["name"]
    score = st.session_state.road_scores[my_town]
    grade, badge_cls = get_rating_char(score)
    
    # 1. TOP STATS HUD
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown(f"<div class='hud-box'>📅 Month {st.session_state.month}/12 | 📍 {my_town}</div>", unsafe_allow_html=True)
    with h2:
        st.markdown(f"<div class='hud-box'>🔵 O&M: {st.session_state.om_coins} Coins <small>(DFM Budget)</small></div>", unsafe_allow_html=True)
    with h3:
        st.markdown(f"<div class='hud-box'>🟡 CIP: {st.session_state.cip_coins} Coins <small>(RFP Bonds)</small></div>", unsafe_allow_html=True)
    with h4:
        st.markdown(f"<div class='hud-box'>❤️ Trust: {st.session_state.public_trust}% <small>(Req > 40%)</small></div>", unsafe_allow_html=True)

    # 2. CONDENSED MAP STATUS BAR
    st.markdown(f"<div class='map-bar'>🗺️ <b>OAHU CORRIDORS STATUS:</b> {render_condensed_map()}</div>", unsafe_allow_html=True)

    # 3. TWO-COLUMN COMPACT GAMEPLAY PANEL
    col_act, col_log = st.columns([1.1, 0.9])
    
    with col_act:
        st.markdown(f"#### 🎮 Month {st.session_state.month} Actions | Status: <span class='{badge_cls}'>Grade {grade} ({score}/100)</span>", unsafe_allow_html=True)
        
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("**[1] 🔧 Dispatch DFM Crew**\n* *Cost:* 50 Blue O&M\n* *Outcome:* +15 Health, +5% Trust *(Temporary cold patch)*")
            if st.button("Select [1] Cold Patch"):
                advance_month(1)
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("**[2] 🏗️ Award CIP Repaving RFP**\n* *Cost:* 300 Gold CIP\n* *Outcome:* Restores to **Grade A+**, +20% Trust *(Req Trust > 40%)*")
            if st.button("Select [2] CIP RFP"):
                advance_month(2)
                st.rerun()

        with a2:
            st.markdown("**[3] 📝 File 311 & Wait**\n* *Cost:* 0 Coins\n* *Outcome:* -12 Health, -8% Trust *(45-day DFM backlog)*")
            if st.button("Select [3] 311 Ticket"):
                advance_month(3)
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**[4] ⏩ Pass Turn**\n* *Cost:* 0 Coins\n* *Outcome:* -8 Health *(Observe weather & traffic wear)*")
            if st.button("Select [4] Pass Turn"):
                advance_month(4)
                st.rerun()

    with col_log:
        st.markdown("#### 📢 Latest System Updates & Weather")
        st.warning(st.session_state.latest_event)
        
        st.markdown("##### 📜 Chronological Event Ledger")
        log_reversed = "\n".join(reversed(st.session_state.event_log))
        st.text_area("Ledger", value=log_reversed, height=140, disabled=True, label_visibility="collapsed")

# --- STEP 4: ENDED ---
elif st.session_state.step == "ended":
    my_town = st.session_state.home_base["name"]
    score = st.session_state.road_scores[my_town]
    grade, badge_cls = get_rating_char(score)
    
    if st.session_state.game_won:
        st.balloons()
        st.success(f"🏆 VICTORY! Fiscal Year Complete. Final Grade: Grade {grade} ({score}/100)")
    else:
        st.error(f"💀 SYSTEM COLLAPSE! Final Grade: Grade {grade} ({score}/100)")

    st.text_area("Final Summary", value="\n".join(reversed(st.session_state.event_log)), height=200, disabled=True)
    if st.button("🔄 Restart Simulation"):
        init_game()
        st.rerun()

# --- FOOTER / PODCAST EXPANDER (COLLAPSED TO PREVENT SCROLLING) ---
with st.expander("🎙️ About Problem Solvers Podcast (Tappy & Pua)", expanded=False):
    st.markdown("""
    Join **Tappy** and **Pua** on **Problem Solvers** as we deconstruct complex civic, technical, and economic challenges from first principles.
    
    **The Socratic Lesson:** Potholes aren't caused by 'lazy crews'—they exist because cities run daily 311 work orders (O&M) and long-term capital bonds (CIP) on separate, decoupled ledgers. Stop asking *'Who is to blame?'* and start asking *'What is the actual system problem we need to define first?'*
    """)
