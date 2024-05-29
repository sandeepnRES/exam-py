from flask import Blueprint, request, jsonify, send_file, render_template
from os import environ
import os
from os import listdir
from os.path import isfile, join
import json
import pandas as pd
from routes.stats import get_stats, read_df, calc_marks

# load_dotenv(find_dotenv())
from datetime import timedelta, datetime

answers_dict = dict()
correct = dict()
subjects=['maths', 'quants', 'cs_eng']
sub_q = [1, 51, 91]
sub_time = [70, 30, 20]

exam_started = False
start_time = datetime.now()
curr_qid = 1
curr_sub_id = 0
curr_paper_id = "2021"
all_paper_ids = ["2019", "2020", "2021", "2022"]
username = "demo"

def get_username():
    global username
    return username

def set_username(uname):
    global username
    username = uname.lower()

def get_file_root():
    global curr_paper_id
    return "paper/"+str(curr_paper_id)+"/"
    
def get_user_file_root():
    global curr_paper_id
    global username
    usr_dir = get_file_root()+"results_" + username + "/"
    if not os.path.exists(usr_dir):
        os.makedirs(usr_dir)
    return usr_dir

bp = Blueprint('asksherlock_api', __name__)


def get_time_left():
    global start_time
    global curr_sub_id
    curr_time = datetime.now()
    time_diff = curr_time - start_time
    print("ct", curr_time)
    print("st", start_time)
    exam_time = timedelta(minutes=sub_time[curr_sub_id])
    # exam_time = timedelta(seconds=10)
    rem_time = exam_time - time_diff
    if rem_time >= timedelta(seconds=0):
        return rem_time.seconds
    else:
        return -1

def get_timer():
    rem_time_secs = get_time_left()
    if rem_time_secs >= 0:
        rem_min = rem_time_secs // 60;
        rem_sec = rem_time_secs % 60;
        timer_init = str(rem_min) + ":" + str(rem_sec)
        print("ti", timer_init)
        return timer_init
    else:
        return "-1"

@bp.route('/get_all_paperids', methods=['GET'])
def get_all_paperids():
    return jsonify({'all_paperids': all_paper_ids})

@bp.route('/next_subject', methods=['GET'])
def next_subject():
    global curr_sub_id
    global curr_qid
    global start_time
    start_time = datetime.now()
    curr_sub_id += 1
    curr_qid = sub_q[curr_sub_id]
    return render_template('exam.html', time_left = get_timer(), q_id=curr_qid, s_id=curr_sub_id)

@bp.route('/exam', methods=['GET'])
def exam():
    global curr_qid
    global exam_started
    global curr_sub_id
    global start_time
    global answers_dict
    global correct
    global curr_paper_id
    
    if not exam_started:
        exam_started = True
        start_time = datetime.now()
        curr_qid = 1
        curr_sub_id = 0
        answers_dict = dict()
        correct = dict()
        if "paperid" in request.args:
            curr_paper_id = request.args['paperid']
        else:
            curr_paper_id = "2021"
            
        if "username" in request.args:
            set_username(request.args["username"])
        
    print(request)
    # time_left = get_timer()
    # if time_left == -1:
    #     return next_subject()
    # else:
    if not "qnum" in request.args:
        qid = str(curr_qid)
        print("First Call: ", qid)
        print("Sub id: ", curr_sub_id)
    else:
        print(request.args)
        qid = request.args['qnum']
    return render_template('exam.html', time_left = get_timer(), q_id=qid, s_id=curr_sub_id)

@bp.route('/question', methods=['GET']) 
def question(): 
    global curr_sub_id
    print(request)
    if not "num" in request.args:
        qnum = 1
    else:
        qnum = request.args['num']
    
    subject = subjects[curr_sub_id]
    filename=get_file_root()+subject+"/q"+str(qnum)+".png"
            
    return send_file(filename, mimetype='image/png')
    
@bp.route('/answer', methods=['GET']) 
def answer(): 
    print(request)
    if not "qnum" in request.args:
        msg = 'Need to provide \'qnum\' in body'
        print(msg)
        return jsonify({"message": msg}), 400
    if not "ans" in request.args:
        msg = 'Need to provide \'ans\' in body'
        print(msg)
        return jsonify({"message": msg}), 400
    
    qnum = request.args['qnum']
    ans = request.args['ans']
    answers_dict[qnum] = ans;
            
    return jsonify({'is_answered': True})
    
