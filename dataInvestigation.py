__author__ = 'Megan Ruthven'
import re
from nltk.corpus import stopwords
import pandas as pd
import json


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
colNames = ('year_month', 'male_count', 'male_mean', 'female_count', 'female_mean', 'both_count', 'both_mean', 'none_count', 'none_mean', 'total_posts', 'gendered_posts','perc_gender', 'perc_female');
def calculateGenderStats(comments):
    totCount = [0,0,0,0];
    totNum = [0,0,0,0];

    for index, row in comments.iterrows():
        if len(row['norm_message']) > 0:
            normM =  set(row['norm_message'].split());
            if bool(mset & normM):
                totCount[0] += 1;
                totNum[0] += row['norm_likes'];
            if bool(fset & normM):
                totCount[1] += 1;
                totNum[1] += row['norm_likes'];
            if bool(mset & normM) & bool(fset & normM):
                totCount[2] += 1;
                totNum[2] += row['norm_likes'];
            if (bool(mset & normM) | bool(fset & normM)) == False:
                totCount[3] += 1;
                totNum[3] += row['norm_likes'];

    meanL =[0,0,0,0];
    for i in range(0, 4):
        if totCount[i] == 0:
            meanL[i] = float('nan');
        else:
            meanL[i] = totNum[i] / totCount[i];


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

    outputInfo = [totCount[0], meanL[0], totCount[1], meanL[1], totCount[2], meanL[2], totCount[3], meanL[3], totalPosts, genderPosts, percGender, percFemale]
    return outputInfo;


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



#dict = defaultdict(list);
#for index, row in comments.iterrows():
#    normLikes = row['norm_likes'];
#    for mm in set(row['norm_message'].split()):
#        dict[mm].append(normLikes);

#mdict = [(k, len(l), reduce(lambda x, y: x + y, l) / len(l)) for k, l in dict.items() if len(l) >= 25]
#mdict.sort(key=itemgetter(2))
#print len(mdict)
#print "popular mean words in HH"
#for word, count, mean in mdict[-100:-1]:
#    print word + '\t| ' + str(mean) + '\t| ' + str(count);

#print "unpopular mean words in HH"
#for word, count, mean in mdict[0:100]:
#    print word + '\t| ' + str(mean) + '\t| ' + str(count);



calculateGenderStats(comments)
#per = comments['date'].to_period("M")
comments.index=comments['date']
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
tt = res[['year_month','perc_gender']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Percentage of posts mentioning a gender over time').set_fontsize(36)


tt = res[['year_month','perc_female']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Percentage of gendered posts with female over time').set_fontsize(36)

tt = res[['year_month','male_mean', 'female_mean', 'both_mean', 'none_mean']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Mean likes for posts in gendered categories over time').set_fontsize(36)


tt = res[['year_month','total_posts']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('total posts over time')

tt = res[['year_month','gendered_posts']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Total gendered posts over time').set_fontsize(36)
# fig, ax = plt.subplots()
# index = np.arange(len(names))
# bar_width = 0.35
# opacity = 0.4
# #
# rects1 = plt.bar(index, means_men, bar_width, color='b', label = 'Male')
# rects2= plt.bar(index + bar_width*1, means_women, bar_width, color='r', label = 'Female')
# rects3= plt.bar(index + bar_width*2, means_both, bar_width, color='g', label = 'Both')
# rects4= plt.bar(index + bar_width*3, means_none, bar_width, color='black', label = 'None')
#
# plt.xlabel('Year, month')
# plt.ylabel('Mean Likes per Post')
# plt.title('Mean Likes per Post over Time')
# plt.xticks(index + bar_width*2, names)
# plt.legend()
#
# fig, ax = plt.subplots()
# index = np.arange(len(names))
# bar_width = 0.35
# opacity = 0.4
# #
# rects1 = plt.bar(index , perc_female, bar_width, color='b')
#
# plt.xlabel('Year, month')
# plt.ylabel('Percentage female')
# plt.title('Percentage female over Time')
# plt.xticks(index + bar_width*0.5, names)
# plt.legend()
#
# fig, ax = plt.subplots()
# index = np.arange(len(names))
# bar_width = 0.35
# opacity = 0.4
# #
# rects1 = plt.bar(index , one_gender, bar_width, color='b')
#
# plt.xlabel('Year, month')
# plt.ylabel('Percentage posts gendered')
# plt.title('Percentage posts gendered over Time')
# plt.xticks(index + bar_width*0.5, names)
# plt.legend()
#
# #plt.tight_layout()
# plt.show()
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

tt = res[['year_month','perc_gender']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Percentage of posts mentioning a gender over groups').set_fontsize(36)


tt = res[['year_month','perc_female']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Percentage of gendered posts with female over groups').set_fontsize(36)

tt = res[['year_month','male_mean', 'female_mean', 'both_mean', 'none_mean']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Mean likes for posts in gendered categories over groups').set_fontsize(36)


tt = res[['year_month','total_posts']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('total posts over groups').set_fontsize(36)

tt = res[['year_month','gendered_posts']];
tt = tt.set_index('year_month')
tt.plot(kind='bar').set_title('Total gendered posts over groups').set_fontsize(36)