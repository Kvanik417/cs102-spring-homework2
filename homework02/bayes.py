import math
from collections import Counter, defaultdict


class NaiveBayesClassifier:
    """Мультиномиальный наивный байесовский классификатор текстов со сглаживанием Лапласа."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes = []
        self.log_priors = {}
        self.word_counts = {}
        self.total_words = {}
        self.vocabulary = set()

    @staticmethod
    def _tokenize(text):
        return text.lower().split()

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        class_docs = Counter(y)
        n_docs = len(y)
        word_counts = defaultdict(Counter)

        for text, label in zip(X, y):
            word_counts[label].update(self._tokenize(text))

        self.classes = list(class_docs)
        self.log_priors = {c: math.log(class_docs[c] / n_docs) for c in self.classes}
        self.word_counts = {c: word_counts[c] for c in self.classes}
        self.total_words = {c: sum(word_counts[c].values()) for c in self.classes}
        self.vocabulary = set().union(*(word_counts[c].keys() for c in self.classes))
        return self

    def _log_proba(self, text, label):
        counts = self.word_counts[label]
        denominator = self.total_words[label] + self.alpha * len(self.vocabulary)
        score = self.log_priors[label]
        for word in self._tokenize(text):
            if word in self.vocabulary:  # слова, которых не было в обучении, пропускаем
                score += math.log((counts[word] + self.alpha) / denominator)
        return score

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        return [max(self.classes, key=lambda c: self._log_proba(text, c)) for text in X]

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        predicted = self.predict(X_test)
        correct = sum(p == t for p, t in zip(predicted, y_test))
        return correct / len(y_test)