@bp.route('/isanswered', methods=['GET']) 
def isanswered(): 
    if not "qnum" in request.args:
        msg = 'Need to provide \'qnum\' in body'
        print(msg)
        return jsonify({"message": msg}), 400
    
    qnum = request.args['qnum']
    response = qnum in answers_dict and answers_dict[qnum] != ""
            
    return jsonify({'is_answered': response})
    
@bp.route('/getanswers', methods=['GET']) 
def getanswers():
    res = json.dumps(answers_dict)
    return jsonify({'answers': res})
 

@bp.route('/result', methods=['GET'])
def result():
    global exam_started
    exam_started = False
    with open(get_file_root() + 'answer.json', 'r') as file:
        ansJson = file.read().rstrip()
    answersDict = json.loads(ansJson)
    subsDict = dict()
    userAnsDict = dict()
    for q in range(1,121):
        qi = str(q)
        correct[qi] = 0
        if qi in answers_dict:
            userAnsDict[qi] = answers_dict[qi]
            if answersDict[qi] == answers_dict[qi]:
                correct[qi] = 1     # Correct Ans
            elif answers_dict[qi] != "":
                correct[qi] = -1    # Wrong Ans
            else:
                userAnsDict[qi] = "-"
            
            if answersDict[qi] == "*":
                correct[qi] = 1     # Correct Ans
        if q<51:
            subsDict[qi] = 'Mathematics'
        elif q<91:
            subsDict[qi] = 'Quantitative Aptitude'
        elif q<111:
            subsDict[qi] = 'Computer Awareness'
        else:
            subsDict[qi] = 'English'

    df_dict = {'subject': subsDict, 'is_correct': correct, 'correct_ans': answersDict, 'user_ans': userAnsDict}
    df = pd.DataFrame(df_dict, index=subsDict.keys())
    marks = calc_marks(df)
    filename = 'res_'+str(datetime.now())+'.csv'
    df.to_csv(get_user_file_root() + filename, index_label="qid");
    df.to_csv(get_user_file_root() + 'res_last.csv', index_label="qid");
    return render_template('result.html', result=marks, username = get_username(), curr_filename = filename)
    
@bp.route('/getresultdetails', methods=['GET'])
def getresultdetails():
    with open(get_file_root() + 'answer.json', 'r') as file:
        ansJson = file.read().rstrip()
    correctJson = json.dumps(correct)
    uAnsJson = json.dumps(answers_dict)
    imfilename = get_stats(get_user_file_root(), 'res_last.csv')

    return jsonify({'is_correct': correctJson, 'correct_ans': ansJson, 'user_ans': uAnsJson, 'imfilename': imfilename})
    
@bp.route('/get_result_image', methods=['GET'])
def get_result_image():
    filename = get_user_file_root() + 'res_last.jpg'
    if 'imfilename' in request.args:
        filename = request.args['imfilename']
    return send_file(filename, mimetype='image/jpg')

@bp.route('/getresultlist', methods=['GET'])
def getresultlist():
    def check_csv_file(res_dir, filename):
        if isfile(join(res_dir, filename)):
            ext = os.path.splitext(filename)[-1].lower()
            if ext == '.csv':
                return True
        return False

    res_dir = get_user_file_root()
    onlyfiles = [f for f in listdir(res_dir) if check_csv_file(res_dir, f)]
    return jsonify({'resultlist': onlyfiles})

@bp.route('/getresultbyname', methods=['GET'])
def getresultbyname():
    if 'filename' in request.args:
        filename = request.args['filename']
    else:
        filename = 'res_last.csv'
    df = read_df(get_user_file_root(), filename)
    imfilename = get_stats(get_user_file_root(), filename)
    correctJson = json.dumps(df['is_correct'].to_dict())
    ansJson = json.dumps(df['correct_ans'].to_dict())
    uAnsJson = json.dumps(df['user_ans'].to_dict())
    marks = calc_marks(df)
 
    return jsonify({'marks': marks, 'is_correct': correctJson, 'correct_ans': ansJson, 'user_ans': uAnsJson, 'imfilename': imfilename})

@bp.route('/result_history', methods=['GET'])
def result_history():
    global curr_paper_id
    global username
    
    if "paperid" in request.args:
        curr_paper_id = request.args['paperid']
    else:
        curr_paper_id = "2021"
        
    if "username" in request.args:
        username = request.args["username"]
    else:
        username = "demo"

    return render_template('result_history.html', username = get_username())

def init():
    print('Init function called...')
    