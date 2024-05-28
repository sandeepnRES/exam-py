import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')

def get_stats(root_dir, filename):
    """
    'subject'
    is_correct'
    'correct_ans'
    'user_ans'
    """
    CORRECT=1
    INCORRECT=-1
    df = read_df(root_dir, filename)
    correct_ans = df[df['is_correct']==CORRECT].groupby('subject').count()
    wrong_ans = df[df['is_correct']==INCORRECT].groupby('subject').count()
    seen_ques = df[df['user_ans']=="-"].groupby('subject').count()
    unseen_ans = df[df['user_ans']==""].groupby('subject').count()
    stats_df = pd.DataFrame({'Correct': correct_ans['is_correct'], 
                             'Wrong': wrong_ans['is_correct'], 
                             'Seen': seen_ques['user_ans'], 
                             'Unseen': unseen_ans['user_ans']})
    stats_df = stats_df.fillna(0)
    sdf = stats_df.transpose()
    plots = sdf.plot.pie(subplots=True, figsize=(15, 15), autopct='%1.1f%%', layout=[2,2], labeldistance=0.92, fontsize=12)
    outfilename = root_dir + os.path.splitext(os.path.basename(filename))[0] + '.jpg'
    plots[0][0].figure.savefig(outfilename, pad_inches=0, dpi=200)
    return outfilename

def read_df(root_dir, filename):
    df = pd.read_csv(root_dir + filename, index_col="qid")
    df = df.fillna("")
    df.index = df.index.astype('str')
    return df

def calc_marks(df):
    CORRECT_MARKS = 4
    WRONG_MARKS = -1
    MATHS_WEIGHT = 3
    QUANT_WEIGHT = 1.5
    CA_WEIGHT = 2
    ENG_WEIGHT = 1
    
    _isCorrect = df['is_correct'].to_dict()
    _correctAns = df['correct_ans'].to_dict()
    _userAnsJson = df['user_ans'].to_dict()
    
    marks = 0
    for q in range(1,121):
        qi = str(q)
        mark = 0
        if _isCorrect[qi] == 1:
            mark = CORRECT_MARKS
        elif _isCorrect[qi] == -1:
            mark = WRONG_MARKS

        if q<51:
            mark *= MATHS_WEIGHT
        elif q<91:
            mark *= QUANT_WEIGHT
        elif q<111:
            mark *= CA_WEIGHT
        else:
            mark *= ENG_WEIGHT
        marks += mark

    return marks
    