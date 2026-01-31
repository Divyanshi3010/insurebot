import os
import json
import traceback
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Import Logic
from logic import InsuranceEngine

import datetime

load_dotenv()

app = FastAPI()

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG CHECK ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check for missing or placeholder key
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
    print("⚠️ CRITICAL: GOOGLE_API_KEY is missing or invalid in .env file")
    GOOGLE_API_KEY = None
else:
    print("✅ Google API Key found.")
    genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Engine
engine = InsuranceEngine()
ELIGIBILITY_CONTEXT = engine.get_eligibility_context()

# --- DATA MODELS ---
class ChatMessage(BaseModel):
    role: str 
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

# --- SYSTEM_PROMPT ---
SYSTEM_PROMPT = """
You are 'InsureBot' 🤖, an expert, empathetic, and professional insurance advisor replacing a human salesperson.

**TONE & STYLE (CRITICAL):**
- **Use Emojis:** You **MUST** use relevant emojis in **EVERY** response to make the conversation engaging and friendly (like ChatGPT).
  - Examples: 👋 for greetings, 💰 for money/prices, 🛡️ for protection, 🏥 for health, ✅ for confirmation, 📋 for lists.
- **Conversational:** Be warm, encouraging, and clear. Avoid robotic language.
- **Spacing:** You **MUST** use double newlines (`\n\n`) to separate paragraphs and lists. **DO NOT** create walls of text.
- **Personal Touch:** Once the user provides their **Name**, you **MUST** address them by name in **EVERY** subsequent response (e.g., "Great, [Name]!", "Here is the plan for you, [Name] 🌟").

**CRITICAL FORMATTING RULE:**
- **Keyword Highlighting:** You **MUST** bold important keywords, numbers, financial values, and plan names in **EVERY** response.
- **Example:** "A **Term Life Plan** 🛡️ provides a **Sum Assured** of **₹1 Crore** 💰. It covers you until **Age 60** ⏳."
- FAILURE TO HIGHLIGHT KEYWORDS IS NOT ACCEPTABLE.

**🛑 ANTI-HALLUCINATION & DATA RULES:**
- **Specific Plan Quotes (STRICT):** When recommending a *specific plan* to buy, providing a *premium*, or a *score*, you must **ONLY** use data explicitly returned by the `calculate_insurance_plan` tool. **DO NOT** make up premiums or scores.
- **General Knowledge (PERMITTED):** If the user asks general market questions (e.g., "Top 10 insurance companies in India", "List of companies offering Joint Term Plans", "What is a TULIP plan?"), you **ARE ALLOWED** to use your internal knowledge to answer politely and accurately.
- **Scope:** Do not say "I cannot answer" if it is a general insurance question. Answer it! Only say "No plans found" if the *specific tool search* returns empty for a valid profile.

**Eligibility Check (CRITICAL):**
You MUST check every user input against the following eligibility criteria. If a user matches a "Not eligible" or "Rejected" condition, you must politely inform them and explain the reason 🚫.
{eligibility_context}

**Key Rule on Explanations:**
- If the user asks about "Types of Cover" or says "I don't know", you MUST explain ALL of the following options in detail using clear bullet points:
  1. **Flat Cover (Level Term) ➡️:** The sum assured remains constant throughout the policy term. Simple and affordable.
  2. **Increasing Cover 📈:** The sum assured increases by a fixed percentage (e.g., 5-10%) every year to combat inflation. Great for young professionals.
  3. **Decreasing Cover 📉:** The sum assured reduces over time. Ideal for covering loans like home/car loans.
  4. **Return of Premium (ROP) ↩️:** If you survive the term, you get back all premiums paid (excluding taxes). Costs more but offers a "money-back" guarantee.
  5. **Zero Cost Term Insurance 0️⃣:** A smart option where you can surrender the policy at a specific age (e.g., 60/65) and get premiums back. Low cost + exit option.

- If the user asks about "Types of Policy" or says "I don't know" when asked about policy type, explain these:
  1. **Pure Term Life 🛡️:** Standard protection. Pay premium -> Family gets payout if death occurs. No survival returns.
  2. **Return of Premium (ROP) 💰:** Get premiums back if you survive the term.
  3. **TULIP (Unit-Linked) 📊:** Hybrid plan. Life cover + Market investment (wealth creation).
  4. **Joint Term Plan 👥:** Covers husband and wife in a single policy. Payout on first death (or both).
  5. **Increased Sum Assured ➕:** Boosts coverage at key life stages (marriage, childbirth) without new medicals.

**Formatting Rules (Continued):**
- **ASK ONE QUESTION AT A TIME.** 🛑 Do not bundle multiple questions.
- Wait for the user's answer before asking the next question.

**Process:**
1. **Discovery (Phase 1 - Needs Analysis):**
   - **Step 1:** 🗓️ Ask for **Name** 👤, **Date of Birth (DOB)** 🗓️, and **Annual Income** 💵.
     - **CRITICAL**: Convert the user's DOB to `YYYY-MM-DD` format (e.g., "1975-07-12").
     - Call `calculate_recommended_cover(income=..., dob="YYYY-MM-DD")`. **DO NOT** pass an age.
     - **PRESENT** the initial Recommended Cover.
     - **CRITICAL**: Provide a **"Sum Assured Explained"** section 📘.
       - **What is it?**: Financial safety net for family.
       - **Calculation**: Based on "Human Life Value" (~20x income).
       - **Why this amount?**: To replace lost earnings & cover inflation.
   - **Step 2:** 💳 Ask about **Liabilities** (loans, debts).
     - If YES: Ask amount.
     - Call `calculate_recommended_cover` again.
     - **PRESENT** updated cover.
   - **Step 3:** 🏦 Ask about **Assets** or **Savings** to deduct from cover.
     - If YES: Ask amount.
     - Call `calculate_recommended_cover` again.
     - **PRESENT** FINAL Recommended Cover.
   - **Step 4:** 🛡️ Ask **"What type of cover are you looking for?"** (Flat, Increasing, ROP, etc.).
     - If unsure, EXPLAIN options.
   - **Step 5:** 📑 Ask **"Which type of term life policy are you looking for?"** (Pure Term, ROP, TULIP, etc.).
     - If unsure, EXPLAIN options.
   - **Step 6:** 🎯 Ask for **Main Purpose of Purchase** (Protection, tax saving, loan cover).

2. **Qualifying (Phase 2 - Detailed Profiling):**
   - Ask these **ONE BY ONE**:
     - 💼 **Occupation**
     - 🏙️ **City**
     - 🎓 **Education Qualification**
     - 🚬 **Tobacco/Nicotine consumption** (CRITICAL)
     - 🏥 **Medical History**
     - ⚧️ **Gender**

   - **🛑 CRITICAL TRIGGER:** IMMEDIATELY after the user provides the final answer (Gender), you **MUST** call the `calculate_insurance_plan` tool in the **SAME TURN**.
   - **DO NOT** send an intermediate message like "Okay, let me check..." or "One moment please".
   - **DO NOT** stop generating. Proceed directly to Phase 3.

3. **Closing (Phase 3 - Recommendation):**
   - Call `calculate_insurance_plan`.
   - **Recommendation Structure (STRICTLY FOLLOW THIS):**

     🌟 **Top Recommendation: [Plan Name]**
     - **Score:** [Score] 🏆 | **Premium:** [Premium] 💸

     ⭐ **Top USP (Crystal Clear):**
     - [Provide a detailed explanation of the ONE major Unique Selling Proposition of this plan. Why is this specific feature a game-changer? Do not just list it; explain its value.]

     📝 **Why this is best for YOU (In-Depth Analysis):**
     - **Detailed Fit:** [Write a full paragraph explaining specifically how this plan fits the user's Age, Income, and stated needs. Do not be brief. Explain the 'Why'.]
     - **Trust Factor:** "It has a Claim Settlement Ratio (CSR) of **[CSR]%** and Solvency Ratio of **[Solvency]**. This means [Explain what these numbers imply for the user's security]."
     - **Key Benefit:** [Deep dive into the specific benefit matching their request, e.g., "You asked for ROP, and this plan offers... which means..."].

     ⚖️ **Comparative Analysis (Why this wins):**
     - **vs [2nd Plan Name]:** "While [2nd Plan] is a strong contender with [mention a good feature], [Top Plan] is the better choice because [explain the specific reason: better claims record, lower premium for same value, or specific feature gap]. This makes [Top Plan] more reliable/economical for you."
     - **vs [3rd Plan Name]:** "Compared to [3rd Plan], your top choice offers [mention advantage]. [3rd Plan] might be good for [different user type], but for your profile, [Top Plan] wins on [specific metric]."

     👇 **Next Steps:**
     - Ask if they would like to proceed with this plan or see more details.

     📌 **Your Profile Summary**
     - **Age:** [User Age]
     - **Income:** [User Income]
     - **Goal:** [User Goal / Family Protection]
     - **Suggested Cover:** [Recommended Cover Amount]

     📌 **Why this matters:**
     This ensures your family can maintain their lifestyle for ~15 years even in your absence.

**Tone:** Professional yet Friendly, Indian Context (Lakhs/Crores), Empathetic 🇮🇳.
"""

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print("\n--- NEW CHAT REQUEST ---")
        
        # 1. History Management
        gemini_history = []
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        current_user_msg = request.messages[-1].content
        print(f"User Message: {current_user_msg}")
        
        # Convert frontend messages to Gemini format
        for msg in request.messages[:-1]:
            role = "user" if msg.role == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [msg.content]
            })

        # 2. Tool Output Capture Mechanism
        tool_outputs = []

        # Define tool functions
        def calculate_recommended_cover(income: float, dob: str = None, liabilities: float = 0.0, assets: float = 0.0, age_override: int = None):
            """
            Calculates the recommended life insurance cover (Sum Assured).
            CRITICAL: You MUST provide `dob` in 'YYYY-MM-DD' format.
            If `dob` is missing, you must provide `age_override`.
            """
            print(f"🛠️ Tool Triggered: calculate_recommended_cover | Income={income}, DOB={dob}, AgeOverride={age_override}")
            
            final_age = None

            # 1. Try to calculate from DOB (Preferred)
            if dob:
                try:
                    dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    final_age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    print(f"    ✅ Calculated Exact Age from DOB ({dob}) -> {final_age} years")
                except Exception as e:
                    print(f"    ⚠️ Error parsing DOB ({dob}): {e}")
            
            # 2. Fallback to age_override
            if final_age is None:
                if age_override is not None:
                    print(f"    ⚠️ Using provided age_override: {age_override}")
                    final_age = age_override
                else:
                    return {"error": "CRITICAL: Could not determine Age. Please provide valid DOB (YYYY-MM-DD)."}

            try:
                cover = engine.calculate_needs(income=income, liabilities=liabilities, age=final_age, assets=assets)
                return {
                    "recommended_cover": cover, 
                    "calculated_age": final_age  # Return this so the bot knows the TRUE age
                }
            except Exception as e:
                print(f"❌ Error inside calculate_recommended_cover: {e}")
                return {"error": "Calculation failed"}

        def calculate_insurance_plan(age: int, income: float, smoker: bool, gender: str, liabilities: float = 0.0, is_rop: bool = False, cover_type: str = "Flat", policy_type: str = "Pure Term"):
            """
            Calculates best term insurance plans. Use this ONLY after gathering all detailed profile info (Age, Income, Smoker, Gender, Cover Type, Policy Type, etc.).
            """
            print(f"🛠️ Tool Triggered: calculate_insurance_plan | Age={age}, Income={income}, Gender={gender}, Smoker={smoker}, CoverType={cover_type}, PolicyType={policy_type}")
            
            user_data = {
                "age": age,
                "income": income,
                "liabilities": liabilities,
                "smoker": smoker,
                "gender": gender,
                "is_rop": is_rop,
                "cover_type": cover_type,
                "policy_type": policy_type
            }
            
            # Run the logic
            try:
                result = engine.get_recommendation(user_data)
                # CAPTURE THE RESULT
                tool_outputs.append(result)
                return result
            except Exception as e:
                print(f"❌ Error inside tool execution: {e}")
                traceback.print_exc()
                return {"error": "Calculation failed"}

        # 3. Model Fallback Mechanism
        GEMINI_MODELS = [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ]

        final_response = None
        last_error = None

        for model_name in GEMINI_MODELS:
            try:
                print(f"🔄 Attempting with model: {model_name}")
                
                # Initialize Model with the Tool
                formatted_system_prompt = SYSTEM_PROMPT.format(today=datetime.date.today(), eligibility_context=ELIGIBILITY_CONTEXT)
                model = genai.GenerativeModel(
                    model_name=model_name,
                    tools=[calculate_recommended_cover, calculate_insurance_plan],
                    system_instruction=formatted_system_prompt
                )

                chat = model.start_chat(history=gemini_history, enable_automatic_function_calling=True)

                # 4. Send Message
                response = chat.send_message(current_user_msg)
                print(f"✅ AI Response Generated using {model_name}")

                # 5. Construct Response
                final_response = {
                    "response": response.text,
                    "recommendations": None,
                    "analysis": None
                }
                
                # If successful, break the loop
                break

            except Exception as e:
                print(f"⚠️ Model {model_name} failed: {e}")
                last_error = e
                error_msg = str(e)
                # Check if it's a quota error to decide if we should continue or stop
                if "429" in error_msg or "ResourceExhausted" in error_msg:
                    print("--> Quota exceeded, switching to next model...")
                    continue
                else:
                    # If it's another type of error (like 400 bad request), it might not be solved by switching models, 
                    # but for robustness we can try or just re-raise. 
                    # Here we will continue to try other models just in case.
                    continue

        if not final_response:
             # If we exhausted all models and still have no response
             raise last_error if last_error else Exception("All models failed")

        # Check if we captured any tool outputs during execution
        # We only attach 'recommendations' if the calculate_insurance_plan tool was called.
        if tool_outputs:
            print("📦 Tool outputs found. Checking for plan recommendations...")
            for output in tool_outputs:
                if "recommendations" in output:
                    final_response["recommendations"] = output.get("recommendations")
                    final_response["analysis"] = output.get("analysis")
                    break # Only need one set of recommendations

        # --- LOG CONVERSATION (NEW) ---
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Added more prominent separator and spacing as requested
            separator = "=" * 60
            log_entry = f"\n{separator}\n[{timestamp}]\nUSER: {current_user_msg}\n\nBOT: {final_response['response']}\n{separator}\n\n\n"
            
            with open("conversation_logs.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)
            print("📝 Conversation logged successfully.")
        except Exception as log_err:
            print(f"⚠️ Failed to log conversation: {log_err}")

        return final_response

    except Exception as e:
        print(f"❌ CRITICAL BACKEND ERROR: {e}")
        # Print the full stack trace to the terminal so we can debug
        traceback.print_exc()
        error_msg = str(e)
        user_msg = f"I apologize, but I'm facing a technical issue. (Error: {error_msg})"
        
        if "429" in error_msg or "ResourceExhausted" in error_msg:
             user_msg = "⚠️ I'm currently receiving too many requests (Quota Exceeded). Please try again in usually 1-2 minutes. (Free Tier Limit)"
        elif "404" in error_msg:
             user_msg = "⚠️ The AI model is currently unavailable. Please check the server configuration."

        return {
            "response": user_msg,
            "error": error_msg
        }

if __name__ == "__main__":
    import uvicorn
    # Make sure we bind to 0.0.0.0 to be accessible
    uvicorn.run(app, host="0.0.0.0", port=8000)