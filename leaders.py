__author__ = 'Megan Ruthven'
import re
from nltk.corpus import stopwords
import pandas as pd
import json
import os

from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
print "Lets look at those datas";
dataPath = 'your_path_to_hh_data.csv';

runName = 'ref_'
reader = pd.read_csv(dataPath, encoding='utf-8')
#reader = reader[reader.group_name != 'Ladies Storm Hackathons'].reset_index();
#reader = reader[reader.group_name == 'Hackathon Hackers'].reset_index();

likes = reader[reader.type == 'like'];
comments = reader[reader.type != 'like'];
#comments = comments[comments['parent_type'] == 'group']
comments['date'] = pd.to_datetime(comments['created_time'])
comments.index=comments['date']
comments.index = comments.index.tz_localize('UTC').tz_convert('US/Central')
beginning = pd.to_datetime("2014-07-01")
comments = comments[comments.index >= beginning]


tops = 20;
named = 'all'
if not os.path.exists(named):
    os.makedirs(named)
members = comments.groupby(['from_id', 'from_name'])

res = members['type'].count();
res = res.reset_index();
res = res.sort(columns = 'type', ascending = False)
out = res[['from_name', 'type']][0:tops]
out.columns = ['Name', 'Number of Content']
out.to_csv(named + '\\top_content_creators.csv', sep=',', encoding='utf-8', index = False);

res = members['like_count'].sum();
res = res.reset_index();
res = res.sort(columns = 'like_count', ascending = False)
out = res[['from_name', 'like_count']][0:tops]
out.columns = ['Name', 'Number of likes']

out.to_csv(named + '\\top_liked.csv', sep=',', encoding='utf-8', index = False);

res = members['like_count'].median();
pes = members['type'].count();
res = pd.concat([res, pes], axis=1, join='inner')
res = res.reset_index();
res = res[res['type'] >=10]
res = res.sort(columns = 'like_count', ascending = False)
out = res[['from_name', 'like_count']][0:tops]
out.columns = ['Name', 'Median likes']
out.to_csv(named + '\\top_median_liked.csv', sep=',', encoding='utf-8', index = False);

members = comments[comments['parent_type'] == 'group'].groupby(['from_id', 'from_name'])

res = members['type'].count();
res = res.reset_index();
res = res.sort(columns = 'type', ascending = False)
out = res[['from_name', 'type']][0:tops]
out.columns = ['Name', 'Number of Content']
out.to_csv(named + '\\top_posts_creators.csv', sep=',', encoding='utf-8', index = False);

res = members['like_count'].median();
pes = members['type'].count();
res = pd.concat([res, pes], axis=1, join='inner')
res = res.reset_index();
res = res[res['type'] >=10]
res = res.sort(columns = 'like_count', ascending = False)
out = res[['from_name', 'like_count']][0:tops]
out.columns = ['Name', 'Median likes']
out.to_csv(named + '\\top_posts_median_liked.csv', sep=',', encoding='utf-8', index = False);


members = likes.groupby(['from_id', 'from_name'])

res = members['type'].count();
res = res.reset_index();
res = res.sort(columns = 'type', ascending = False)
out = res[['from_name', 'type']][0:tops]
out.columns = ['Name', 'Number of Content']
out.to_csv(named + '\\top_give_likes.csv', sep=',', encoding='utf-8', index = False);

print 'Determined most active overall'

grouped = comments.groupby('group_name');
for name, group in grouped:
    if len(group) > 1000:
        named = re.sub('[^0-9a-zA-Z]+', '_',(name.encode('latin-1',errors='ignore')))
        if not os.path.exists(named):
            os.makedirs(named)
        members = group.groupby(['from_id', 'from_name'])

        res = members['type'].count();
        res = res.reset_index();
        res = res.sort(columns = 'type', ascending = False)
        out = res[['from_name', 'type']][0:tops]
        out.columns = ['Name', 'Number of Content']
        out.to_csv(named + '\\top_content_creators.csv', sep=',', encoding='utf-8', index = False);

        res = members['like_count'].sum();
        res = res.reset_index();
        res = res.sort(columns = 'like_count', ascending = False)
        out = res[['from_name', 'like_count']][0:tops]
        out.columns = ['Name', 'Number of likes']

        out.to_csv(named + '\\top_liked.csv', sep=',', encoding='utf-8', index = False);

        res = members['like_count'].median();
        pes = members['type'].count();
        res = pd.concat([res, pes], axis=1, join='inner')
        res = res.reset_index();
        res = res[res['type'] >=10]
        res = res.sort(columns = 'like_count', ascending = False)
        out = res[['from_name', 'like_count']][0:tops]
        out.columns = ['Name', 'Median likes']
        out.to_csv(named + '\\top_median_liked.csv', sep=',', encoding='utf-8', index = False);

        members = group[group['parent_type'] == 'group'].groupby(['from_id', 'from_name'])

        res = members['type'].count();
        res = res.reset_index();
        res = res.sort(columns = 'type', ascending = False)
        out = res[['from_name', 'type']][0:tops]
        out.columns = ['Name', 'Number of Posts']
        out.to_csv(named + '\\top_posts_creators.csv', sep=',', encoding='utf-8', index = False);

        res = members['like_count'].median();
        pes = members['type'].count();
        res = pd.concat([res, pes], axis=1, join='inner')
        res = res.reset_index();
        res = res[res['type'] >=10]
        res = res.sort(columns = 'like_count', ascending = False)
        out = res[['from_name', 'like_count']][0:tops]
        out.columns = ['Name', 'Median likes']
        out.to_csv(named + '\\top_posts_median_liked.csv', sep=',', encoding='utf-8', index = False);

        print 'Finished most active for ' + named + ' subgroup'

grouped = pd.groupby(comments,by=[comments.index.year,comments.index.week])
res = grouped['type'].count();
res = res.reset_index();
res['year_month'] = [str(row['level_0']) +', ' + str(row['level_1']) for (i, row) in res.iterrows()]
out = res[['year_month', 'type']]
out = out.set_index('year_month')
out.plot(kind='bar').set_title('Number of posts by week').set_fontsize(36)
#

res = comments.groupby('like_count');
res = res['type'].count();
plt.figure();
ax = res.plot(x_compat=True, title = 'Count of # of likes on content', logx= True, logy = True)
ax.set_xlabel('# likes on content')
ax.set_ylabel('# content with those likes')
print "fin"