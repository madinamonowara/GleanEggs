# Glean Eggs
Glean Eggs is a reactive web application designed to help users save time and money on grocery shopping. By combining real-time price tracking, AI-generated lists, and user preferences like dietary restrictions and budget, Glean Eggs empowers users to shop smarter—not harder.

# Description of system:
Generate AI-powered grocery lists based on personal preferences (e.g. vegan, budget-conscious).
Track real-time price changes and compare products side-by-side.
Access curated recipes and meal suggestions with direct links to add ingredients to their list.
Contribute price data they see in-store to improve the system’s accuracy.
Filter and explore products by category.

# Technologies Used
Frontend: HTML, CSS, JavaScript
Backend: Python, Flask
Database: Firebase Realtime Database
APIs:
TheMealDB
Bureau of Labor Statistics API
FoodFactFinder (grocery price data)
DeepSeek API (for AI-powered list generation)
Charts: Chart.js
Hosting: Heroku

# Dependencies:
Install these using pip:
pip install flask
pip install firebase-admin
pip install requests

Additional files needed:
- Firebase service account key (firebase-credentials.json)
- .env file (optional for API keys and config)

# Installation & Running Instructions
1. Clone the repository
git clone https://github.com/yourusername/glean-eggs.git
cd glean-eggs

2. Install Python dependencies
pip install -r requirements.txt
If you don’t have a requirements.txt, you can generate one:
pip freeze > requirements.txt

3. Add Firebase Credentials
Create a file firebase-credentials.json in the project root. You can download this from your Firebase project settings.

4. Run the Flask app
python main.py

Then visit http://127.0.0.1:5000 in your browser.

# Deployment:
We deployed Glean Eggs using Heroku.

1. Create a Procfile:
web: python main.py

2. Add and commit changes:
git add .
git commit -m "Prepare for deployment"

3. Push to Heroku:
heroku create
git push heroku main

4. Open the app:
heroku open


# Contributors

Zuzanna — Frontend (UI/UX, all the pages other than login, spinning egg, styling)
Madina — login page front+backend, fixing preferences bug
Shameed — Backend, AI logic, API integrations, data collection logic
Yana — Firebase logic, category systems

