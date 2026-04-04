# GigShield: AI-Powered Parametric Insurance for Gig Workers

## 🚀 The Problem We're Solving
India's gig economy employs millions of delivery partners (Swiggy, Zepto, Blinkit) who earn their livelihood entirely on an hourly, per-delivery basis. They face devastating income loss during extreme, localized anomalies—whether it's highly severe Bengaluru monsoons, toxic smog/AQI spikes, lethal heatwaves, civic curfews, or even central platform server outages. Traditional insurance completely ignores "daily wage loss," and typical claim processes are bureaucratic, slow, and inaccessible to this demographic. 

## 💡 What Inspired Us
Seeing delivery workers huddled under overpasses during sudden, intense rains. They aren't just getting wet; they are losing their daily bread with absolutely zero safety blanket. We realized that if a Q-commerce platform can deliver groceries in 10 minutes, we should be able to deliver an insurance payout in 10 minutes—without making the worker dial a number or fill out a form.

## 🛠️ Our Solution
GigShield is an automated, native Android parametric insurance platform. Workers purchase a highly affordable, dynamic weekly policy. Our backend relies on continuous background monitor jobs that constantly poll public civic and environmental Data APIs (OpenWeatherMap, AQICN). 

If a disruption crosses a severe threshold in a worker's active delivery zone, it trips a **Zero-Touch Claim Workflow**. The worker does not lift a finger. The claim is natively generated, analyzed for fraud, and the payout is calculated and automatically transferred via UPI, instantly notifying the worker that their lost hours have been reimbursed.

**[📱 Try GigShield Now on Appetize.io](https://appetize.io/app/b_f7n2uvl2v7ptemrrokc5ncut6y)**

---

## 🔄 The Pivot: Original Plan vs. Updated LLM Architecture
**What was told before:** We originally architected our backend reliant on rigid, traditional Machine Learning patterns. The plan was to train an XGBoost Classifier for Risk Profiling and an Isolation Forest model (scikit-learn) for Fraud Detection anomaly scoring. 

**The Updated Plan & Implementation:** Halfway through our build phase, we had a major architectural breakthrough and pivoted to a fully **LLM-Driven Agentic System**. Instead of rigid ML boundaries, we successfully integrated the **Groq API running LLaMA-3.3-70B**. 
We feed hyper-local zone contexts, historic weather variables, and temporal worker data directly into specialized LLM computational prompts. The LLM natively evaluates the risk profile and performs associative reasoning for fraud synthesis (e.g., deducing temporal anomalies from spoofed GPS logic that a rigid Isolation Forest might overlook). *This allowed our platform to reason dynamically, rather than just threshold-match.*

## 🏗️ How We Built It
* **Frontend:** Built fully Native in Android (Kotlin + Jetpack Compose). We prioritized a native app over a PWA to ensure deep device sensor access (essential for future anti-spoofing).
* **Backend Pipeline:** Python FastAPI running async `APScheduler` cron-jobs polling real-time weather and civic nodes. 
* **The Brain:** Groq LLaMA models running localized inference at lightning-fast speeds to assign trust metrics, fraud probabilities, and payout structures. 

## 🧠 What We Learned & Challenges We Faced
* **The "Zero-Touch" Challenge:** Constructing an architecture where the user interaction is strictly zero required complex background orchestration. We had to ensure the background scheduled jobs seamlessly mapped geofenced API weather anomalies against granular database rows of worker policies concurrently.
* **LLM Determinism:** A massive hurdle we faced was prompt engineering the LLaMA model to ensure strictly formatted `JSON-only` outputs devoid of conversational fluff so that our backend parsers didn't break during automated claim fulfillment. 
* We learned that the phenomenal inference speed of the Groq acceleration engine fully validated our pivot away from traditional Scikit-Learn paradigms. It easily provided the sub-second latency required for real-time mobile UX.

## 🧮 The Mathematics of GigShield
We engineered a heavily tailored Premium logic. GigShield aligns pricing tightly with the worker's own earnings cycle (updating every Monday).

$$ Weekly Premium = P_{base} + \left( E_{weekly} \times 0.014 \right) + \left( R_{LLM} \times 1.5 \right) + S_{claims} $$

Where:
* $P_{base}$ = Minimum viable Base Premium (₹29)
* $E_{weekly}$ = Earnings linked component based on 7-day declarations
* $R_{LLM}$ = The dynamic `Risk Score` (1.0 to 10.0) calculated by the Groq LLaMA model based on the pin-code's seasonal data.
* $S_{claims}$ = Historical claim surcharge.

*Payout Equation during a parametric trigger:*
$$ Payout = \min\left( \left( H_{lost} \times R_{hourly} \times C_{rate} \right), \ C_{remaining} \right) $$

*(e.g., Rain pays out at 80% $C_{rate}$ against $H_{lost}$ hours, dynamically capped against the worker's remaining policy coverage $C_{remaining}$).*

## 🔮 Future Plans
We plan to scale our anti-spoofing measures by integrating cell-tower triangulation network mapping. This will allow the LLM to cross-validate hardware metrics against syndicate GPS-spoofing ring attacks to keep the liquidity pool impenetrable.
