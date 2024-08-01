import instaloader
import requests
import time
import os
from config.config import INSTAGRAM_USERNAME, DISCORD_WEBHOOK_URL, CHECK_INTERVAL, LAST_POST_FILE

def get_instagram_photos(username):
    loader = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(loader.context, username)
    photos = []
    for post in profile.get_posts():
        photos.append({
            'id': post.shortcode,
            'caption': post.caption,
            'media_url': post.url,
            'permalink': f'https://www.instagram.com/p/{post.shortcode}/'
        })
        break
    return photos

def send_to_discord(webhook_url, content):
    data = {'content': content}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print('Mensaje enviado a Discord exitosamente.')
    else:
        print(f'Error al enviar el mensaje a Discord: {response.status_code}')

def main():
    last_post_id = None
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, 'r') as file:
            last_post_id = file.read().strip()

    while True:
        photos = get_instagram_photos(INSTAGRAM_USERNAME)

        if not photos:
            print('No se encontraron fotos.')
            time.sleep(CHECK_INTERVAL)
            continue

        for photo in photos:
            if last_post_id is None or photo['id'] != last_post_id:
                message = f"{photo['caption']}\n{photo['media_url']}\n{photo['permalink']}"
                send_to_discord(DISCORD_WEBHOOK_URL, message)
                last_post_id = photo['id']

                with open(LAST_POST_FILE, 'w') as file:
                    file.write(last_post_id)

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
