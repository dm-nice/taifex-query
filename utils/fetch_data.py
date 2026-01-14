
import urllib.request
import urllib.parse

# The URL for the daily market report
url = 'https://www.taifex.com.tw/cht/3/futDailyMarketReport'

# The form data to be sent with the POST request
# We are fetching for the date 2025/12/18
form_data = {
    'queryType': '2',      # Query by date
    'marketCode': '0',     # Regular trading session
    'queryDate': '2025/12/18',
}

# Encode the form data
data = urllib.parse.urlencode(form_data).encode('utf-8')

try:
    # Create a request object
    req = urllib.request.Request(url, data=data)

    # Open the URL
    with urllib.request.urlopen(req) as response:
        # Read the response content
        html_content = response.read()

        # Save the content to a file
        with open('market_report.html', 'wb') as f:
            f.write(html_content)
        
        print("Successfully downloaded market report to market_report.html")

except Exception as e:
    print(f"An error occurred: {e}")
