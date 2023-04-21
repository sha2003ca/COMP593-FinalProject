'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import sys
import requests
from datetime import datetime, timedelta

NASA_APOD_API_URL = 'https://apod.nasa.gov/apod/astropix.html'
NASA_API_KEY = 'z7r4WAcFEHcZuGdP9hO2kqNifeKUFFWRqwhsyVZl'

def main():
    # TODO: Add code to test the functions in this module
    apod_date = None
    if len(sys.argv) > 1:
        apod_date = sys.argv[1]

    if not apod_date:
        # If no date argument is provided, use today's date
        apod_date = datetime.today().strftime('%Y-%m-%d')

    apod_info = get_apod_info(apod_date)
    if not apod_info:
        print(f"Unable to retrieve APOD information for date {apod_date}.")
        return

    apod_url = get_apod_image_url(apod_info)
    if not apod_url:
        print(f"No APOD image or video URL found for date {apod_date}.")
        return

    print(apod_url)
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    try:
        response = requests.get(f"{NASA_APOD_API_URL}?api_key={NASA_API_KEY}&date={apod_date}")
        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None
    return   

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict['hdurl'] or apod_info_dict['url']
    elif apod_info_dict['media_type'] == 'video':
        return apod_info_dict['thumbnail_url']
    else:
        return None
    return

if __name__ == '__main__':
    main()