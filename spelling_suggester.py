import os
import re
import string
import pickle
import enchant
from collections import Counter
from collections import defaultdict
from nltk.stem.wordnet import wordnet

letters = string.ascii_lowercase

english_dict = enchant.Dict("en_US")

top = 5

words_path = os.path.join(os.path.dirname(__file__), 'words.pickle')


def words(text):
    return re.findall(r'\w+', text.lower())


if not os.path.isfile(words_path):
    if not (os.path.isfile(os.path.join(os.path.dirname(__file__), 'big.txt')) or os.path.isfile(
            os.path.join(os.path.dirname(__file__), 'agents_texts.txt'))):
        raise Exception('files missing')
    WORDS = Counter(words(open(os.path.join(os.path.dirname(__file__), 'big.txt')).read()))
    AGENT_WORDS = Counter(
        words(open(os.path.join(os.path.dirname(__file__), 'agent_texts.txt'), encoding='utf-8').read()))
    WORDS.update(AGENT_WORDS)
    with open(words_path, 'wb') as f:
        pickle.dump(WORDS, f)

with open(words_path, 'rb') as f:
    WORDS = pickle.load(f)

total_words = sum(WORDS.values())


def word_probability(word):
    return WORDS[word] / total_words


def edits1(word):
    if not hasattr(edits1, 'd'):
        edits1.d = defaultdict(set)
    v = edits1.d[word]
    if v:
        return v
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [l + r[1:] for l, r in splits if r]
    transposes = [l + r[1] + r[0] + r[2:] for l, r in splits if len(r) > 1]
    replaces = [l + c + r[1:] for l, r in splits if r for c in letters]
    inserts = [l + c + r for l, r in splits for c in letters]
    v = edits1.d[word] = set(deletes + transposes + replaces + inserts)
    return v


def edits2(word):
    if not hasattr(edits2, 'd'):
        edits2.d = defaultdict(set)
    v = edits2.d[word]
    if v:
        return v
    v = edits2.d[word] = set(e2 for e1 in edits1(word) for e2 in edits1(e1))
    return v


def edits3(word):
    v = set(e3 for e1 in edits1(word) for e2 in edits1(e1) for e3 in edits1(e2) if len(e3) > 1)
    # print(len(v))
    # v1 = set()
    # for x in v:
    #     print(x)
    #     if (english_dict.check(x) or wordnet.synsets(x)) and len(x) > 1:
    #         v1.add(x)
    # v = set(x for x in v if (english_dict.check(x) or wordnet.synsets(x)) and len(x) > 1)
    return v


def known(words):
    # return set(w for w in words if w in WORDS)
    return set(w for w in words if (english_dict.check(w) or wordnet.synsets(w)))


def candidates(word):
    s = set()
    # return known([word]) or known(edits1(word)) or known(edits2(word)) or [word]
    s.update(known([word]))
    s.update(known(edits1(word)))
    s.update(known(edits2(word)))
    # s.update(known(edits3(word)))
    return s


def suggestions(word):
    if not hasattr(suggestions, 'd'):
        suggestions.d = defaultdict(set)
    v = suggestions.d[word]
    if v:
        return v
    v = suggestions.d[word] = [x for x in sorted(candidates(word), key=word_probability, reverse=True) if
                               word_probability(x) > 0.0 and
                               (english_dict.check(x) or wordnet.synsets(x))][:top]
    return v


# print(suggestions('spellng'))

def check_spelling_errors_for_missing_space(error_list):
    """Checks if the reported errors are valid words with space missing or not."""
    new_error_list = []
    error_suggestion_dict = {}
    space_missing = defaultdict(list)

    for word in error_list:
        flag = False
        for i in range(1, len(word)):
            a = word[0:i]
            b = word[i:]
            if a == 'a' or len(a) > 1:
                if (english_dict.check(a) or wordnet.synsets(a)) and (
                        english_dict.check(b) or wordnet.synsets(b)) and len(b) > 1:
                    space_missing[word].append((a, b))
                    flag = True
        if not flag:
            new_error_list.append(word)
    for word in new_error_list:
        error_suggestion_dict[word] = suggestions(word)
    space_keys = space_missing.keys()
    for word in space_keys:
        error_suggestion_dict[word] = suggestions(word)
    error_suggestion_dict = {x: y for x, y in error_suggestion_dict.items() if y}
    error_suggestion_keys = error_suggestion_dict.keys()
    space_missing = {x: [(a, b) for a, b in y if word_probability(a) > 0.0 and word_probability(b) > 0.0]
                     for x, y in space_missing.items() if x not in error_suggestion_keys}

    return {'errors': error_suggestion_dict, 'space_miss_suggestions': space_missing}

# for x, y in check_spelling_errors_for_missing_space(
#         ['hellp', 'ther', 'yuo', 'togeter', 'hellothere', 'spellng']).items():
#     print()
#     print()
#     print('____', x, '____')
#     for k, v in y.items():
#         print()
#         print()
#         print('Mistake::> ', k)
#         print()
#         print('    suggestions:')
#         [print(z) for z in v]
