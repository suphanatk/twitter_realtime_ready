from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from config import TWITTER_USERNAMES

app = Flask(__name__)
socketio = SocketIO(app)
latest_posts = {}

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(options=chrome_options)

def scrape_tweets():
    global latest_posts
    while True:
        driver = get_driver()
        for username in TWITTER_USERNAMES:
            try:
                driver.get(f"https://x.com/{username}")
                time.sleep(5)
                elements = driver.find_elements(By.XPATH, "//div[@data-testid='tweetText']")
                if elements:
                    tweet = elements[0].text.strip()
                    if latest_posts.get(username) != tweet:
                        latest_posts[username] = tweet
                        socketio.emit("new_post", {"username": username, "text": tweet})
            except Exception as e:
                print(f"[ERROR] ดึงโพสต์ของ {username} ไม่ได้: {e}")
        driver.quit()
        time.sleep(30)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    threading.Thread(target=scrape_tweets, daemon=True).start()
    socketio.run(app, debug=True)
