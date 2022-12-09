# lingwiki

This module will allow you to download parsed content from wikipedia articles.

## Article return format
```
dict
{
    'title': 'Alan Turing',
    'paragraphs': ['Alan Mathison Turing OBE FRS (/ˈtjʊərɪŋ/; 23 June 1912 – 7 June 1954) was an English mathematician...', ... ],
    'images': ['image link1', 'image link2'...],
    'links': ['link1', 'link2'...],
}
```

**Done**:
 - `get_article()` - get article's content using url.

**In progress**
 - `article_flow()` - get multiple articles content by urls. It threads downloading. Acceppts as input iterable object or a text file.

**ToDo**
 - `get_rand_article()` - same as `get_article()` but returns random one. You can choose the article's language.
 - `rand_article_flow()` - You get the point.

 