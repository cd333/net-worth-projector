import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="AIzaSyBnBeq-SU03tBwFM_hPDWPNiFHa_uVwURo")  # Replace with your actual key
model = genai.GenerativeModel('gemini-2.5-flash')

print("=== Net Worth Projector ===\n")

current_net_worth = float(input("Current net worth: $"))
annual_savings = float(input("Annual savings: $"))
annual_return_rate = float(input("Expected annual return rate (as decimal, e.g., 0.07 for 7%): "))
years = int(input("Number of years to project: "))

# Collect life events using natural language
print("\nAdd major life events in natural language (or press Enter to skip)")
print("Examples: 'Buying a $80k car in year 3' or 'Expect $200k inheritance in year 5'")
life_events = {}

while True:
    event_input = input("\nDescribe event (or press Enter to finish): ")
    if event_input == "":
        break
    
    # Ask Gemini to parse the event
    prompt = f"""Extract the following information from this financial event description:
    "{event_input}"
    
    Return ONLY a JSON object with these fields:
    - year: the year number (integer)
    - amount: the dollar amount (negative for expenses, positive for income)
    - description: brief description
    
    Example output: {{"year": 3, "amount": -80000, "description": "car purchase"}}
    
    Return only the JSON, no other text."""
    
    response = model.generate_content(prompt)
    
    try:
        # Parse the JSON response
        import json
        # Clean up the response in case there are markdown code blocks
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        event_data = json.loads(response_text)
        year = event_data["year"]
        amount = event_data["amount"]
        description = event_data["description"]
        
        life_events[year] = {"amount": amount, "description": description}
        print(f"  ✓ Added: Year {year}, ${amount:,.0f} ({description})")
    except Exception as e:
        print(f"  ✗ Couldn't parse that. Try being more specific about the year and amount.")
        print(f"  Error: {e}")

# Use long-term average US inflation rate
inflation_rate = 0.031  # 3.1% - average US inflation 1913-2024

print(f"\nUsing {inflation_rate * 100}% inflation rate (long-term US average)")
print("Calculating...\n")

# Calculate real return rate
real_annual_return = (1 + annual_return_rate) / (1 + inflation_rate) - 1

# Year-by-year breakdown
future_value = current_net_worth
real_future_value = current_net_worth

print("Year | Nominal Value | Real Value (Today's $) | Event")
print("-" * 70)

for year in range(1, years + 1):
    # Add annual savings
    future_value += annual_savings
    real_future_value += annual_savings
    
    # Apply life event if it exists for this year
    event_note = ""
    if year in life_events:
        event = life_events[year]
        future_value += event["amount"]
        real_future_value += event["amount"]
        event_note = f"${event['amount']:,.0f}"
        if event["description"]:
            event_note += f" ({event['description']})"
    
    # Apply growth
    future_value *= (1 + annual_return_rate)
    real_future_value *= (1 + real_annual_return)
    
    print(f"{year:4} | ${future_value:13,.2f} | ${real_future_value:18,.2f} | {event_note}")

# Calculate total life events impact
total_events = sum(event["amount"] for event in life_events.values())

print("\n" + "=" * 70)
print(f"\nTotal contributions: ${annual_savings * years:,.2f}")
print(f"Total life events: ${total_events:,.2f}")
print(f"Nominal investment growth: ${future_value - current_net_worth - (annual_savings * years) - total_events:,.2f}")
print(f"Real investment growth: ${real_future_value - current_net_worth - (annual_savings * years) - total_events:,.2f}")