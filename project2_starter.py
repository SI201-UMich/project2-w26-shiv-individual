# SI 201 HW4 (Library Checkout System)
# Your name:
# Your student id:
# Your email:
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    results = []

    title_divs = soup.find_all("div", {"data-testid": "listing-card-title"})
    for div in title_divs:
        title  = div.get_text(strip=True)
        div_id = div.get("id", "")
        listing_id = div_id.replace("title_", "")
        if title and listing_id:
            results.append((title, listing_id))
    
    return results
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    html_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # Policy Number (default then extract using regex)
    policy_number = "Pending"

    policy_label = soup.find(string = re.compile("Policy number", re.I))
    if policy_label:
        container_text = policy_label.parent.parent.get_text(strip=True)
        match = re.search(
            r"Policy number[:\s]*(.+?)(?:Response|Language|Superhost|\Z)",
            container_text,
            re.I
        )
        if match:
            raw_value = match.group(1).strip()
            raw_value = raw_value.replace("\ufeff", "").replace("\xa0", " ").strip()
            if re.match(r"pending", raw_value, re.I):
                policy_number = "Pending"
            elif re.match(r"exempt", raw_value, re.I):
                policy_number = "Exempt"
            else:
                policy_number = raw_value
    
    # Host Type (superhost)
    host_type = "regular"
    if soup.find(string = re.compile("is a Superhost", re.I)):
        host_type = "Superhost"

    # Host Name and Room Type (search h2 tags)
    host_name = ""
    room_type = "Entire Room"

    hosted_h2 = None
    for h2 in soup.find_all("h2"):
        if re.search(r"hosted by", h2.get_text(), re.I):
            hosted_h2 = h2
            break
    if hosted_h2:
        h2_text = hosted_h2.get_text(separator=" ", strip=True)
        h2_text = h2_text.replace("\xa0", " ")
        name_match = re.search(r"hosted by\s+(.+)", h2_text, re.I)
        if name_match:
            host_name = name_match.group(1).strip()
        if "Private" in h2_text:
            room_type = "Private Room"
        elif "Shared" in h2_text:
            room_type = "Shared Room"
        else:
            og_tag = soup.find("meta", property="og:description")
            if og_tag:
                og_text = og_tag.get("content", "")
                first_sentence = og_text.split(".")[0]
                if "Private room" in first_sentence or first_sentence.startswith("Private"):
                    room_type = "Private Room"
                elif "Shared room" in first_sentence or first_sentence.startswith("Shared"):
                    room_type = "Shared Room"
                else:
                    room_type = "Entire Room"
    
    # Location Rating (default 0.0, then extract using regex)
    location_rating = 0.0

    for div in soup.find_all("div", class_="_a3qxec"):
        text = div.get_text(strip=True)
        if text.startswith("Location"):
            rating_match = re.search(r"Location(\d+\.\d+)", text)
            if rating_match:
                location_rating = float(rating_match.group(1))
                break
    
    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = load_listing_results(html_path)

    database = []
    for listing_title, listing_id in listings:
        details = get_listing_details(listing_id)
        info = details[listing_id]
        row = (
            listing_title,
            listing_id,
            info["policy_number"],
            info["host_type"],
            info["host_name"],
            info["room_type"],
            info["location_rating"]
        )
        database.append(row)

    return database
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda row: row[6], reverse=True)

    headers = ["Listing Title", "Listing ID", "Policy Number", "Host Type", "Host Name", "Room Type", "Location Rating"]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    totals = {}
    counts = {}

    for row in data:
        room_type = row[5]
        location_rating = row[6]

        if location_rating == 0.0:
            continue

        if room_type not in totals:
            totals[room_type] = 0.0
            counts[room_type] = 0
        
        totals[room_type] += location_rating
        counts[room_type] += 1
    
    averages = {}
    for room_type in totals:
        averages[room_type] = round(totals[room_type] / counts[room_type], 1)
    return averages
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    valid_pattern = re.compile(r"^(20\d{2}-00\d{4}STR|STR-000\d{4})$")
    invalid_ids = []

    for row in data:
        listing_id = row[1]
        policy_number = row[2]
        if policy_number in ("Pending", "Exempt"):
            continue
        if not valid_pattern.match(policy_number):
            invalid_ids.append(listing_id)
        
    return invalid_ids
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/110.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    titles = []
    for tag in soup.find_all("h3", class_="gs_rt"):
        for span in tag.find_all("span"):
            span.decompose()
        title_text = tag.get_text(strip=True)
        if title_text:
            titles.append(title_text)
    return titles
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        self.assertEqual(len(self.listings), 18)
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        results = [get_listing_details(listing_id) for listing_id in html_list]
        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)
        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)
        # TODO: Read the CSV back in and store rows in a list.
        rows = []
        with open(out_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                rows.append(row)
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        self.assertEqual(rows[0], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])
        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        averages = avg_location_rating_by_room_type(self.detailed_data)
        # TODO: Check that the average for "Private Room" is 4.9.
        self.assertEqual(averages["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        invalid_listings = validate_policy_numbers(self.detailed_data)
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        self.assertEqual(invalid_listings, ["16204265"])


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)