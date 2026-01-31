import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="AIzaSyBnBeq-SU03tBwFM_hPDWPNiFHa_uVwURo")

model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("Say hello!")

print(response.text)