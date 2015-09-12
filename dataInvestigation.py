__author__ = 'Megan Ruthven'
import re
from nltk.corpus import stopwords
import pandas as pd
import json
import math
import statistics

print "Lets look at those datas";
dataPath = 'C:\\Users\\mar3939\\Desktop\\HH\\08202015_datefix.csv';
stop = stopwords.words('english')
with open('config.json') as in_json:
    data = json.load(in_json);

    male = [word.lower().strip() for word in data['male']];
    mset = set(male);
    female = [word.lower().strip() for word in data['female']];
    fset = set(female);

topX = 10;
colNames = ('year_month', 'male_count', 'male_mean', 'male_conf', 'female_count', 'female_mean', 'female_conf', 'both_count', 'both_mean', 'both_conf', 'none_count', 'none_mean', 'none_conf', 'total_posts', 'gendered_posts','perc_gender', 'perc_female');
def calculateGenderStats(comments):
    totCount = [0,0,0,0];
    totNum = [[],[],[],[]];

    for index, row in comments.iterrows():
        if len(row['norm_message']) > 0:
            normM =  set(row['norm_message'].split());
            if bool(mset & normM):
                totCount[0] += 1;
                totNum[0].append(row['norm_likes']);
            if bool(fset & normM):
                totCount[1] += 1;
                totNum[1].append(row['norm_likes']);
            if bool(mset & normM) & bool(fset & normM):
                totCount[2] += 1;
                totNum[2].append(row['norm_likes']);
            if (bool(mset & normM) | bool(fset & normM)) == False:
                totCount[3] += 1;
                totNum[3].append(row['norm_likes']);

    meanL =[0,0,0,0];
    confL = [0,0,0,0];
    for i in range(0, 4):
        if totCount[i] == 0:
            meanL[i] = float('nan');
            confL[i] = float('nan')
        else:
            totNum[i].sort();
            N = len(totNum[i])-1
            low = int(round(N/2 - 1.96*math.sqrt(N)/2));
            high = int(round(N/2 + 1+ 1.96*math.sqrt(N)/2));
            midl = int(math.floor(N/2));
            midh = int(math.ceil(N/2));
            if low < 0:
                low = 0;
            if high > N:
                high = N;
            if midl < 0:
                midl = 0;
            if midh > N:
                midh = N;
            meanL[i] = (totNum[i][midl] + totNum[i][midh])/2;

            confL[i] = (meanL[i] - totNum[i][low], totNum[i][high] - meanL[i])

            #meanL[i] = statistics.median(totNum[i]) #sum(totNum[i])/len(totNum[i]); #totNum[i] / totCount[i];
            #var = map(lambda x: (x - meanL[i])**2, totNum[i]);
            #confL[i] = 1.96*math.sqrt(sum(var)/len(var))/math.sqrt(len(totNum[i]))


    print 'Male words present had ' + str(totCount[0]) + ' occurrences in HH and averaged ' + str(meanL[0]) + ' likes'
    print 'Female words present had ' + str(totCount[1]) + ' occurrences in HH and averaged ' + str(meanL[1]) + ' likes'
    print 'Both female and male present had ' + str(totCount[2]) + ' occurrences in HH and averaged ' + str(meanL[2]) + ' likes'
    print 'Both no female or male present had ' + str(totCount[3]) + ' occurrences in HH and averaged ' + str(meanL[3]) + ' likes'

    totalPosts = totCount[0] + totCount[1] + totCount[3] - totCount[2];
    genderPosts = totCount[0] + totCount[1] - totCount[2];
    percGender = 100.0* genderPosts/totalPosts;
    if genderPosts == 0:
        percFemale = float('nan');
    else:
        percFemale = 100.0 * totCount[1]/genderPosts;
    print 'The percentage of posts that had at least one gender is: ' + str(percGender) + '%';
    print 'The percentage of posts with female pronouns of the gendered set is: ' + str(percFemale) + '%'

    outputInfo = [totCount[0], meanL[0], confL[0], totCount[1], meanL[1], confL[1], totCount[2], meanL[2], confL[2], totCount[3], meanL[3], confL[3], totalPosts, genderPosts, percGender, percFemale]
    return outputInfo;


runName = 'all_posts'
reader = pd.read_csv(dataPath, encoding='utf-8')
reader = reader[reader.group_name != 'Ladies Storm Hackathons'].reset_index();
#reader = reader[reader.group_name == 'Hackathon Hackers'].reset_index();

likes = reader[reader.type == 'like'];
comments = reader[reader.type != 'like'];
#comments = comments[comments['parent_type'] == 'group']
comments['norm_message'] = [re.sub('[^0-9a-zA-Z\x20]+', ' ', re.sub('\'+', '', row.encode('latin-1','ignore'))).lower().strip() if isinstance(row, unicode) else '' for row in comments.message]
likeMean = 0 # comments['like_count'].mean();
print likeMean;
comments['norm_likes'] = comments['like_count'];#[(cou - likeMean) for cou in comments['like_count']];

comments['date'] = pd.to_datetime(comments['created_time'])
comments = comments.sort(['date'])
comments.index=comments['date']
comments.index = comments.index.tz_localize('UTC').tz_convert('US/Central')


calculateGenderStats(comments)
#per = comments['date'].to_period("M")

