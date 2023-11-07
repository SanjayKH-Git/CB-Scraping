import time
import csv
from playwright.sync_api import sync_playwright

start = time.time()

def login(page):
    main_url = "https://www.crunchbase.com/login?"
    email = "rajkumarrr5551234@gmail.com"
    pswd = "Crunchbasepassword123456"
    # email = "sanjaykhegde98@gmail.com"
    # pswd = "Sanjaycrunch823#"
    page.goto(main_url, wait_until="load", timeout=0)
    time.sleep(6)

    email_input_selector = "//input[@name='email']"
    page.fill(email_input_selector, email)

    pswd_input_selector = "//input[@name='password']"
    page.fill(pswd_input_selector, pswd)

    # time.sleep(3)
    login_button_selector = "//div[@class='actions']//button[1]"
    page.click(login_button_selector)
    # time.sleep(3)
    logged_in = page.wait_for_selector(
        "//span[text()='Account']", timeout=15000
    ).text_content()

    if logged_in == "Account":
        print(f"----- Logged into -----{email}------ Account-----\n")
        return page

    else:
        login(page)


op_name = "China 1000"
# op_name = "China 623"
output_file = f"USA/{op_name}.csv"

# Scraper
with sync_playwright() as p:
    browser = p.firefox.launch(headless=True, args=["--start-maximized"])
    context = browser.new_context()
    page = context.new_page()
    # page.viewport_size({"width":0, "height":0})

    page = login(page)

    # Next_url = "https://www.crunchbase.com/discover/saved/us-2-992/7739d571-9ec3-4e18-8ded-f348ae71aad4"
    # Next_url = "https://www.crunchbase.com/discover/saved/us-992/4e45a6df-97d2-4200-aab7-b6f048eb0717"
    # Next_url = "https://www.crunchbase.com/discover/saved/us-californea-others-979/2010c771-8ceb-4f53-95be-0b6743c78636"
    # Next_url = "https://www.crunchbase.com/discover/saved/us-new-york-1000/ac0e88f7-d5af-4fdf-b710-667a87448f3e"
    # Next_url = "https://www.crunchbase.com/discover/saved/us-san-francisco-1000/b75099f1-f871-43dd-8a66-ada018befc63"
    # Next_url = "https://www.crunchbase.com/discover/saved/us-san-francisco-720-16-rounds/8bb48dd7-f8e4-4609-9598-c722bc13efd3"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/0a3feb058dc2fbbb0c9e235e5b0b56d5"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/75c62db333352845a8311aaba8c152a9"
    # Next_url = "https://www.crunchbase.com/discover/saved/south-america-1000/e86b423d-2075-4ad1-9642-3b9d271e1ff9"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/ce49d3be8016d1fde8fbcdc98f4e22fc"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/e7663bfbcfce1cf21e6562e6c225bd22"
    # Next_url = "https://www.crunchbase.com/discover/saved/bangladesh-myanmar-thailand-cambodia/ea58875a-6a51-4398-8a78-3fe4dee35411"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/ff97ec9b23cefd6890c90fbb798ecd77"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/0b18e34c051cebd4a3b2524c16d2e2f6"
    # Next_url = "https://www.crunchbase.com/discover/organization.companies/147da9d02dbdb57bc2a76a0875f47a65"

    round = 1
    result_data = []

    while Next_url and round < 22:
        round_info = f"\nround> {round}  {Next_url} \n {len(result_data)}/{(round * 50) - 50} Found"
        print(round_info)
        with open(f"USA/next_url_{op_name}.txt", "a") as file:
            file.write(round_info)

        try:
            # page = context.new_page()
            page.goto(Next_url, wait_until="load", timeout=100000)
            time.sleep(30)
            # grid = page.locator("//div[@class='grid-id-organization-companies']").first()

            if round == 1:
                headers = ["Organization URL"] + [
                    div.text_content().strip()
                    for div in page.query_selector_all(
                        "//div[@class='header-contents' or @class='header-contents sorted']/div"
                    )
                ][1:-1]
                print(
                    len(headers),
                    headers,
                )
                with open(output_file, "w", newline="") as output_csv:
                    csvwriter = csv.writer(output_csv)
                    csvwriter.writerow(headers)

            elif round % 30 == 0:
                page = login(page)

            # Finding Next page URL
            next_button_selector = "//a[@aria-label='Next']"
            page.wait_for_selector(next_button_selector)
            Next_url = "https://www.crunchbase.com/" + page.query_selector(
                next_button_selector
            ).get_attribute("href")
            time.sleep(15)
            print("NExt", Next_url)
            # Extracting data from the page
            chunk_size = 104
            record_list_xpath = "//div[@class='non-select-column']"
            page.wait_for_selector(record_list_xpath)
            select_All_records_list = page.query_selector_all(record_list_xpath)
            # print(select_All_records_list)
            print("record Length:", len(select_All_records_list))
            if len(select_All_records_list) < 5000:
                time.sleep(30)
                select_All_records_list = page.query_selector_all(record_list_xpath)
                print("Re Waited Length:", len(select_All_records_list))

            All_records_list = [
                select_All_records_list[i : i + chunk_size]
                for i in range(0, len(select_All_records_list), chunk_size)
            ]

            for rec in All_records_list:
                organization_url = "https://www.crunchbase.com/" + rec[
                    0
                ].query_selector("a").get_attribute("href")

                iter_data = [organization_url]
                for col in rec[:-1]:
                    cdata = col.text_content().replace(",", " ").replace("\n", "")
                    if "View on" in cdata:
                        cdata = col.query_selector("a").get_attribute("href")
                    iter_data.append(cdata)

                # Wrighting Data
                if iter_data not in result_data:
                    result_data.append(iter_data)
                    print(len(iter_data), iter_data)
                    with open(
                        output_file, "a", newline="", encoding="utf-8"
                    ) as output_csv:
                        csvwriter = csv.writer(output_csv)
                        csvwriter.writerow(iter_data)
                else:
                    print("exist")

        except Exception as e:
            print("Not Found", e)

        round += 1
        print("Length of result: ", len(result_data))

    # time.sleep(40)
    browser.close()

end = time.time()
execution_time_seconds = end - start
print(execution_time_seconds)
