__author__ = 'Megan Ruthven'
import re
from nltk.corpus import stopwords
import pandas as pd
import json
import numpy as np


print "Lets look at those datas";
dataPath = 'your_path';
stop = stopwords.words('english')
with open('config.json') as in_json:
    data = json.load(in_json);

    male = [word.lower().strip() for word in data['male']];
    mset = set(male);
    female = [word.lower().strip() for word in data['female']];
    fset = set(female);

colNames = ('name', 'male_count', 'male_median', 'female_count', 'female_median', 'both_count', 'both_median', 'none_count', 'none_median', 'total_posts', 'total_median', 'gendered_posts', 'gendered_median');


def agg_groups(group, name):
    t = dict.fromkeys(colNames, 0)
    t['name'] = name;
    t['male_count'] = group['male'].sum();
    t['female_count'] = group['female'].sum();
    t['both_count'] = group['both'].sum();
    t['none_count'] = group['none'].sum();
    t['total_posts'] = group['type'].count();
    t['gendered_posts'] = t['male_count'] + t['female_count'] - t['both_count']
    t['male_median'] = group[group['male'] == 1]['like_count'].median();
    t['female_median'] = group[group['female'] == 1]['like_count'].median();
    t['none_median'] = group[group['none'] == 1]['like_count'].median();
    t['both_median'] = group[group['both'] == 1]['like_count'].median();
    t['gendered_median'] = group[group['none'] == 0]['like_count'].median();
    t['total_median'] = group['like_count'].median();
    return t;

runName = 'posts_'
reader = pd.read_csv(dataPath, encoding='utf-8')
reader = reader[reader.group_name != 'Ladies Storm Hackathons'].reset_index();
#reader = reader[reader.group_name == 'Hackathon Hackers'].reset_index();

likes = reader[reader.type == 'like'];
comments = reader[reader.type != 'like'];
comments = comments[comments['parent_type'] == 'group']
comments['norm_message'] = [re.sub('[^0-9a-zA-Z\x20]+', ' ', re.sub('\'+', '', row.encode('latin-1','ignore'))).lower().strip() if isinstance(row, unicode) else '' for row in comments.message]
likeMean = 0
print likeMean;
comments['norm_likes'] = comments['like_count'];

comments['date'] = pd.to_datetime(comments['created_time'])
comments = comments.sort(['date'])
comments.index=comments['date']
comments.index = comments.index.tz_localize('UTC').tz_convert('US/Central')
# using only dates from HH's inception onwards
comments15 = comments[comments.index.year == 2015];
comments14 = comments[comments.index.year == 2014];
comments14.index=comments14['date']
comments14 = comments14[comments14.index.month >= 7];
comments = comments15.append(comments14, ignore_index = True)

# determining gender membership
comments['male'] = [1 if mset.intersection(row.split()) else 0 for row in comments['norm_message']]
comments['female'] = [1 if fset.intersection(row.split()) else 0 for row in comments['norm_message']]
comments['both'] = [1 if row['male'] == 1 and row['female'] == 1 else 0 for (i, row) in comments.iterrows()]
comments['none'] = [0 if row['male'] == 1 or row['female'] == 1 else 1 for (i, row) in comments.iterrows()]

comments.index=comments['date']
comments.index = comments.index.tz_localize('UTC').tz_convert('US/Central')

# start of analysis on different categories in the data

grouped = pd.groupby(comments,by=[comments.index.year,comments.index.month])
res = pd.DataFrame(columns=colNames)

for name, group in grouped:
    if name[0] >= 2015 or (name[0] == 2014 and name[1] >=7) :
        print name
        t = agg_groups(group, name)
        res = res.append(t, ignore_index = True)
res.to_csv(runName + 'month_year.csv', sep=',');

grouped = pd.groupby(comments,by=[comments.index.dayofweek,comments.index.hour])
res = pd.DataFrame(columns=colNames)

for name, group in grouped:
    print name
    t = agg_groups(group, name)
    res = res.append(t, ignore_index = True)
res.to_csv(runName + 'dow_hour.csv', sep=',');

grouped = pd.groupby(comments,by=[comments.index.year, comments.index.week])
res = pd.DataFrame(columns=colNames)

for name, group in grouped:
    if name[0] >= 2015 or (name[0] == 2014 and name[1] >=30) :
        print name
        t = agg_groups(group, name)
        res = res.append(t, ignore_index = True)
res.to_csv(runName + 'week_year.csv', sep=',');

grouped = pd.groupby(comments,by=[comments.index.dayofweek])
res = pd.DataFrame(columns=colNames)

for name, group in grouped:
    print name
    t = agg_groups(group, name)
    res = res.append(t, ignore_index = True)
res.to_csv(runName + 'dow.csv', sep=',');

grouped = pd.groupby(comments,by=[comments.index.hour])
res = pd.DataFrame(columns=colNames)

for name, group in grouped:
    print name
    t = agg_groups(group, name)
    res = res.append(t, ignore_index = True)
res.to_csv(runName + 'hour.csv', sep=',');

grouped = comments.groupby('group_name');
res = pd.DataFrame(columns=colNames)

for name, group in grouped:
    print name.encode('latin-1','ignore')
    t = agg_groups(group, name.encode('latin-1','ignore'))
    res = res.append(t, ignore_index = True)
res.to_csv(runName + 'group.csv', sep=',');

print "fin"