import json
import os
import time
import random
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
            post_data = {
                "url": post.url,
                "caption": post.caption,
                "timestamp": post.date_utc.isoformat(),
                "media_urls": [post.url]  # Include main post URL by default
            }

            # Handle multiple slides in a post
            for node in post.get_sidecar_nodes():
                post_data["media_urls"].append(node.display_url)

            data["photos"].append(post_data)

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

    # Split media URLs into chunks of 10 | Error 400 Bad Request if more than 10 URLs
    chunks = [data['media_urls'][i:i+10] for i in range(0, len(data['media_urls']), 10)]

    for chunk in chunks:
        embeds = []
        for media_url in chunk:
            embeds.append({
                "image": {
                    "url": media_url
                },
                "color": {

                },
                "footer": {
                    "text": f"{data['caption']}",
                    "icon_url": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
                }
            })

        discord_message = {
            "embeds": embeds
        }

    response = requests.post(DISCORD_WEBHOOK_URL, headers=headers, data=json.dumps(discord_message))
    if response.status_code == 204:
        print("Posted to Discord successfully.")
    else:
        print(f"Failed to post to Discord: {response.status_code}")
        print(response.text)
        print(response.content)

def post_random_from_feed():
    with open("instagram_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data["photos"]:
        post = random.choice(data["photos"])
        post_to_discord(post)
        data["photos"].remove(post)
        save_data_to_json(data, "instagram_data.json")

#%%
def main():
    print("Checking for new posts...")
    data = get_instagram_data(INSTAGRAM_USERNAME)

    if data:
        save_data_to_json(data, "instagram_data.json")

        # Post latest photo to Discord for initial test
        if data["photos"]:
            last_photo = data["photos"][0]
            last_post_id = load_last_post()

            if last_photo["url"] != last_post_id:
                post_to_discord(last_photo)
                save_last_post(last_photo["url"])
                return  # Stop after posting the first photo for testing

    # After initial test, continue posting randomly
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
                    post_to_discord(last_photo)
                    save_last_post(last_photo["url"])
                else:
                    # If no new post, post a random one from the saved feed
                    post_random_from_feed()

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
