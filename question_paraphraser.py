from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import spacy
import numpy
import time


class GenerateParaphraseQuestions:

    def __init__(self):

        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        model = T5ForConditionalGeneration.from_pretrained('ramsrigouthamg/t5_paraphraser')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        self.device = device
        self.model = model
        self.nlp = spacy.load('en_core_web_sm')
        self.set_seed(42)

    def set_seed(self, seed):
        numpy.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def paraphrase(self, payload):
        start = time.time()
        inp = {
            "input_text": payload.get("input_text"),
            "max_questions": payload.get("max_questions", 3)
        }

        text = inp['input_text']
        num = inp['max_questions']

        self.sentence = text
        self.text = "paraphrase: " + self.sentence + " </s>"

        max_len = 256

        encoding = self.tokenizer.encode_plus(text, pad_to_max_length=True, return_tensors="pt")
        input_ids, attention_masks = encoding["input_ids"].to(self.device), encoding["attention_mask"].to(self.device)

        # set top_k = 50 and set top_p = 0.95 and num_return_sequences = 3
        beam_outputs = self.model.generate(
            input_ids=input_ids, attention_mask=attention_masks,
            do_sample=True,
            max_length=256,
            top_k=120,
            top_p=0.98,
            early_stopping=True,
            num_return_sequences=num
        )

        #         print ("\nOriginal Question ::")
        #         print (text)
        #         print ("\n")
        #         print ("Paraphrased Questions :: ")
        final_outputs = []
        for beam_output in beam_outputs:
            sent = self.tokenizer.decode(beam_output, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            if sent.lower() != self.sentence.lower() and sent not in final_outputs:
                final_outputs.append(sent)

        output = {}
        output['Question'] = text
        output['Count'] = num
        output['Paraphrased Questions'] = final_outputs

        # for i, final_output in enumerate(final_outputs):
        #     print("{}: {}".format(i, final_output))

        if torch.device == 'cuda':
            torch.cuda.empty_cache()

        return output

# class GenerateParaphraseQuestions:
#     def paraphrase():
#         ls= [{"Question":"How many versions of the remote-work model are there?",
#             "Paraphrased_Question":['Is there a full list of available remote-work models?',
#              ' How many are there?', 'How many versions of remote-work models are there?',
#              'What are the current versions of remote work models?'],
#             "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#             working remotely means replicating the activities that usually happened in the office.'''},
#              {"Question": "How many versions of the remote-work model are there?",
#               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                        ' How many are there?', 'How many versions of remote-work models are there?',
#                                        'What are the current versions of remote work models?'],
#               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                          working remotely means replicating the activities that usually happened in the office.'''},
#              {"Question": "How many versions of the remote-work model are there?",
#               "Paraphrased_Question": ['Is there a full list of available remote-work models?',],
#               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                          working remotely means replicating the activities that usually happened in the office.'''},
#              {"Question": "How many versions of the remote-work model are there?",
#               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                        'What are the current versions of remote work models?'],
#               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                          working remotely means replicating the activities that usually happened in the office.'''},
#              {"Question": "How many versions of the remote-work model are there?",
#               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                        'How many versions of remote-work models are there?',
#                                        'What are the current versions of remote work models?'],
#               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                          working remotely means replicating the activities that usually happened in the office.'''}
#              ]
#         return ls