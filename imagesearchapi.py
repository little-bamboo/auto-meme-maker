import requests
import io
import re
import json
from operator import itemgetter

import numpy as np
import cv2
from PIL import Image
import pytesseract


class ImageSearchApi(object):

    def __init__(self):
        self.searching = False

    def filter_images_with_text(self, image_list):
        print("processing list of images")

        for image in image_list:
            
            try:

                response = requests.get(image['image'])
                img = Image.open(io.BytesIO(response.content))

                open_cv_image = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2GRAY)
                text_found = pytesseract.image_to_string(open_cv_image).strip()

                # print("Text Found: {0} \nIn Image: {1}".format(text_found, image['image']))

                if text_found == '':
                    # Return the first image without any text found
                    return img

            except Exception as e:
                print("Error Reading Image Text: {0}".format(e))

        return

    def search(self, keywords, max_results=None):
        url = 'https://duckduckgo.com/'
        params = {
            'q': keywords
        }

        #   First make a request to above URL, and parse out the 'vqd'
        #   This is a special token, which should be used in the subsequent request
        res = requests.post(url, data=params)
        search_object = re.search(r'vqd=(\d+)\&', res.text, re.M | re.I)

        if search_object:
            headers = {
                'dnt': '1',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'x-requested-with': 'XMLHttpRequest',
                'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6,ms;q=0.4',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'referer': 'https://duckduckgo.com/',
                'authority': 'duckduckgo.com',
            }

            params = (
                ('l', 'wt-wt'),
                ('o', 'json'),
                ('q', keywords),
                ('vqd', search_object.group(1)),
                ('f', ',,,'),
                ('p', '2')
            )

            request_url = url + "i.js"

            res = requests.get(request_url, headers=headers, params=params)
            data = json.loads(res.text)
            results = data["results"]

            filtered_results = [d for d in results if 800 <= d['width'] <= 2000]

            # Iterate over images and sort list of items in dict by image width
            images_desc_by_width = sorted(filtered_results, key=itemgetter('width'), reverse=True)

            filtered_images = self.filter_images_with_text(images_desc_by_width)

            return filtered_images

        else:
            return

    def print_json(self, objs):
        for obj in objs:
            print("Width {0}, Height {1}".format(obj["width"], obj["height"]))
            print("Thumbnail {0}".format(obj["thumbnail"]))
            print("Url {0}".format(obj["url"]))
            print("Title {0}".format(obj["title"].encode('utf-8')))
            print("Image {0}".format(obj["image"]))
            print("__________")
