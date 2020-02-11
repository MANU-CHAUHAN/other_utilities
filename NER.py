import nltk
from polyglot.text import Text
from nltk.tag import StanfordNERTagger
import os

dir = os.path.dirname(__file__)

exs_texts = []
exs = []

tagger = StanfordNERTagger(os.path.join(dir, 'english.muc.7class.distsim.crf.ser.gz'),
                           os.path.join(dir, 'stanford-ner-3.9.1.jar'))


def ner_checker(texts):
    all_set = set()

    def stanford_ner_check(texts):
        for i, text in texts:
            for word, tag in tagger.tag(text.split()):
                if tag != 'O':
                    all_set.add(word)

    def polyglot_ner_check(texts):
        try:
            for i, text in texts:
                t = Text(text)
                for entity in t.entities:
                    # tag = entity.tag
                    # if tag == 'I-ORG':
                    #     tag = 'ORGANIZATION'
                    # elif tag == 'I-PER':
                    #     tag = 'PERSON'
                    all_set.add(' '.join(entity))
        except Exception as e:
            exs.append(e)
            exs_texts.append(text)

    def nltk_ner_check(texts):
        for i, text in texts:
            for entity in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text))):
                if isinstance(entity, nltk.tree.Tree):
                    etext = " ".join([word for word, tag in entity.leaves()])
                    # label = entity.label()
                    all_set.add(etext)

    stanford_ner_check(texts=texts)
    polyglot_ner_check(texts=texts)
    nltk_ner_check(texts=texts)
    return all_set

d = [(1,"Hi Partha. I work at Google. Where do you work?"), (1,"Where is your iPhone?")]
print(len(d))
print(NER_Checker(d))
