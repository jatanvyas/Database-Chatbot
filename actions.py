from rasa_core.actions import Action
from rasa_core.events import AllSlotsReset
import logging
import ast
import pandas as pd
from fuzzywuzzy import process
import webbrowser
import matplotlib.pyplot as plt
import bs4

# --------------------------------------------------------
# set up DB
# --------------------------------------------------------

dbfile = 'db/movies_metadata.csv'
dfmaster = pd.read_csv(dbfile)
params = list(dfmaster.columns.values)
titles = dfmaster['title'].tolist()

#Copy to operate
x = dfmaster
i = 1
hi = 1

# --------------------------------------------------------
# Req. functions
# --------------------------------------------------------
#Get original name of movie
def get_movie_name(t):
    res = process.extractOne(t,titles)
    return dfmaster[dfmaster['title'].isin([res[0]])]

#Get original name of parameter
def get_para(t):
    res = process.extractOne(t, params)
    return res[0]

#Check if its json or list of json
def json_list(x):
    try:
        a = ast.literal_eval(x)
        try:
            b = a['name']
            return b
        except TypeError:
            b = [c['name'] for c in a]
            c = ', '.join(b)
            return c
    except:         #its overview
        return x

def plotter(j):
    global x, i
    ax = x.plot(kind="bar", x="title", y=j)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig('graphs/graph' + str(i) + '.png')
    i = i + 1
    return None

def htmlgen(j):
    global x, hi
    x[[j, 'title']].to_html("results/file"+str(hi)+".html")
    hi = hi + 1
    return None

# -------------------------------------------------------
# Actions for intents
# -------------------------------------------------------

class ActionIMDB(Action):

    def name(self):
        return "action_imdb"

    def run(self, dispatcher, tracker, domain):
        print("imdb")
        title = tracker.get_slot('movie')
        if title:
            ex = get_movie_name(title)
            ans = ex['imdb_id'].tolist()[0]
            webbrowser.open('https://www.imdb.com/title/'+ans)
            dispatcher.utter_message("There you go.")
        else:
            dispatcher.utter_message("I didn't get you... please try again.")
        return [AllSlotsReset()]


class ActionGenQ(Action):

    def name(self):
        return "action_genq"

    def run(self, dispatcher, tracker, domain):
        print("action genq")
        try:
            para = tracker.get_slot('param')
            title = tracker.get_slot('movie')
            ex = get_movie_name(title)
            ext = ex[get_para(para)].tolist()[0]
            ans = json_list(ext)
            poster = ex['poster_path'].tolist()[0]
            dispatcher.utter_message("The "+para+" of "+title+" is "+str(ans))
            dispatcher.utter_message('http://image.tmdb.org/t/p/w342/'+poster)
        except:
            dispatcher.utter_message("Please try again!")
        return [AllSlotsReset()]


class ActionGenCalc(Action):

    def name(self):
        return "action_gencalc"

    def run(self, dispatcher, tracker, domain):
        global x
        print("actiongencalc")
        this = tracker.get_slot('this')
        opcalc = tracker.get_slot('opcalc')
        para = get_para(tracker.get_slot('pnum'))

        if this is None:
            x = dfmaster  # reload db

        try:
            if (opcalc == 'mean') or (opcalc == 'average'):
                ans = x[para].mean()
            elif opcalc == 'median':
                ans = x[para].median()
            elif opcalc == 'mode':
                ans = x[para].mode()
            else:
                ans = x[para].sum()
            dispatcher.utter_message("The " + str(opcalc) + " of "+ str(para) +" is " + str(ans))
        except:
            dispatcher.utter_message("I didn't get you... please try again.")

        return [AllSlotsReset()]


class ActionFilterNum(Action):

    def name(self):
        return "action_filternum"

    def run(self, dispatcher, tracker, domain):
        global x,i;
        print("filternum")
        this = tracker.get_slot('this')
        para = get_para(tracker.get_slot('pnum'))
        num = tracker.get_slot('num')
        up = tracker.get_slot('up')
        print('got slots')
        if this is None:
            x = dfmaster
        print('this is none')
        try:
            if up is not None:                                          # show most first
                x.sort_values(by=para, ascending=False, inplace=True)
            else:                                                       # least first
                x.sort_values(by=para, ascending=True, inplace=True)

            if num is not None:
                x = x.head(int(num))
            else:
                x = x.head()

            # Generate graph
            plotter(para)
            print('plotter done')

            # Generate table
            htmlgen(para)
            print('html done')
            
            dispatcher.utter_message("Check out the results window.")
            dispatcher.utter_message("graphs/graph"+str(i-1)+".png")

        except:
            dispatcher.utter_message("I didn't get you... please try again.")

        return [AllSlotsReset()]


class ActionFilterText(Action):

    def name(self):
        return "action_filtertext"

    def run(self, dispatcher, tracker, domain):
        global x, hi;
        print("filtertext")
        this = tracker.get_slot('this')  # for context
        val = tracker.get_slot('val')
        para = get_para(tracker.get_slot('ptext'))

        if this is None:
            x = dfmaster                 # reload db

        try:
            x = x[x[para].str.contains(val, case=False, na=False)]

            # Generate table
            htmlgen(para)

            dispatcher.utter_message("Check out the results!")
            dispatcher.utter_message("results/file"+str(hi-1)+".html")

        except:
            dispatcher.utter_message("Please try again...")

        return [AllSlotsReset()]


class ActionFilterComp(Action):

    def name(self):
        return "action_filtercomp"

    def run(self, dispatcher, tracker, domain):
        global x, hi;
        print("filtercomp")
        this = tracker.get_slot('this')
        opcomp = tracker.get_slot('opcomp')
        pnum = get_para(tracker.get_slot('pnum'))
        numall = tracker.get_slot('numall')

        if this is None:
            x = dfmaster  # reload db

        try:
            if opcomp == 'greater than':
                x = x[x[pnum] > int(numall)]
            elif opcomp == 'less than':
                x = x[x[pnum] < int(numall)]
            else:
                x = x[x[pnum] == int(numall)]

            # Generate table
            htmlgen(para)

            dispatcher.utter_message("See the filtered results.")
            dispatcher.utter_message("results/file" + str(hi - 1) + ".html")

        except:
            dispatcher.utter_message("Please try again.")

        return [AllSlotsReset()]


class ActionExport(Action):

    def name(self):
        return "action_export"

    def run(self, dispatcher, tracker, domain):

        global x
        try:
            op = tracker.get_slot('format')
            if op == 'excel':
                writer = pd.ExcelWriter('output/output.xlsx')
                dispatcher.utter_message('Exported to .xlsx format. Click on link to download.')                
                x.to_excel(writer,'Sheet1')
                writer.save()
                dispatcher.utter_message("output/output.xlsx")
            else:
                x.to_csv('output/output.csv')
                dispatcher.utter_message('Exported to .csv format. Click on link to download.')
                dispatcher.utter_message("output/output.csv")
        except:
            dispatcher.utter_message("Please try exporting again!")

        return [AllSlotsReset()]
