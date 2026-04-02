import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import requests
import json
from difflib import SequenceMatcher

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
page_title=“Best Ball Value Hunter”,
page_icon=“🎯”,
layout=“wide”,
initial_sidebar_state=“expanded”
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0e1a; color: #e8eaf0; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
.header-box {
    background: linear-gradient(135deg, #0d1b3e 0%, #1a0a2e 60%, #0a1a2e 100%);
    border: 1px solid #2a3060;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
}
.grade-box {
    background: linear-gradient(135deg, #12172a, #1a2035);
    border: 2px solid #2a3050;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    margin-bottom: 20px;
}
</style>

“””, unsafe_allow_html=True)

# ── BASELINE DATA ──────────────────────────────────────────────────────────────

BASELINE_CSV = (
“Player,Pos,ADP,+/-,%,sigma\n”
“Bijan Robinson,RB1,1.4,-0.2,-16.7%,0.1\n”
“Jahmyr Gibbs,RB2,1.8,2.2,55.0%,0.6\n”
“Ja’Marr Chase,WR1,3.4,-0.1,-3.0%,0.2\n”
“Puka Nacua,WR2,3.9,-1.5,-62.5%,0.4\n”
“Jaxon Smith-Njigba,WR3,5.1,-0.5,-10.9%,0.1\n”
“Jonathan Taylor,RB3,6.4,1.0,13.5%,0.2\n”
“Christian McCaffrey,RB4,7.5,0.6,7.4%,0.3\n”
“CeeDee Lamb,WR4,8.5,-1.5,-21.4%,0.5\n”
“Amon-Ra St. Brown,WR5,9.0,1.3,12.6%,0.2\n”
“Justin Jefferson,WR6,10.1,5.3,34.4%,2.0\n”
“James Cook,RB5,11.0,-1.2,-12.2%,0.3\n”
“Ashton Jeanty,RB6,11.9,4.2,26.1%,1.0\n”
“De’Von Achane,RB7,13.5,-3.0,-28.6%,0.9\n”
“Omarion Hampton,RB8,15.3,2.4,13.6%,0.7\n”
“Jeremiyah Love,RB9,15.6,6.2,28.4%,1.7\n”
“Saquon Barkley,RB10,16.0,1.0,5.9%,0.5\n”
“Malik Nabers,WR7,17.7,-3.0,-20.4%,1.2\n”
“Trey McBride,TE1,18.9,-5.7,-43.2%,1.7\n”
“Kenneth Walker III,RB11,19.1,17.3,47.5%,5.1\n”
“Drake London,WR8,19.5,-5.1,-35.4%,1.5\n”
“Derrick Henry,RB12,20.4,1.5,6.8%,0.6\n”
“Chase Brown,RB13,21.9,2.3,9.5%,0.7\n”
“Brock Bowers,TE2,23.3,-3.6,-18.3%,1.2\n”
“George Pickens,WR9,23.9,-2.5,-11.7%,0.6\n”
“Nico Collins,WR10,24.4,-1.5,-6.6%,0.5\n”
“Chris Olave,WR11,27.0,-0.8,-3.1%,0.5\n”
“Josh Jacobs,RB14,27.2,2.9,9.6%,0.8\n”
“Josh Allen,QB1,29.0,-2.6,-9.8%,1.0\n”
“A.J. Brown,WR12,29.4,1.9,6.1%,1.5\n”
“Travis Etienne Jr.,RB15,30.3,6.2,17.0%,2.9\n”
“Tetairoa McMillan,WR13,31.6,-1.8,-6.0%,0.7\n”
“Breece Hall,RB16,32.4,3.3,9.2%,1.6\n”
“Tee Higgins,WR14,32.9,-3.2,-10.8%,1.1\n”
“Kyren Williams,RB17,34.3,-0.7,-2.1%,0.7\n”
“Rashee Rice,WR15,35.1,-8.9,-34.0%,3.9\n”
“Garrett Wilson,WR16,36.6,5.3,12.6%,1.0\n”
“Bucky Irving,RB18,36.9,-5.2,-16.4%,3.2\n”
“Ladd McConkey,WR17,38.8,-1.5,-4.0%,0.9\n”
“Emeka Egbuka,WR18,39.0,17.4,30.9%,4.2\n”
“Javonte Williams,RB19,40.4,31.6,43.9%,8.0\n”
“Zay Flowers,WR19,40.6,4.8,10.6%,1.3\n”
“DeVonta Smith,WR20,41.5,2.0,4.6%,1.2\n”
“Luther Burden,WR21,42.3,11.8,21.8%,3.0\n”
“Jameson Williams,WR22,45.1,-8.9,-24.6%,2.3\n”
“Colston Loveland,TE3,46.0,-3.9,-9.3%,1.6\n”
“Jaylen Waddle,WR23,47.2,23.3,33.0%,4.4\n”
“Terry McLaurin,WR24,47.5,18.1,27.6%,3.9\n”
“TreVeyon Henderson,RB20,48.7,-2.9,-6.3%,1.3\n”
“Davante Adams,WR25,48.8,-8.4,-20.8%,2.4\n”
“Mike Evans,WR26,49.8,18.2,26.8%,7.9\n”
“Lamar Jackson,QB2,50.9,-2.7,-5.6%,1.7\n”
“Rome Odunze,WR27,52.8,4.4,7.7%,2.5\n”
“Quinshon Judkins,RB21,53.8,7.3,11.9%,1.6\n”
“D.J. Moore,WR28,54.1,34.8,39.1%,16.4\n”
“Carnell Tate,WR29,56.5,-4.3,-8.2%,1.5\n”
“Cam Skattebo,RB22,56.8,-9.5,-20.1%,5.4\n”
“Bhayshul Tuten,RB23,56.8,35.1,38.2%,9.6\n”
“David Montgomery,RB24,57.0,71.2,55.5%,22.2\n”
“Christian Watson,WR30,58.7,-5.1,-9.5%,1.3\n”
“D’Andre Swift,RB25,60.6,-4.4,-7.8%,1.3\n”
“Brian Thomas,WR31,61.9,17.2,21.7%,4.4\n”
“Jayden Daniels,QB3,62.4,11.0,15.0%,2.6\n”
“Makai Lemon,WR32,63.4,-1.8,-2.9%,2.5\n”
“Marvin Harrison,WR33,64.7,9.3,12.6%,2.4\n”
“Joe Burrow,QB4,64.7,7.4,10.3%,1.7\n”
“RJ Harvey,RB26,66.5,-20.3,-43.9%,6.4\n”
“Tyler Warren,TE4,68.1,-0.8,-1.2%,1.3\n”
“Caleb Williams,QB5,68.5,-12.4,-22.1%,2.9\n”
“Alec Pierce,WR34,68.8,-7.6,-12.4%,4.9\n”
“Jalen Hurts,QB6,69.6,8.6,11.0%,2.0\n”
“Jordyn Tyson,WR35,70.8,-20.8,-41.6%,5.5\n”
“Drake Maye,QB7,71.9,-32.2,-81.1%,8.9\n”
“Parker Washington,WR36,72.9,13.0,15.1%,2.4\n”
“Chuba Hubbard,RB27,73.8,21.1,22.2%,6.8\n”
“Courtland Sutton,WR37,74.3,-17.1,-29.9%,4.8\n”
“DK Metcalf,WR38,76.9,-12.5,-19.4%,4.1\n”
“Michael Wilson,WR39,77.5,-8.6,-12.5%,2.7\n”
“Jaylen Warren,RB28,78.1,-2.7,-3.6%,2.2\n”
“Rhamondre Stevenson,RB29,79.2,-9.6,-13.8%,4.6\n”
“Harold Fannin,TE5,80.4,-10.0,-14.2%,2.3\n”
“Dak Prescott,QB8,80.6,16.6,17.1%,3.8\n”
“Justin Herbert,QB9,82.6,-18.2,-28.3%,4.2\n”
“Trevor Lawrence,QB10,83.9,-6.3,-8.1%,1.6\n”
“Ricky Pearsall,WR40,85.2,3.3,3.7%,3.7\n”
“Jaxson Dart,QB11,86.5,-14.1,-19.5%,3.5\n”
“Jordan Addison,WR41,87.1,24.0,21.6%,5.7\n”
“Jakobi Meyers,WR42,87.2,3.4,3.8%,1.3\n”
“Tyler Allgeier,RB30,87.5,41.0,31.9%,9.6\n”
“Tucker Kraft,TE6,89.2,-1.1,-1.2%,2.4\n”
“Patrick Mahomes,QB12,89.3,5.6,5.9%,1.7\n”
“Rico Dowdle,RB31,91.3,13.5,12.9%,4.2\n”
“Chris Godwin,WR43,91.4,28.6,23.8%,9.6\n”
“Kyle Monangai,RB32,93.4,-5.5,-6.3%,3.0\n”
“Brock Purdy,QB13,94.6,13.6,12.6%,3.1\n”
“Romeo Doubs,WR44,95.7,16.5,14.7%,15.0\n”
“Bo Nix,QB14,97.1,9.3,8.7%,2.4\n”
“Michael Pittman Jr.,WR45,97.5,-11.4,-13.2%,2.0\n”
“Kyle Pitts,TE7,99.0,-47.0,-90.4%,9.1\n”
“Blake Corum,RB33,99.8,-7.4,-8.0%,2.9\n”
“Quentin Johnston,WR46,101.4,-14.6,-16.8%,5.3\n”
“Sam LaPorta,TE8,101.6,-5.9,-6.2%,3.2\n”
“Matthew Stafford,QB15,102.3,-15.0,-17.2%,2.5\n”
“J.K. Dobbins,RB34,102.3,64.0,38.5%,14.9\n”
“Wan’Dale Robinson,WR47,102.4,2.2,2.1%,3.5\n”
“Tony Pollard,RB35,105.1,-19.9,-23.4%,5.8\n”
“Jared Goff,QB16,105.4,14.4,12.0%,3.0\n”
“Jayden Reed,WR48,105.6,4.1,3.7%,3.1\n”
“Kyler Murray,QB17,106.1,45.7,30.1%,17.1\n”
“Jadarian Price,RB36,108.3,-11.2,-11.5%,3.6\n”
“Jordan Love,QB18,109.1,8.5,7.2%,2.1\n”
“Xavier Worthy,WR49,109.2,-0.4,-0.4%,3.9\n”
“Baker Mayfield,QB19,111.5,20.9,15.8%,4.4\n”
“Oronde Gadsden,TE9,112.2,-0.1,-0.1%,3.0\n”
“Kenneth Gainwell,RB37,114.5,16.5,12.6%,6.1\n”
“Jalen Coker,WR50,116.6,-2.7,-2.4%,1.5\n”
“KC Concepcion,WR51,117.1,45.7,28.1%,7.1\n”
“Tyler Shough,QB20,118.6,27.4,18.8%,5.5\n”
“Jordan Mason,RB38,119.8,39.3,24.7%,14.8\n”
“Dalton Kincaid,TE10,119.9,-25.4,-26.9%,5.6\n”
“Josh Downs,WR52,121.3,9.4,7.2%,11.7\n”
“Matthew Golden,WR53,121.8,4.3,3.4%,1.4\n”
“George Kittle,TE11,123.1,9.2,7.0%,2.9\n”
“Malik Willis,QB21,123.9,49.0,28.3%,15.5\n”
“Jayden Higgins,WR54,125.2,-7.4,-6.3%,2.0\n”
“Rachaad White,RB39,125.9,42.2,25.1%,16.7\n”
“Khalil Shakir,WR55,126.8,-24.3,-23.7%,7.1\n”
“Jake Ferguson,TE12,128.0,9.4,6.8%,2.1\n”
“Jonah Coleman,RB40,129.2,-18.4,-16.6%,4.6\n”
“Sam Darnold,QB22,129.5,21.0,14.0%,6.3\n”
“Kenyon Sadiq,TE13,131.2,-2.4,-1.9%,7.5\n”
“Jalen McMillan,WR56,132.4,11.4,7.9%,8.4\n”
“Travis Kelce,TE14,133.3,61.3,31.5%,14.6\n”
“C.J. Stroud,QB23,135.5,27.7,17.0%,6.4\n”
“Jauan Jennings,WR57,136.0,-5.6,-4.3%,7.6\n”
“Dallas Goedert,TE15,137.2,-22.2,-19.3%,7.7\n”
“Aaron Jones,RB42,137.4,12.5,8.3%,9.6\n”
“Jacory Croskey-Merritt,RB43,139.6,-13.4,-10.6%,5.6\n”
“Chris Rodriguez,RB44,140.0,88.3,38.7%,37.2\n”
“Rashid Shaheed,WR59,141.4,-2.0,-1.4%,1.5\n”
“Cam Ward,QB24,141.7,28.0,16.5%,5.5\n”
“Isaiah Likely,TE16,142.6,25.7,15.3%,12.2\n”
“Daniel Jones,QB25,144.5,38.7,21.1%,8.6\n”
“Zach Charbonnet,RB45,146.1,4.1,2.7%,5.2\n”
“Bryce Young,QB26,147.1,10.6,6.7%,4.6\n”
“Mark Andrews,TE17,147.3,-10.7,-7.8%,3.0\n”
“Tyrone Tracy,RB46,149.0,2.6,1.7%,6.5\n”
“Jonathon Brooks,RB47,150.1,56.2,27.2%,10.9\n”
“Travis Hunter,WR62,153.6,-23.0,-17.6%,6.2\n”
“Brandon Aiyuk,WR63,154.3,-17.0,-12.4%,4.4\n”
“Keaton Mitchell,RB48,155.2,55.5,26.3%,17.3\n”
“Juwan Johnson,TE19,156.5,16.0,9.3%,5.4\n”
“Jerry Jeudy,WR64,160.8,-30.2,-23.1%,6.0\n”
“Deebo Samuel,WR65,161.0,-33.4,-26.2%,11.2\n”
“Hunter Henry,TE20,161.1,-13.1,-8.9%,6.4\n”
“James Conner,RB49,161.7,-1.0,-0.6%,7.9\n”
“Chig Okonkwo,TE21,161.9,74.2,31.4%,27.5\n”
“Isiah Pacheco,RB53,167.8,53.0,24.0%,27.1\n”
“Adonai Mitchell,WR67,169.9,-12.7,-8.1%,6.3\n”
“Calvin Ridley,WR68,172.3,-8.0,-4.9%,2.7\n”
“Tyreek Hill,WR71,175.9,-30.0,-20.6%,10.1\n”
“Dylan Sampson,RB55,178.4,0.0,0.0%,2.1\n”
“Tank Dell,WR72,179.2,-18.5,-11.5%,4.0\n”
“Tre’ Harris,WR73,182.2,33.7,15.6%,7.3\n”
“Brian Robinson,RB56,183.2,37.1,16.8%,7.2\n”
“Tank Bigsby,RB58,185.8,-6.8,-3.8%,3.4\n”
“Darnell Mooney,WR74,186.2,15.9,7.9%,12.0\n”
“Christian Kirk,WR75,186.9,16.0,7.9%,17.3\n”
“Chimere Dike,WR77,189.5,-8.8,-4.9%,5.0\n”
“David Njoku,TE26,192.3,22.8,10.6%,9.0\n”
“Nicholas Singleton,RB59,192.9,3.5,1.8%,7.1\n”
“Alvin Kamara,RB60,193.4,-25.7,-15.3%,16.4\n”
“Mason Taylor,TE27,193.7,8.0,4.0%,3.3\n”
“Cade Otton,TE28,197.1,5.9,2.9%,5.5\n”
“Gunnar Helm,TE29,199.5,33.3,14.3%,6.3\n”
“Jordan James,RB66,214.5,24.2,10.1%,4.7\n”
“Najee Harris,RB67,215.6,7.1,3.2%,6.5\n”
“Ollie Gordon,RB68,223.3,5.9,2.6%,4.0\n”
“Cooper Kupp,WR93,230.8,-39.0,-20.3%,8.0\n”
“Mike Gesicki,TE34,230.9,5.7,2.4%,1.8\n”
)

@st.cache_data
def load_baseline():
df = pd.read_csv(io.StringIO(BASELINE_CSV))
df.columns = df.columns.str.strip()
df[’%’] = df[’%’].str.replace(’%’, ‘’, regex=False).astype(float)
df[‘BasPos’] = df[‘Pos’].str.extract(r’(RB|WR|TE|QB)’)
df[‘PosRank’] = df[‘Pos’].str.extract(r’(\d+)’).astype(float)
df = df.drop_duplicates(subset=[‘Player’]).reset_index(drop=True)
return df

def fuzzy_match(name, candidates, threshold=0.72):
best_score = 0
best_match = None
name_lower = name.lower().strip()
for candidate in candidates:
score = SequenceMatcher(None, name_lower, candidate.lower().strip()).ratio()
if score > best_score:
best_score = score
best_match = candidate
if best_score >= threshold:
return best_match, best_score
return None, best_score

def positional_bonus(pos):
bonuses = {‘RB’: 3.0, ‘WR’: 2.0, ‘TE’: 4.0, ‘QB’: 1.5}
return bonuses.get(pos, 2.0)

def risk_adjusted_score(value_delta, sigma, pos):
if sigma <= 0:
sigma = 0.1
raw = value_delta / (1 + sigma * 0.1)
return raw + positional_bonus(pos)

def team_rating(scores):
if not scores:
return 0, ‘F’, ‘Mystery Team’
avg = np.mean(scores)
normalized = min(100, max(0, 50 + avg * 2.5))
score = int(normalized)
if score >= 90:
grade, title = ‘A+’, ‘Value Assassin’
elif score >= 80:
grade, title = ‘A’, ‘Steal Machine’
elif score >= 70:
grade, title = ‘B+’, ‘Smart Drafter’
elif score >= 60:
grade, title = ‘B’, ‘Solid Operator’
elif score >= 50:
grade, title = ‘C+’, ‘Market Drafter’
elif score >= 40:
grade, title = ‘C’, ‘Slight Reacher’
elif score >= 30:
grade, title = ‘D’, ‘Reach Merchant’
else:
grade, title = ‘F’, ‘Full Send Disaster’
return score, grade, title

def grade_color(grade):
colors = {
‘A+’: ‘#00ff88’, ‘A’: ‘#00ff88’,
‘B+’: ‘#66ccff’, ‘B’: ‘#66ccff’,
‘C+’: ‘#ffcc44’, ‘C’: ‘#ffcc44’,
‘D’: ‘#ff8844’, ‘F’: ‘#ff4444’
}
return colors.get(grade, ‘#aab0c0’)

def grade_emoji(score):
if score >= 80:
return ‘🔥’
elif score >= 60:
return ‘⚡’
else:
return ‘💀’

def generate_narrative(results_df, grade, title, score):
steals = results_df[results_df[‘Value Delta’].notna() & (results_df[‘Value Delta’] > 5)][‘Player’].tolist()
reaches = results_df[results_df[‘Value Delta’].notna() & (results_df[‘Value Delta’] < -5)][‘Player’].tolist()
steal_str = ’, ’.join(steals[:3]) if steals else ‘none’
reach_str = ’, ’.join(reaches[:3]) if reaches else ‘none’

```
prompt = (
    "You are a sarcastic but insightful fantasy football analyst. "
    "Analyze this best ball roster in 3-4 punchy sentences. "
    "Overall grade: " + grade + " (" + str(score) + "/100) - " + title + ". "
    "Top steals vs Big Board ADP: " + steal_str + ". "
    "Biggest reaches: " + reach_str + ". "
    "Be specific, funny, and brutally honest. No fluff."
)

try:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"Content-Type": "application/json"},
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=20
    )
    data = response.json()
    if "content" in data and len(data["content"]) > 0:
        return data["content"][0]["text"]
    return "Could not generate narrative."
except Exception as e:
    return "Narrative unavailable: " + str(e)
```

def extract_roster_from_image(image_bytes, mime_type):
img_b64 = base64.b64encode(image_bytes).decode(“utf-8”)
prompt = (
“This is a screenshot of an Underdog Fantasy best ball roster. “
“Extract every player name and their current ADP or pick number if visible. “
“Return ONLY a JSON array like: “
’[{“name”: “Player Name”, “current_adp”: 12.5}] ’
“If ADP is not visible, set current_adp to null. “
“No other text, just the JSON array.”
)
try:
response = requests.post(
“https://api.anthropic.com/v1/messages”,
headers={“Content-Type”: “application/json”},
json={
“model”: “claude-sonnet-4-20250514”,
“max_tokens”: 1000,
“messages”: [
{
“role”: “user”,
“content”: [
{
“type”: “image”,
“source”: {
“type”: “base64”,
“media_type”: mime_type,
“data”: img_b64
}
},
{“type”: “text”, “text”: prompt}
]
}
]
},
timeout=30
)
data = response.json()
raw = data[“content”][0][“text”].strip()
raw = raw.replace(”`json", "").replace("`”, “”).strip()
players = json.loads(raw)
return players, None
except Exception as e:
return [], str(e)

def process_roster(roster_entries, baseline_df):
results = []
baseline_names = baseline_df[‘Player’].tolist()

```
for entry in roster_entries:
    name = entry.get('name', '').strip()
    current_adp = entry.get('current_adp', None)
    if not name:
        continue

    matched_name, match_score = fuzzy_match(name, baseline_names)
    if matched_name is None:
        results.append({
            'Player': name,
            'Matched': 'No match',
            'Pos': 'N/A',
            'Baseline ADP': None,
            'Current ADP': current_adp,
            'Value Delta': None,
            'Sigma': None,
            'Risk Score': None,
            'Confidence': round(match_score, 2)
        })
        continue

    row = baseline_df[baseline_df['Player'] == matched_name].iloc[0]
    baseline_adp = row['ADP']
    sigma = row['sigma']
    pos = row['BasPos']

    value_delta = None
    if current_adp is not None:
        try:
            value_delta = baseline_adp - float(current_adp)
        except Exception:
            value_delta = None

    risk_score = None
    if value_delta is not None:
        risk_score = round(risk_adjusted_score(value_delta, sigma, pos), 2)

    results.append({
        'Player': name,
        'Matched': matched_name,
        'Pos': pos,
        'Baseline ADP': baseline_adp,
        'Current ADP': current_adp,
        'Value Delta': round(value_delta, 1) if value_delta is not None else None,
        'Sigma': sigma,
        'Risk Score': risk_score,
        'Confidence': round(match_score, 2)
    })

return pd.DataFrame(results)
```

def color_delta(val):
if val is None or (isinstance(val, float) and np.isnan(val)):
return ‘’
if val > 10:
return ‘background-color: #003320; color: #00ff88;’
elif val > 3:
return ‘background-color: #002010; color: #44ff99;’
elif val < -10:
return ‘background-color: #330000; color: #ff4444;’
elif val < -3:
return ‘background-color: #220000; color: #ff8888;’
return ‘color: #aab0c0;’

# ═══════════════════════════════════════════════════════════════════════════════

# MAIN UI

# ═══════════════════════════════════════════════════════════════════════════════

baseline_df = load_baseline()

st.markdown(”””

<div class="header-box">
    <h1 style="margin:0; font-size:2.2rem; color:#fff;">Best Ball Value Hunter 🎯</h1>
    <p style="margin:6px 0 0; color:#8892b0; font-size:1rem;">
        Underdog Big Board Baseline · Value Delta · Risk-Adjusted Scoring · AI Narrative
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([“📸 Upload Screenshot”, “✏️ Manual Entry”, “📋 Big Board”])

with tab1:
st.markdown(”### Upload Underdog Roster Screenshot”)
st.caption(“Claude Vision extracts player names and ADPs automatically.”)
uploaded = st.file_uploader(“Upload screenshot (PNG or JPG)”, type=[“png”, “jpg”, “jpeg”])

```
if uploaded is not None:
    image_bytes = uploaded.read()
    ext = uploaded.name.split(".")[-1].lower()
    mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
    mime_type = mime_map.get(ext, "image/png")

    st.image(image_bytes, caption="Uploaded Roster", use_column_width=True)

    with st.spinner("Extracting players with Claude Vision..."):
        players, err = extract_roster_from_image(image_bytes, mime_type)

    if err:
        st.error("Vision extraction failed: " + err)
    elif not players:
        st.warning("No players found. Try a clearer screenshot.")
    else:
        st.success("Extracted " + str(len(players)) + " players!")
        st.session_state['results'] = process_roster(players, baseline_df)
```

with tab2:
st.markdown(”### Manual Roster Entry”)
st.caption(“One player per line. Format: Player Name, Current ADP (ADP is optional)”)

```
example_text = (
    "Bijan Robinson, 1.4\n"
    "Ja'Marr Chase, 3.8\n"
    "Trey McBride\n"
    "Josh Allen, 28.0\n"
    "CeeDee Lamb, 10.2"
)
raw_input = st.text_area("Paste your roster:", value=example_text, height=250)

if st.button("Analyze Roster", type="primary"):
    lines = [l.strip() for l in raw_input.strip().split("\n") if l.strip()]
    roster_entries = []
    for line in lines:
        parts = line.split(",")
        name = parts[0].strip()
        adp = None
        if len(parts) > 1:
            try:
                adp = float(parts[1].strip())
            except Exception:
                adp = None
        roster_entries.append({"name": name, "current_adp": adp})
    st.session_state['results'] = process_roster(roster_entries, baseline_df)
```

with tab3:
st.markdown(”### Full Big Board Baseline”)
st.caption(“Fixed ADP snapshot from the Underdog Big Board tournament drop.”)
st.dataframe(
baseline_df[[‘Player’, ‘Pos’, ‘ADP’, ‘+/-’, ‘%’, ‘sigma’]].rename(
columns={‘sigma’: ‘Volatility (sigma)’}
),
use_container_width=True,
hide_index=True
)

# ── RESULTS ───────────────────────────────────────────────────────────────────

if ‘results’ in st.session_state:
results_df = st.session_state[‘results’]

```
st.markdown("---")
st.markdown("## Team Analysis")

valid_scores = results_df['Risk Score'].dropna().tolist()
team_score, grade, title = team_rating(valid_scores)
g_color = grade_color(grade)
emoji = grade_emoji(team_score)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Players Analyzed", len(results_df))
with c2:
    matched_count = (results_df['Matched'] != 'No match').sum()
    st.metric("Matched to Board", matched_count)
with c3:
    steals_count = results_df[results_df['Value Delta'].notna() & (results_df['Value Delta'] > 3)].shape[0]
    st.metric("Steals (Delta > 3)", steals_count)
with c4:
    reaches_count = results_df[results_df['Value Delta'].notna() & (results_df['Value Delta'] < -3)].shape[0]
    st.metric("Reaches (Delta < -3)", reaches_count)

grade_html = (
    "<div class='grade-box'>"
    "<div style='font-size:3.5rem; font-weight:800; color:" + g_color + ";'>" + grade + "</div>"
    "<div style='font-size:1.4rem; color:#fff; margin-top:4px;'>" + title + " " + emoji + "</div>"
    "<div style='font-size:1rem; color:#8892b0; margin-top:4px;'>Team Score: "
    + str(team_score) + " / 100</div>"
    "</div>"
)
st.markdown(grade_html, unsafe_allow_html=True)

if st.button("Generate AI Narrative Summary 🤖"):
    with st.spinner("Cooking up spicy takes..."):
        narrative = generate_narrative(results_df, grade, title, team_score)
    narrative_html = (
        "<div style='background:#12172a; border:1px solid #2a3050; border-radius:12px;"
        " padding:20px; margin:16px 0;'>"
        "<p style='color:#e8eaf0; font-size:1rem; line-height:1.7; margin:0;'>"
        + narrative +
        "</p></div>"
    )
    st.markdown(narrative_html, unsafe_allow_html=True)

st.markdown("### Player Value Table")

display_cols = ['Player', 'Matched', 'Pos', 'Baseline ADP', 'Current ADP', 'Value Delta', 'Risk Score', 'Confidence']
display_df = results_df[display_cols].copy()

def style_row(row):
    delta = row['Value Delta']
    styles = [''] * len(row)
    try:
        idx = list(display_df.columns).index('Value Delta')
        if delta is not None and not (isinstance(delta, float) and np.isnan(delta)):
            styles[idx] = color_delta(delta)
    except Exception:
        pass
    return styles

styled = display_df.style.apply(style_row, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

chart_df = results_df[results_df['Value Delta'].notna()].copy()

if not chart_df.empty:
    st.markdown("### Value Delta Chart")
    chart_sorted = chart_df.sort_values('Value Delta', ascending=True)
    bar_colors = ['#00ff88' if v > 0 else '#ff4444' for v in chart_sorted['Value Delta']]

    fig_bar = go.Figure(go.Bar(
        x=chart_sorted['Value Delta'],
        y=chart_sorted['Player'],
        orientation='h',
        marker_color=bar_colors,
        text=chart_sorted['Value Delta'].apply(lambda x: ('+' if x > 0 else '') + str(round(x, 1))),
        textposition='outside'
    ))
    fig_bar.update_layout(
        paper_bgcolor='#0a0e1a',
        plot_bgcolor='#12172a',
        font_color='#e8eaf0',
        height=max(300, len(chart_sorted) * 32),
        margin=dict(l=20, r=60, t=20, b=20),
        xaxis_title='Value Delta (positive = steal)',
        xaxis=dict(gridcolor='#1e2640'),
        yaxis=dict(gridcolor='#1e2640')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### Positional Breakdown")
    pos_group = chart_df.groupby('Pos')['Value Delta'].mean().reset_index()
    pos_group.columns = ['Position', 'Avg Value Delta']
    pos_color_map = {'RB': '#00ff88', 'WR': '#6699ff', 'TE': '#ff9944', 'QB': '#ffcc44'}
    bar_pos_colors = [pos_color_map.get(p, '#aab0c0') for p in pos_group['Position']]

    fig_pos = go.Figure(go.Bar(
        x=pos_group['Position'],
        y=pos_group['Avg Value Delta'],
        marker_color=bar_pos_colors,
        text=pos_group['Avg Value Delta'].round(1),
        textposition='outside'
    ))
    fig_pos.update_layout(
        paper_bgcolor='#0a0e1a',
        plot_bgcolor='#12172a',
        font_color='#e8eaf0',
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis_title='Avg Value Delta',
        xaxis=dict(gridcolor='#1e2640'),
        yaxis=dict(gridcolor='#1e2640')
    )
    st.plotly_chart(fig_pos, use_container_width=True)

st.markdown("### Export")
csv_out = results_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Results CSV",
    data=csv_out,
    file_name="best_ball_value_results.csv",
    mime="text/csv"
)
```

st.markdown(”””

<div style="text-align:center; color:#2a3060; font-size:11px; margin-top:40px;
font-family: monospace;">
BEST BALL VALUE HUNTER - UNDERDOG BIG BOARD BASELINE - FIXED ADP SNAPSHOT
</div>
""", unsafe_allow_html=True)
