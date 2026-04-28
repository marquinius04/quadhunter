# Quadhunter 🏍️
Quadhunter is a real-time web scraping and visualization tool designed to find Quad and ATV listings. It leverages headless browser automation to extract the newest ads in Wallapop from the motorcycles category and utilizes Machine Learning (TF-IDF similarity) to accurately distinguish between quads and motorcycles, delivering results through a live-streaming web interface.


https://github.com/user-attachments/assets/f91748ef-d617-4dda-b95a-21f706a66af8


# Features 🚀
- Real-time Scraping: Powered by Playwright, the scraper navigates through listings and extracts data on the fly.

- Intelligent Filtering: Uses TF-IDF Vectorization and Cosine Similarity to ensure that listings categorized as "motorcycles" but named like "quads" are correctly identified (and vice versa).

- SSE Streaming: Results are sent from the Python backend to the frontend using Server-Sent Events (SSE), meaning you don't have to refresh the page to see new results.

- Modern UI: A sleek, dark-themed interface featuring a CSS-only Carousel with dynamic JavaScript injection and smooth text animations.

- Resource Optimized: Automatically blocks unnecessary web assets (images, fonts, stylesheets) during the initial crawl to minimize bandwidth and maximize speed.


# Tech stack 🛠
**Frontend:** HTML5, CSS3

**Backend:** Python, Flask

**Scraping:** Playwright

**Data Analysis:** Scikit-learn (Smart keyword weighting & Pattern matching)
# Installation 📦
1. Clone the repository:
```
git clone https://github.com/youruser/quadhunter.git
cd quadhunter
```

2. Install dependencies:
```
pip install flask playwright scikit-learn
```
3. Install the browser engine:
```
playwright install chrome
```
# Usage 🚦
1. Start the application:
```
python app.py
```
2. Open your browser:

Navigate to http://127.0.0.1:5000.

3. Watch the results:

The scraper will begin its search. As soon as a valid Quad listing is found and verified by the similarity engine, it will slide into the carousel automatically.
# Project structure 🏗
```
.
├── app.py              # Flask server and UI logic
├── quadhunter.py       # Scraper engine and similarity logic
├── static/
│   └── fonts/          # Custom typography (Braaap, Cross, Rickey)
└── README.md           # Project documentation
```
# How it works 🧠
## The similarity engine
Because Wallapop mixes some categories into one single bigger one, the script uses a pre-trained set of keywords for Quads and Motorcycles. When an ad is found, its title is transformed into a vector and compared against these sets. If the "Quad score" is significantly higher than the "Motorcycle score," the listing is accepted.

## The live feed
The frontend uses a EventSource to listen to the /stream_search endpoint. Instead of waiting for the scraper to finish the entire search, the server "yields" each result individually. This creates a low-latency experience where quads appear on your screen the moment they are discovered.
