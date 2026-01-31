import pandas as pd
import json
import os

class InsuranceEngine:
    def __init__(self):
        # 1. LOAD THE REAL CLAIMS CSV
        try:
            # Absolute path calculation to avoid FileNotFoundError
            base_path = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_path, "data", "insurance_claims_dataset.csv")
            json_path = os.path.join(base_path, "data", "products_config.json")
            
            # Check if files exist
            if not os.path.exists(csv_path):
                print(f"❌ CSV NOT FOUND at: {csv_path}")
                self.claims_df = pd.DataFrame()
            else:
                self.claims_df = pd.read_csv(csv_path)
                print("✅ CSV Loaded Successfully")

            if not os.path.exists(json_path):
                print(f"❌ JSON NOT FOUND at: {json_path}")
                self.product_data = {}
            else:
                with open(json_path, "r") as f:
                    self.product_data = json.load(f)
                print("✅ Product Config Loaded Successfully")
            
            # Load Eligibility CSV
            eligibility_csv_path = os.path.join(base_path, "data", "term_insurance_eligibility.csv")
            if not os.path.exists(eligibility_csv_path):
                print(f"❌ Eligibility CSV NOT FOUND at: {eligibility_csv_path}")
                self.eligibility_df = pd.DataFrame()
            else:
                self.eligibility_df = pd.read_csv(eligibility_csv_path)
                print("✅ Eligibility CSV Loaded Successfully")
            
            # --- DATA CLEANING ---
            if not self.claims_df.empty:
                # Rename columns safely
                rename_map = {
                    'Company': 'Company',
                    'Claims_Paid_Ratio_Death': 'CSR',      
                    'Solvency_2025': 'Solvency'
                }
                # Only rename columns that actually exist
                self.claims_df.rename(columns={k: v for k, v in rename_map.items() if k in self.claims_df.columns}, inplace=True)

                # Clean percentage signs
                if 'CSR' in self.claims_df.columns and self.claims_df['CSR'].dtype == 'object':
                    self.claims_df['CSR'] = self.claims_df['CSR'].str.replace('%', '').astype(float)
                
                # Ensure Solvency is numeric
                if 'Solvency' in self.claims_df.columns:
                    self.claims_df['Solvency'] = pd.to_numeric(self.claims_df['Solvency'], errors='coerce').fillna(0)
                
        except Exception as e:
            print(f"❌ CRITICAL ERROR initializing engine: {e}")
            self.claims_df = pd.DataFrame()
            self.product_data = {}
            self.eligibility_df = pd.DataFrame()

    def get_eligibility_context(self):
        """
        Returns a formatted string of eligibility conditions from the CSV.
        """
        if self.eligibility_df.empty:
            return "No eligibility data available."
        
        context = "### Term Insurance Eligibility Conditions:\n"
        for _, row in self.eligibility_df.iterrows():
            category = row.get('Category', 'General')
            condition = row.get('Condition / Profile', 'Unknown')
            impact = row.get('Impact on Eligibility', 'Review needed')
            context += f"- **{category}**: If user matches '{condition}', then: {impact}\n"
        
        return context

    def calculate_needs(self, income, liabilities, age, assets=0):
        # Age-based multipliers
        multiplier = 20 # Fallback
        
        if 18 <= age <= 35:
            multiplier = 25
        elif 36 <= age <= 40:
            multiplier = 20
        elif 41 <= age <= 45:
            multiplier = 15
        elif 46 <= age <= 50:
            multiplier = 12
        elif 51 <= age <= 55:
            multiplier = 10
        elif 56 <= age <= 60:
            multiplier = 5
            
        print(f"💰 Calculating Needs: Age={age}, Income={income}, Liabilities={liabilities}, Assets={assets}, Multiplier={multiplier}x")
        
        # Formula: (Income * Multiplier) + Liabilities - Assets
        total_needs = (income * multiplier) + liabilities - assets
        
        # Ensure it doesn't go below zero (or some minimum sensible basic cover, but strict math says 0)
        return float(max(total_needs, 0))

    def estimate_premium(self, age, sum_insured, smoker, is_rop, gender, company_name="Unknown", cover_type="Flat", policy_type="Pure Term"):
        base_rate = 12000
        
        # Company Tier Factors (Simulated Market Rates)
        # Tier 1 (Premium Brands) -> Higher Cost
        # Tier 2 (Value Brands) -> Medium Cost
        # Tier 3 (Budget Brands) -> Lower Cost
        company_factors = {
            "HDFC Life": 1.15,
            "ICICI Prudential": 1.12,
            "SBI Life": 1.10,
            "Max Life": 1.05,
            "Bajaj Allianz Life": 1.00, # Benchmark
            "TATA AIA": 1.02,
            "Kotak Life": 0.95,
            "Pramerica Life": 0.90,
            "Aditya Birla": 1.00
        }
        
        # Default to 1.0 if company not found
        market_factor = 1.0
        for key, val in company_factors.items():
            if key.lower() in str(company_name).lower():
                market_factor = val
                break
        
        cover_factor = sum_insured / 10000000
        age_factor = 1 + ((age - 30) * 0.05) if age > 30 else 1
        smoker_factor = 1.5 if smoker else 1.0
        rop_factor = 1.9 if is_rop else 1.0
        gender_factor = 0.85 if str(gender).lower() == "female" else 1.0
        
        # Cover Type Factor
        cover_type_factor = 1.0
        ct_lower = str(cover_type).lower()
        if "increasing" in ct_lower:
            cover_type_factor = 1.2
        elif "decreasing" in ct_lower:
            cover_type_factor = 0.9
            
        # Policy Type Factor
        policy_type_factor = 1.0
        pt_lower = str(policy_type).lower()
        
        if "joint" in pt_lower:
            policy_type_factor = 1.7 # Spouse cover cost
        elif "tulip" in pt_lower or "unit linked" in pt_lower:
            policy_type_factor = 1.5 # Investment component
        elif "return of premium" in pt_lower:
            rop_factor = 1.9 # Ensure ROP factor is applied if selected here
        elif "increasing" in pt_lower or "increased" in pt_lower:
             cover_type_factor = 1.2 # Ensure Increasing factor is applied
        
        # Return standard int
        return int(round(base_rate * cover_factor * age_factor * smoker_factor * rop_factor * gender_factor * market_factor * cover_type_factor * policy_type_factor))

    def calculate_suitability_score(self, user_data, policy_details):
        if not policy_details:
            return -50 # Penalty for unknown policies
            
        score = 0
        
        # 1. Eligibility Check (Hard Constraints)
        eligibility = policy_details.get('eligibility', {})
        min_age = eligibility.get('min_age', 18)
        max_age = eligibility.get('max_age', 65)
        min_income = eligibility.get('min_income', 0)
        
        user_age = int(user_data.get('age', 30))
        user_income = float(user_data.get('income', 0))
        
        if user_age < min_age or user_age > max_age:
            return -1000 # Disqualify
            
        if user_income < min_income:
            return -1000 # Disqualify

        # 2. Feature Matching (Soft Constraints)
        features = policy_details.get('features', {})
        user_wants_rop = bool(user_data.get('is_rop', False))
        
        # ROP Matching
        if user_wants_rop:
            if features.get('rop'):
                score += 20 # Strong Boost for exact match
            else:
                score -= 30 # Strong Penalty if requirement not met
        elif features.get('rop'):
             # If user didn't ask for ROP but policy has it, it usually costs more. 
             # We let the premium penalty handle the cost, but maybe slight unmatched penalty?
             # actually, ROP plans are good, maybe neutral.
             pass

        # Budget Matching
        if user_income < 500000:
            if features.get('cheap'):
                score += 15 # Boost for budget-friendly plans for lower income
        
        # General Feature Bonuses
        if features.get('critical_illness'):
            score += 5
        if features.get('wop'): # Waiver of Premium
            score += 3
        if features.get('govt_backed'):
            score += 2
        if features.get('whole_life'):
            score += 2
        
        print(f"    ℹ️ Suitability for {policy_details['metadata']['product_name']}: {score}")
        return score

    def get_recommendation(self, user_data):
        print(f"⚙️ Processing Recommendation for: {user_data}")
        
        if self.claims_df.empty:
            print("⚠️ Claims DataFrame is empty. Cannot recommend.")
            return {"error": "Data not loaded correctly"}

        try:
            age = int(user_data.get('age', 30))
            income = float(user_data.get('income', 1000000))
            liabilities = float(user_data.get('liabilities', 0))
            smoker = bool(user_data.get('smoker', False))
            is_rop = bool(user_data.get('is_rop', False))
            gender = str(user_data.get('gender', 'Male'))
            cover_type = str(user_data.get('cover_type', 'Flat'))
            policy_type = str(user_data.get('policy_type', 'Pure Term'))

            recommended_cover = self.calculate_needs(income, liabilities, age)

            results = []
            
            for _, row in self.claims_df.iterrows():
                company = str(row.get('Company', 'Unknown'))
                
                # Match Policy
                matching_policies = []
                for p in self.product_data.get('policies', []):
                    if company.lower() in p['metadata']['insurer_name'].lower():
                        matching_policies.append(p)
                
                policy_details = None
                
                # Filter based on Policy Type Preference
                user_policy_type = str(user_data.get('policy_type', 'Pure Term')).lower()
                
                # Debug: Print what we are looking for
                # print(f"    🔍 Looking for policy type: '{user_policy_type}' for {company}")

                for p in matching_policies:
                    meta = p.get('metadata', {})
                    brochure_type = str(meta.get('brochure_type', '')).lower()
                    product_cat = str(meta.get('product_category', '')).lower()
                    
                    # Logic to select best fit
                    if "tulip" in user_policy_type or "unit linked" in user_policy_type:
                        if "ulip" in brochure_type or "unit linked" in product_cat:
                            policy_details = p
                            break
                    elif "return of premium" in user_policy_type:
                        if "return of premium" in brochure_type or "savings" in product_cat:
                            policy_details = p
                            break
                    else: # Default to Pure Term
                        # Strict check: Must be a Term Insurance or generic Pure Risk product
                        if "term insurance" in brochure_type or "pure risk" in product_cat:
                            # ensuring we don't accidentally pick a ULIP/ROP if brochure_type is vague but category isn't
                            if "unit linked" not in product_cat and "savings" not in product_cat:
                                policy_details = p
                                break
                
                # STRICT POLICY: If no specific match found, SKIP this company.
                # Do NOT fallback to matching_policies[0].
                if not policy_details:
                    # print(f"    ❌ No matching policy found for {company} (Req: {user_policy_type}). Skipping.")
                    continue


                # Default values if no metadata
                if policy_details:
                    product_name = policy_details['metadata']['product_name']
                    # Get features description
                    features_dict = policy_details.get('features', {})
                    # Try to get USP from various fields
                    usp = features_dict.get('description')
                    if not usp:
                         usp = policy_details.get('metadata', {}).get('marketing_tagline')
                    if not usp:
                        usp = "Comprehensive Coverage"
                else:
                    # If matches found in Claims but not in Product Config, skip it to avoid hallucinations
                    continue

                # Calculate Suitability
                suitability_score = self.calculate_suitability_score(user_data, policy_details)
                
                # If disqualified, skip
                if suitability_score <= -900:
                    continue

                est_premium = self.estimate_premium(
                    age, recommended_cover, smoker, is_rop, gender, company, cover_type, policy_type
                )
                
                csr_val = float(row.get('CSR', 0))
                solvency_val = float(row.get('Solvency', 0))
                
                # Enhanced Score Logic:
                # 1. Base Score = CSR (approx 95-99)
                # 2. Solvency Bonus = Solvency * 2 (approx 3-6 points)
                # 3. Suitability Score = (-30 to +20 points)
                # 4. Premium Penalty = Premium / 2500 (approx 5-20 points) - Reduced weight to prioritize fit
                
                premium_penalty = est_premium / 2500
                score = float(csr_val + (solvency_val * 2) + suitability_score - premium_penalty)

                results.append({
                    "company": company,
                    "product_name": str(product_name),
                    "usp": str(usp),
                    "premium_estimate": int(est_premium),
                    "csr": csr_val,
                    "solvency": solvency_val, # Expose Solvency for detailed trust analysis
                    "score": score,
                    "suitability": suitability_score,
                    "features": features_dict # Pass full features for detailed explanation
                })

            # Sort by Score
            sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
            top_3 = sorted_results[:3]

            print(f"✅ Generated {len(top_3)} recommendations")
            
            return {
                "analysis": {
                    "recommended_cover": float(recommended_cover),
                    "logic": f"Calculated based on 20x annual income ({income}) plus liabilities ({liabilities})."
                },
                "recommendations": top_3
            }
        except Exception as e:
            print(f"❌ Logic Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}