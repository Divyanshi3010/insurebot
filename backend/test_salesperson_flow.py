
import requests
import json

url = "http://localhost:8000/chat"
headers = {"Content-Type": "application/json"}

def send_chat(messages):
    data = {"messages": messages}
    print(f"\nSending User Message: {messages[-1]['content']}")
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    try:
        res_json = response.json()
        print(f"Bot Response: {res_json['response']}")
        if res_json.get('recommendations'):
            print("Received Recommendations!")
        else:
            print("No Recommendations yet.")
            
        return res_json['response']
    except:
        print("Error parsing response")
        return ""

# Step 1: Start Conversation
history = [{"role": "user", "content": "Hi, I am looking for insurance."}]
resp1 = send_chat(history)
history.append({"role": "model", "content": resp1})

# Step 2: Provide Age/Income
history.append({"role": "user", "content": "I am 30 years old and earn 20 Lakhs."})
resp2 = send_chat(history)
history.append({"role": "model", "content": resp2})
# EXPECTATION: Should mention cover amount, but NOT plans. Should ask next question.

# Step 3: Provide Occupation
history.append({"role": "user", "content": "I am a Software Engineer."})
resp3 = send_chat(history)
history.append({"role": "model", "content": resp3})

# Step 4: Provide Smoker status
history.append({"role": "user", "content": "No, I don't smoke."})
resp4 = send_chat(history)
history.append({"role": "model", "content": resp4})

# Step 5: Provide Gender (if asked)
history.append({"role": "user", "content": "Male."})
resp5 = send_chat(history)