comments['dow'] = comments.index.weekday;
grouped = comments.groupby('dow')
#    outputInfo = [totCount[0], meanL[0], totCount[1], meanL[1], totCount[2], meanL[2], totCount[3], meanL[3], totalPosts, genderPosts, percGender, percFemale]

res = pd.DataFrame(columns=colNames)
dictOut = dict();
for name, group in grouped:
    print name
    out = ((calculateGenderStats(group)))
    tout = [str(name)] + out;
    for i in range(0, len(tout)):
        dictOut[colNames[i]] = tout[i]
    res = res.append(dictOut, ignore_index = True)

resDates = res;
res.to_csv(runName + '_dow.csv', sep=',');

comments['hour'] = comments.index.hour;
grouped = comments.groupby('hour')
#    outputInfo = [totCount[0], meanL[0], totCount[1], meanL[1], totCount[2], meanL[2], totCount[3], meanL[3], totalPosts, genderPosts, percGender, percFemale]

res = pd.DataFrame(columns=colNames)
dictOut = dict();
for name, group in grouped:
    print name
    out = ((calculateGenderStats(group)))
    tout = [str(name)] + out;
    for i in range(0, len(tout)):
        dictOut[colNames[i]] = tout[i]
    res = res.append(dictOut, ignore_index = True)

resDates = res;
res.to_csv(runName + '_hour.csv', sep=',');
# tt = res[['year_month','perc_gender']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Percentage of posts mentioning a gender over time').set_fontsize(36)
#
#
# tt = res[['year_month','perc_female']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Percentage of gendered posts with female over time').set_fontsize(36)
#
# tt = res[['year_month','male_mean', 'female_mean', 'both_mean', 'none_mean']];
# tt = tt.set_index('year_month')
# tterr = res[['year_month','male_conf', 'female_conf', 'both_conf', 'none_conf']];
# tterr = tterr.set_index('year_month')
# tt.plot(yerr = tterr.values.T, kind='bar').set_title('Mean likes for posts in gendered categories over groups').set_fontsize(36)
#
# tt = res[['year_month','total_posts']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('total posts over time')
#
# tt = res[['year_month','gendered_posts']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Total gendered posts over time').set_fontsize(36)

#comments.index=comments['date']
grouped = pd.groupby(comments,by=[comments.index.year,comments.index.month])
#    outputInfo = [totCount[0], meanL[0], totCount[1], meanL[1], totCount[2], meanL[2], totCount[3], meanL[3], totalPosts, genderPosts, percGender, percFemale]

res = pd.DataFrame(columns=colNames)
dictOut = dict();
for name, group in grouped:
    if name[0] >= 2015 or (name[0] == 2014 and name[1] >=7) :
        print name
        out = ((calculateGenderStats(group)))
        tout = [str(name)] + out;
        for i in range(0, len(tout)):
            dictOut[colNames[i]] = tout[i]
        res = res.append(dictOut, ignore_index = True)

resDates = res;
res.to_csv(runName + '_month_year.csv', sep=',');

# tt = res[['year_month','perc_gender']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Percentage of posts mentioning a gender over time').set_fontsize(36)
#
#
# tt = res[['year_month','perc_female']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Percentage of gendered posts with female over time').set_fontsize(36)
#
# tt = res[['year_month','male_mean', 'female_mean', 'both_mean', 'none_mean']];
# tt = tt.set_index('year_month')
# tterr = res[['year_month','male_conf', 'female_conf', 'both_conf', 'none_conf']];
# tterr = tterr.set_index('year_month')
# tt.plot(yerr = tterr.values.T, kind='bar').set_title('Mean likes for posts in gendered categories over groups').set_fontsize(36)
#
# tt = res[['year_month','total_posts']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('total posts over time')
#
# tt = res[['year_month','gendered_posts']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Total gendered posts over time').set_fontsize(36)

grouped = comments.groupby('group_name');
res = pd.DataFrame(columns=colNames)
dictOut = dict();
for name, group in grouped:
    if name[0] >= 2014 :
        print name.encode('latin-1','ignore')
        out = ((calculateGenderStats(group)))
        tout = [name.encode('latin-1','ignore')] + out;
        for i in range(0, len(tout)):
            dictOut[colNames[i]] = tout[i]
        res = res.append(dictOut, ignore_index = True)

resGroup = res;
res.to_csv(runName + '_groups.csv', sep=',');


# tt = res[['year_month','perc_gender']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Percentage of posts mentioning a gender over groups').set_fontsize(36)
#
#
# tt = res[['year_month','perc_female']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Percentage of gendered posts with female over groups').set_fontsize(36)
#
# tt = res[['year_month','male_mean', 'female_mean', 'both_mean', 'none_mean']];
# tt = tt.set_index('year_month')
# tterr = res[['year_month','male_conf', 'female_conf', 'both_conf', 'none_conf']];
# tterr = tterr.set_index('year_month')
# tt.plot(yerr = tterr.values.T, kind='bar').set_title('Mean likes for posts in gendered categories over groups').set_fontsize(36)
#
# tt = res[['year_month','total_posts']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('total posts over groups').set_fontsize(36)
#
# tt = res[['year_month','gendered_posts']];
# tt = tt.set_index('year_month')
# tt.plot(kind='bar').set_title('Total gendered posts over groups').set_fontsize(36)