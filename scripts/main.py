import json
import os
import time
import instaloader
import requests
from config.config import INSTAGRAM_USERNAME, DISCORD_WEBHOOK_URL, CHECK_INTERVAL, LAST_POST_FILE

def get_instagram_data(username):
    loader = instaloader.Instaloader()

    data = {
        "photos": []
    }

    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        print(f"Profile {username} found.")

        # Debug: Print profile info
        print(f"Profile Info: Followers: {profile.followers}, Posts: {profile.mediacount}, is_private: {profile.is_private}")

        # Extract posts
        print("Fetching posts...")
        for post in profile.get_posts():
            print(f"Found post: {post.url}")
            data["photos"].append({
                "url": post.url,
                "caption": post.caption,
                "timestamp": post.date_utc.isoformat()
            })
            # Delay to mimic human behavior
            time.sleep(2)  # Adjust delay as needed

        return data

    except instaloader.exceptions.ProfileNotExistsException:
        print(f'Profile {username} does not exist.')
        return None
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}.")

def load_last_post():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_post(post_id):
    with open(LAST_POST_FILE, 'w') as f:
        f.write(post_id)
    print(f"Last post ID saved to {LAST_POST_FILE}.")

def post_to_discord(data):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 204:
        print("Posted to Discord successfully.")
    else:
        print(f"Failed to post to Discord: {response.status_code}")

def main():
    while True:
        print("Checking for new posts...")
        data = get_instagram_data(INSTAGRAM_USERNAME)

        if data:
            save_data_to_json(data, "instagram_data.json")

            # Post latest photo to Discord
            if data["photos"]:
                last_photo = data["photos"][0]
                last_post_id = load_last_post()

                if last_photo["url"] != last_post_id:
                    post_to_discord({
                        "content": f"New post from {INSTAGRAM_USERNAME}: {last_photo['url']}\nCaption: {last_photo['caption']}"
                    })
                    save_last_post(last_photo["url"])

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
