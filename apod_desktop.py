"""
COMP 593 - Final Project

Description:
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
import re
import sys
from datetime import date
import os
import inspect
import sqlite3
import os
import requests
import image_lib
import hashlib
import ctypes

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, file_path, 3)
        image_lib.set_desktop_background_image(file_path)
        print(f'Setting desktop to {file_path}...success')
    else:
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, file_path, 3)
        print(f'Setting desktop to {file_path}...success')

def get_apod_date():
    """Gets the APOD date

    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    # Check if a date was provided as a command line argument
    if len(sys.argv) > 1:
        apod_date_str = sys.argv[1]
    else:
        apod_date_str = date.today().isoformat()

    try:
        apod_date = date.fromisoformat(apod_date_str)

        # Check that the APOD date is not in the future
        if apod_date > date.today():
            print(f"Error: APOD date cannot be in the future")
            print("Script execution aborted")
            sys.exit(1)

    except ValueError as e:
        if "day is out of range for month" or "month must be in 1..12" in str(e):
            print(f"Error: Invalid date format; day is out of range for month")
            print("Script execution aborted")
        else:
            print(f"Error: Invalid date format; Invalid isoformat string: {apod_date}")
            print("Script execution aborted")
        sys.exit(1)

    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
 
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.
 
    Args:
        parent_dir (str): Full path of parent directory
    """
# Define global variables
    global image_cache_dir
    global image_cache_db
 
    # Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir, 'image_cache')
 
    # Check if the image cache directory exists
    if os.path.exists(image_cache_dir):
        print("Image cache directory", image_cache_dir)
        print("Image cache directory already exists:")
    else:
        # Create the image cache directory
        os.makedirs(image_cache_dir)
        print("Image cache directory", image_cache_dir)
        print("Image cache directory created:")
 
    # Determine the path of the image cache database
    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')
    print("Image cache DB:", image_cache_db)
 
    # Create the DB if it does not already exist
    if not os.path.exists(image_cache_db):
        conn = sqlite3.connect(image_cache_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE apod
                     (id INTEGER PRIMARY KEY,
                      title TEXT,
                      explanation TEXT,
                      file_path TEXT,
                      sha256 TEXT)''')
        conn.commit()
        conn.close()
        print("Image cache DB created.")
    else:
        print("Image cache DB already exists")
def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.

    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())

    # Download the APOD information from the NASA API
    url = f"https://api.nasa.gov/planetary/apod?api_key=z7r4WAcFEHcZuGdP9hO2kqNifeKUFFWRqwhsyVZl&date={apod_date.isoformat()}"
    response = requests.get(url)
    apod_data = response.json()
    print(f"Getting {apod_date} APOD information from NASA...success")

# Check whether the APOD already exists in the image cache
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute("SELECT id FROM apod WHERE title=?", (apod_data['title'],))
    result = c.fetchone()
    print(f"APOD title: {apod_data['title']}")
    print(f"APOD URL: {apod_data['hdurl']}")
    print(f"Downloading image from {apod_data['hdurl']}...success")
    global file_path

    response = requests.get(apod_data['hdurl'])
    file_name = os.path.basename(apod_data['hdurl'])
    file_path = os.path.join(image_cache_dir, file_name)

    sha256 = hashlib.sha256(response.content).hexdigest()
    print("APOD SHA-256:",sha256)

    if result:
        print("APOD image is already in cache.")
        return result[0]
    with open(file_path, 'wb') as f:
        f.write(response.content)
        print(f"Saved APOD image file as {file_path}")
    print("Adding APOD to image cache DB...success")

    # Add the APOD information to the DB

    c.execute("INSERT INTO apod (title, explanation, file_path,sha256) VALUES (?, ?, ?, ?)",
            (apod_data['title'], apod_data['explanation'], file_path, sha256))
    conn.commit()


    # Close the database connection
    conn.close()

    # Return the record ID of the APOD in the image cache DB
    return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value

    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute("SELECT id FROM apod_cache WHERE sha256=?", (image_sha256,))
    row = c.fetchone()
    if row is not None:
        return row[0]
    else:
        return 0

def determine_apod_file_path(image_title, image_url, cache_dir):
    """Determines the path at which a newly downloaded APOD image must be
    saved in the image cache.

    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is '/tmp/APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be '/tmp/APOD/NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL

    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # Get file extension from image URL
    file_extension = os.path.splitext(image_url)[1]

    # Remove leading/trailing spaces, replace inner spaces with underscores, and remove non-letter/number/underscore characters from title
    file_name = re.sub(r'[^\w\s]', '', image_title.strip()).replace(' ', '_') + file_extension

    # Join file path with directory path and return
    file_path = os.path.join(cache_dir, file_name)
    return file_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # Query DB for image info
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.cursor()
    cursor.execute("SELECT title, explanation, file_path FROM apod WHERE id=?", (image_id,))
    row = cursor.fetchone()
    conn.close()

    # Put information into a dictionary
    if row is not None:
        # Put information into a dictionary
        apod_info = {
            'title': row[0],
            'explanation': row[1],
            'file_path': row[2],
        }
        return apod_info
    else:
        return file_path
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute("SELECT title FROM apod")
    result = c.fetchall()
    titles = [r[0] for r in result]
    conn.close()
    return titles

if __name__ == '__main__':
    main()
