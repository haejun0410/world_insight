import requests
from bs4 import BeautifulSoup

class GenerateNews:
    @staticmethod
    def generate_news():
        base_html_output = """
        <html>
        <head>
            <title>BBC News Articles</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV" crossorigin="anonymous"></script>
        </head>
        <body>
        """
        
        countrylist = ['africa', 'asia', 'australia', 'europe', 'latin_america', 'middle_east', 'us-canada', 'uk']
        
        for country in countrylist:
            html_output = base_html_output

            if country == 'us-canada' or country == 'uk':
                url = "https://www.bbc.com/news/" + country
            else:
                url = "https://www.bbc.com/news/world/" + country

            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', attrs={'data-testid': 'liverpool-card'})

            html_output += "<div class='container'>"
            html_output += "<h1 class='text-center my-4'>BBC News Articles from " + f'{country}' + "</h1>"

            for article in articles:
                headline_tag = article.find('h2', attrs={'data-testid': 'card-headline'})
                headline = headline_tag.get_text(strip=True) if headline_tag else "No headline available"
                descript_tag = article.find('p', attrs={'data-testid': 'card-description'})
                descript = descript_tag.get_text(strip=True) if descript_tag else "No description available"
                link_tag = article.find('a', attrs={'data-testid': 'internal-link'})
                link = 'https://www.bbc.com' + link_tag.get('href') if link_tag else "#"
                image_tag = article.find('div', attrs={'class': 'sc-a898728c-1 jWZsJP'})
                image = image_tag.find_all('img') if image_tag else []

                html_output += "<div class='card mb-4'>"
                html_output += "<div class='card-body'>"
                html_output += f"<h2 class='card-title'>{headline}</h2>"
                html_output += f"<p class='card-text'>{descript}</p>"
                html_output += f"<a href='{link}' class='btn btn-primary'>Read more</a>"
                html_output += "</div>"
                if image:
                    html_output += "<div class='card-img'>"
                    for img in image[1:]:
                        html_output += str(img)
                    html_output += "</div>"
                html_output += "</div>"

            html_output += "</div>"

            html_output += "</body></html>"

            filename = f'templates/{country}.html'
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(html_output)

if __name__ == "__main__":
    GenerateNews.generate_news()
