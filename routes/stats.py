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
    df = pd.read_csv(root_dir + filename, index_col="qid")
    df = df.fillna("")
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
    
    