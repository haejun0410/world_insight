import requests
import requests
from bs4 import BeautifulSoup

# URL of the page to be crawled
countrylist = ['africa', 'asia', 'australia', 'europe', 'latin_america', 'middle_east', 'us-canada', 'uk']
for country in countrylist:
    if country == 'us-canada' or country == 'uk':
        url = "https://www.bbc.com/news/" + country
    else:
        url = "https://www.bbc.com/news/world/" + country
    # Send a request to the website
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception for HTTP errors

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find articles by looking for the specific data-testid that identifies them
    articles = soup.find_all('div', attrs={'data-testid': 'liverpool-card'})

    # Start the HTML output
    html_output = "<html><head><title>BBC News Articles</title></head><body>"
    html_output += "<h1>BBC News Articles from" + f'{country}' + "</h1>"

# Iterate through each article
    for article in articles:
        # Extract the headline safely
        headline_tag = article.find('h2', attrs={'data-testid': 'card-headline'})
        headline = headline_tag.get_text(strip=True)
    
        descript_tag = article.find('p', attrs={'data-testid': 'card-description'})
        descript = descript_tag.get_text(strip=True) 
    
        link_tag = article.find('a', attrs={'data-testid': 'internal-link'})
        link = 'https://www.bbc.com' + link_tag.get('href') 
    
        image_tag = article.find('div', attrs={'class': 'sc-a898728c-1 jWZsJP'})
        image = image_tag.find_all('img')
        html_output += f"<div><h2>{headline}</h2><p>{descript}</p><a href='{link}'>Read more</a>{image}</div><hr>"

        


    # Close the HTML tags
    html_output += "</body></html>"
    filename = f'{country}.html'
    # Save the HTML content to a file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_output)

#print("HTML file created successfully. You can now open 'output.html' in your web browser to view the articles.")