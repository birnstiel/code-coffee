#!/usr/bin/evn python
import ads

# articles = [list(ads.SearchQuery(bibcode=bibcode))[0] for bibcode in bibcodes]
# articles = list(ads.SearchQuery(author='Birnstiel,T'))
articles = list(ads.SearchQuery(author='Birnstiel,T', fl=['id', 'author', 'year', 'bibtex', 'bibcode', 'title', 'citation_count']))

for article in articles:
    print(
        (article.author[0].split(',')[0] + article.year + ':').ljust(20) +
        str(article.citation_count) + ' citation(s)'
    )
