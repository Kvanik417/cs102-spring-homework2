from bottle import (
    route, run, template, request, redirect
)

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier

HABR_ARTICLES_URL = "https://habr.com/ru/articles/"

# порядок вывода: сначала «интересно», затем «возможно», в конце «не интересно»
LABEL_ORDER = {"good": 0, "maybe": 1, "never": 2}


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    news_id = request.query.id
    label = request.query.label
    s = session()
    news = s.query(News).get(news_id)
    if news is not None:
        news.label = label
        s.commit()
    if __name__ == "__main__":
        redirect('/news')


@route("/update")
def update_news():
    s = session()
    for item in get_news(HABR_ARTICLES_URL, n_pages=3):
        exists = s.query(News).filter(
            News.title == item["title"], News.author == item["author"]
        ).first()
        if not exists:
            s.add(News(
                title=item["title"],
                author=item["author"],
                url=item["url"],
                complexity=item.get("complexity"),
                habr_id=item.get("habr_id"),
            ))
            s.commit()
    if __name__ == "__main__":
        redirect('/news')


def classify_news():
    """ Обучает классификатор на размеченных новостях и возвращает неразмеченные,
    отсортированные по предсказанной метке (good -> maybe -> never). """
    s = session()
    labeled = s.query(News).filter(News.label != None).all()
    unlabeled = s.query(News).filter(News.label == None).all()
    if not labeled or not unlabeled:
        return unlabeled

    model = NaiveBayesClassifier()
    model.fit([n.title for n in labeled], [n.label for n in labeled])
    predicted = model.predict([n.title for n in unlabeled])

    ranked = sorted(zip(predicted, unlabeled), key=lambda pair: LABEL_ORDER.get(pair[0], len(LABEL_ORDER)))
    return [n for _, n in ranked]


@route("/classify")
def classify_page():
    return template('news_template', rows=classify_news())


if __name__ == "__main__":
    run(host="localhost", port=8080)
