import string
import traceback
import pke
import torch
from nltk.corpus import stopwords
from flashtext import KeywordProcessor
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, T5ForConditionalGeneration, T5Tokenizer

def generate_qa(text):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    question_model = T5ForConditionalGeneration.from_pretrained('ramsrigouthamg/t5_squad_v1')
    question_tokenizer = T5Tokenizer.from_pretrained('ramsrigouthamg/t5_squad_v1')
    question_model = question_model.to(device)

    summary_tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-6-6")
    summary_model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-6-6")
    summarizer = pipeline("summarization", model=summary_model, tokenizer=summary_tokenizer, framework="tf")
    to_tokenize = text
    summarized = summarizer(to_tokenize, min_length=75)

    # keyword extraction
    def multipartite_keyword(text):
        out = []
        try:
            # 1. create a MultipartiteRank extractor.
            extractor = pke.unsupervised.MultipartiteRank()

            # 2. load the content of the document.
            extractor.load_document(text)

            # 3. select the longest sequences of nouns and adjectives, that do
            #    not contain punctuation marks or stopwords as candidates.
            pos = {'NOUN', 'PROPN', 'ADJ'}
            stoplist = list(string.punctuation)
            stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
            stoplist += stopwords.words('english')
            extractor.candidate_selection(pos=pos, stoplist=stoplist)

            # 4. build the Multipartite graph and rank candidates using random walk,
            #    alpha controls the weight adjustment mechanism, see TopicRank for
            #    threshold/method parameters.
            extractor.candidate_weighting(alpha=1.1,
                                          threshold=0.74,
                                          method='average')

            # 5. get the 10-highest scored candidates as keyphrases
            keyphrases = extractor.get_n_best(n=10)

            for val in keyphrases:
                out.append(val[0])
        except:
            out = []
            traceback.print_exc()

        return out

    summary = summarized[0]['summary_text']

    def get_keywords(originaltext, summarytext):
        keywords = multipartite_keyword(originaltext)
        print("keywords unsummarized: ", keywords)
        keyword_processor = KeywordProcessor()
        for keyword in keywords:
            keyword_processor.add_keyword(keyword)

        keywords_found = keyword_processor.extract_keywords(summarytext)
        keywords_found = list(set(keywords_found))
        print("keywords_found in summarized: ", keywords_found)

        important_keywords = []
        for keyword in keywords:
            if keyword in keywords_found:
                important_keywords.append(keyword)

        return important_keywords

    imp_keywords = get_keywords(to_tokenize, summary)

    def get_question(context, answer, model, tokenizer):
        text = "context: {} answer: {}".format(context, answer)
        encoding = tokenizer.encode_plus(text, max_length=384, pad_to_max_length=False, truncation=True,
                                         return_tensors="pt").to(device)
        input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

        outs = model.generate(input_ids=input_ids,
                              attention_mask=attention_mask,
                              early_stopping=True,
                              num_beams=5,
                              num_return_sequences=1,
                              no_repeat_ngram_size=2,
                              max_length=72)
        dec = [tokenizer.decode(ids, skip_special_tokens=True) for ids in outs]

        Question = dec[0].replace("question:", "")
        Question = Question.strip()
        return Question

    ls = []
    for answer in imp_keywords:
        ques = get_question(summary, answer, question_model, question_tokenizer)
        q = ques
        answer.capitalize()
        b = [q, answer]
        ls.append(b)

    return tuple(ls)