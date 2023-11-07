import concurrent.futures
import csv
import json
import requests
from bs4 import BeautifulSoup as Bs
from lxml import etree
from tqdm import tqdm
import time
import os

start = time.time()
## Direct Path
# https://www.yellowpages.com/search?search_terms=plumbers&geo_location_terms=cheyenne
Category_url = "https://www.yellowpages.com/categories"
Category_resp = requests.get(Category_url, headers={"User-Agent": "Mozilla/5.0"})
Category_soup = Bs(Category_resp.text, "html.parser")
dom = etree.HTML(str(Category_soup))
# print(Category_soup.prettify())
Category_resp.close()

# Find all Category
category_list = dom.xpath("//div[@class='list-content']//a/text()")
print(len(category_list), category_list)

# Find all city
cata_url = "https://www.yellowpages.com/categories/electricians"
cata_resp = requests.get(cata_url, headers={"User-Agent": "Mozilla/5.0"})
cata_soup = Bs(cata_resp.text, "html.parser")
cata_dom = etree.HTML(str(cata_soup))
# print(cata_soup.prettify())
cata_resp.close()

city_list = cata_dom.xpath("//div[@class='list-content']//a/text()")
print(len(city_list), city_list)

final_data = []


def scrape_category(category, city):
    business_loc = []
    count = 0
    page_result_list = []
    city_dir = f"YP/YellowPages/{city}_dir"
    os.makedirs(city_dir, exist_ok=True)
    output_file = f"{city_dir}/{city}_{category}.csv"

    # Writing Headers
    headers = [
        "Business Name",
        "Phone Number",
        "Email",
        "Website",
        "Street Address",
        "City",
        "State",
        "Zip Code",
        "Facebook URL",
        "Instagram URL", 
        "Linkedin URL",
        "Twitter URL",
        "Business Hours",
        "Yellow Page Rating",
        "Review Count",
        "Years in Business",
        "Years with yellow pages",
        "Trip Advisor Ratings",
        "Trip Advisor Count",
        "Accreditation",
        "Page Destination URL",
        "Business Information",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as output_csv:
        csvwriter = csv.writer(output_csv)
        csvwriter.writerow(headers)

    for page in tqdm(range(1, 20)):
        try:
            city_cata_url = f"https://www.yellowpages.com/search?search_terms={category.lower().replace(' ', '-')}&geo_location_terms={city.replace(' ', '+')}&page={page}"
            city_cata_resp = requests.get(
                city_cata_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            city_cata_soup = Bs(city_cata_resp.text, "html.parser")
            city_cata_dom = etree.HTML(str(city_cata_soup))

            city_cata_resp.close()
            business_loc = [
                (a.text, "https://www.yellowpages.com" + a["href"])
                for a in city_cata_soup.find_all("a", class_="business-name")
            ]

            if business_loc:
                print(
                    f"\ncity: {city}\ncategory:{category}\nPage:{page} {city_cata_url}\n"
                )

                for biz_name, business_url in business_loc:
                    count += 1
                    biz_resp = requests.get(
                        business_url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    biz_soup = Bs(biz_resp.text, "html.parser")
                    biz_dom = etree.HTML(str(biz_soup))
                    biz_resp.close()

                    json_script = json.loads(
                        biz_soup.find("script", type="application/ld+json").text
                    )

                    try:
                        biz_info = biz_soup.find(class_="general-info").text
                    except Exception:
                        biz_info = ""

                    try:
                        phone = json_script["telephone"]
                    except Exception:
                        phone = ""

                    try:
                        email = json_script["email"].replace("mailto:", "")
                    except Exception:
                        email = ""

                    try:
                        website = json_script["url"]
                    except Exception:
                        website = ""

                    try:
                        openingHours = str(json_script["openingHours"])
                    except Exception:
                        openingHours = ""

                    try:
                        address_dic = json_script["address"]
                    except Exception:
                        address_dic = {}

                    try:
                        streetAddress = address_dic["streetAddress"]
                    except Exception:
                        streetAddress = ""

                    try:
                        addressLocality = address_dic["addressLocality"]
                    except Exception:
                        addressLocality = ""

                    try:
                        addressRegion = address_dic["addressRegion"]
                    except Exception:
                        addressRegion = ""

                    try:
                        postalCode = address_dic["postalCode"]
                    except Exception:
                        postalCode = ""

                    try:
                        facebook_url = biz_soup.find("a", class_="fb-link")["href"]
                        Instagram_url = ""
                        Linkedin_url = ""
                        Twitter_url = ""
                    except Exception:
                        facebook_url = ""

                    try:
                        yellowPageRating = json_script["aggregateRating"]["ratingValue"]
                        reviewCount = json_script["aggregateRating"]["reviewCount"]
                    except Exception:
                        yellowPageRating = ""
                        reviewCount = ""

                    try:
                        Accreditation = " ".join(
                            biz_dom.xpath("//div[@class='bbb-rating']//text()")
                        )
                    except Exception:
                        yellowPageRating = ""

                    try:
                        years_in_business = biz_dom.xpath(
                            "//div[@class='years-in-business']//strong/text()"
                        )[0]
                    except Exception:
                        years_in_business = ""

                    try:
                        years_with_yp = biz_dom.xpath(
                            "//div[@class='years-with-yp']//strong/text()"
                        )[0]
                    except Exception:
                        years_with_yp = ""

                    try:
                        ta_count_span = biz_soup.find("span", class_="ta-count")
                        ta_count = ta_count_span.text
                        ta_rating = ta_count_span.parent()

                    except Exception:
                        ta_count = ""
                        ta_rating = ""

                    page_result = [
                        biz_name,
                        phone,
                        email,
                        website,
                        streetAddress,
                        addressLocality,
                        addressRegion,
                        postalCode,
                        facebook_url,
                        Instagram_url,
                        Linkedin_url,
                        Twitter_url,
                        openingHours,
                        yellowPageRating,
                        reviewCount,
                        years_in_business,
                        years_with_yp,
                        ta_rating,
                        ta_count,
                        Accreditation,
                        business_url,
                        biz_info,
                    ]

                    print(count, page_result, "\n")
                    page_result_list.append(page_result)

        except Exception as e:
            print(count, business_url, "not found, stopped", e, json_script)

        with open(output_file, "a", newline="", encoding="utf-8") as output_csv:
            csvwriter = csv.writer(output_csv)
            csvwriter.writerows(page_result_list)


with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    # Start the threads for each category and city
    futures = [
        (executor.submit(scrape_category, category, city))
        for category in category_list
        for city in city_list[:1]
    ]

# Wait for all threads to complete
concurrent.futures.wait(futures)

end = time.time()
execution_time_seconds = end - start
print(execution_time_seconds)

with open("YP/Total Time.csv", 'w') as file:
    # Write each result to the file
    file.write(str(execution_time_seconds))
