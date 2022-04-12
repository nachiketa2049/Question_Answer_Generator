from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline #4.17.0
import numpy
from question_paraphraser import GenerateParaphraseQuestions
from haystack.nodes import QuestionGenerator
import re
import warnings
import smtplib, ssl
from app import db, UserData, QuestionAnswer


def generate_question_answer(text,user_id, email):
    warnings.simplefilter("ignore")
    print("started")

    # Load model for question generation via haystack
    question_generator = QuestionGenerator(model_name_or_path="valhalla/t5-base-e2e-qg")

    # generate questions and store it into list
    question_list = question_generator.generate(text)

    # Load model & tokenizer for answer generation
    model_name = "deepset/roberta-base-squad2"
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Generate answers and store it into list
    nlp = pipeline('question-answering', model=model, tokenizer=tokenizer)
    answer_list=[]
    for i in question_list:
        QA_input = {
            'question': i,
            'context':text
        }
        answer_list.append(nlp(QA_input))

    # Convert one word answer into full sentence
    full_answer_list=[]
    for i in range(len(question_list)):
        full_answer_list.append(re.findall(r"([^.]*{}[^.]*)".format(text[answer_list[i]["start"]:answer_list[i]["end"]]),text))

    #generate paraphrase question
    paraphrase_question= GenerateParaphraseQuestions()
    paraphrased_list=[]
    for i in question_list:
        payload2 = {
            "input_text" : i,
            "max_questions": 3
        }
        output = paraphrase_question.paraphrase(payload2)
        paraphrased_list.append(output['Paraphrased Questions'])

    #For test purpose to print output just uncomment bolow code

    # for i in range(len(res)):
    #     print(res[i])
    #     for j in paraphrased_list[i]:
    #         print(" "+j)
    #     print('\n')
    #     print(full_answer_list[i])
    #     print('\n')
    #     print('-------------------------------------------------------------------------------------------------')

    # Creating a list for all question answer pairs containing question, paraphrased questions and answer in dictionary
    # Format be like [{question:'', paraphrase_question:'',answer:''},{question:'', paraphrase_question:'',answer:''}]

    question_answer_pairs=[]
    for i in range(len(question_list)):
        question_answer_dict={}
        question_answer_dict['Question']=question_list[i]
        question_answer_dict['Paraphrased_Question'] =paraphrased_list[i]
        question_answer_dict['Answer']=full_answer_list[i]
        question_answer_pairs.append(question_answer_dict)

    user = UserData.query.filter_by(user_id=user_id).first()
    qa=QuestionAnswer.query.filter_by(user_id=user.user_id).all()
    if qa:
        timestamp = qa[-1].timestamp + 1
    else:
        timestamp=0

    for question_answer in question_answer_pairs:
        que_ans = QuestionAnswer(user_id=user.user_id,
                                 question=question_answer['Question'],
                                 paraphrased_question=str(question_answer['Paraphrased_Question']),
                                 answer=question_answer['Answer'][0],
                                 timestamp=timestamp)
        db.session.add(que_ans)
        db.session.commit()

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "nlquest001@gmail.com"  # Enter your email address
    receiver_email = email  # Enter receiver's email address
    password = "tzexydyeosxtbzht"
    message = """\
Subject: Voila! Your Questions and Answers are ready
Your Questions and Answers are generated. Kindly check your Dashboard."""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print("ended")
    return question_answer_pairs


# from question_paraphraser import GenerateParaphraseQuestions
#
# def generate_question_answer(text,user_id, email):
#     # #question_answer_pairs = qg.paraphrase()
#     question_answer_pairs = [{"Question": "How many versions of the remote-work model are there?",
#                               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                                        'How many are there?',
#                                                        'How many versions of remote-work models are there?',
#                                                        'What are the current versions of remote work models?'],
#                               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                 working remotely means replicating the activities that usually happened in the office.'''},
#                              {"Question": "How many versions of the remote-work model are there?",
#                               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                                        ' How many are there?',
#                                                        'How many versions of remote-work models are there?',
#                                                        'What are the current versions of remote work models?'],
#                               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                              working remotely means replicating the activities that usually happened in the office.'''},
#                              {"Question": "How many versions of the remote-work model are there?",
#                               "Paraphrased_Question": ['Is there a full list of available remote-work models?', ],
#                               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                              working remotely means replicating the activities that usually happened in the office.'''},
#                              {"Question": "How many versions of the remote-work model are there?",
#                               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                                        'What are the current versions of remote work models?'],
#                               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                              working remotely means replicating the activities that usually happened in the office.'''},
#                              {"Question": "How many versions of the remote-work model are there?",
#                               "Paraphrased_Question": ['Is there a full list of available remote-work models?',
#                                                        'How many versions of remote-work models are there?',
#                                                        'What are the current versions of remote work models?'],
#                               "Answer": '''There isn’t a single version for the remote-work model: For most companies,
#                              working remotely means replicating the activities that usually happened in the office.'''}
#                              ]
#     user = UserData.query.filter_by(user_id=user_id).first()
#     for question_answer in question_answer_pairs:
#         que_ans=QuestionAnswer(user_id=user.user_id,
#                                question=question_answer['Question'],
#                                paraphrased_question=str(question_answer['Paraphrased_Question']),
#                                answer=question_answer['Answer'])
#         db.session.add(que_ans)
#         db.session.commit()
#     print(email)
#     return question_answer_pairs
