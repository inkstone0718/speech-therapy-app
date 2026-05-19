import urllib.request
import urllib.parse
import json

word = "蘋果"
url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(word)}&gsrnamespace=6&gsrlimit=1&prop=imageinfo&iiprop=url"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 SpeechTherapyApp/1.0'})
try:
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    pages = data['query']['pages']
    for page_id in pages:
        image_url = pages[page_id]['imageinfo'][0]['url']
        print(f"Found image for {word}: {image_url}")
except Exception as e:
    print(f"Error: {e}")
