from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import jieba
import sqlite3
import time
import math
from operator import itemgetter
# Create your views here.

def addlink(nowtext):
	jieba.load_userdict('word.txt')
	ret=""
	wordlist=jieba.lcut(nowtext)
	conn = sqlite3.connect("wordurl.db")
	cursor = conn.cursor()
	for i in wordlist:
		sql="select * from links where word = ? "
		cursor.execute(sql,(i,))
		values = cursor.fetchall()
		if (values):
			ret=ret+'<a href="/app/team'+values[0][1]+'"  target="_blank">'+i+'</a>'
		else:
			ret=ret+i
	return ret
	
	
def textred(text,wordlist):
	newtext = text
	minpos = 10000
	for word in wordlist:
		tmp = newtext.find(word)
		if tmp != -1:
			if tmp < minpos:
				minpos = tmp
	if minpos > 20:
		newtext = "..."+newtext[minpos-20:minpos+30]+"..."
	else:
		newtext = newtext[0:50]+"..."
	for word in wordlist:
		if newtext.find(word) != -1:
			newtext = newtext.replace(word, '<font color="#FF3300">'+word+'</font>')
	return newtext

def titlered(title,wordlist):
	newtext = title
	for word in wordlist:
		if newtext.find(word) != -1:
			newtext = newtext.replace(word, '<font color="#FF3300">'+word+'</font>')
	return newtext
	
def index(request):
	return render(request, 'board.html')
	
def getnews(request,net):
	print(net)
	conn = sqlite3.connect("news.db")
	cursor = conn.cursor()
	sql = "select * from news where url = ? "
	cursor.execute(sql,(net,))
	values = cursor.fetchall()
	nowpage=values[0]
	addlinktext=addlink(nowpage[4])
	return render(request,'news1.html',{'title':nowpage[1], 'fromwhere':nowpage[2], 'time': nowpage[3],'text':addlinktext})
	
def getteam(request,net):
	print(net)
	#getmessage
	conn_message = sqlite3.connect("teammessage.db")
	cursor_message = conn_message.cursor()
	sql_message="select * from team where url = ? "
	cursor_message.execute(sql_message,(net,))
	values_message= cursor_message.fetchall()
	nowtitle=values_message[0][1]
	messagelist=[]
	for nowmessage in values_message:
		messagelist.append({'message' : nowmessage[2]})
	#endgetmessage
	#getplayer
	conn_player = sqlite3.connect("teamplayer.db")
	cursor_player = conn_player.cursor()
	sql_player="select * from team where url = ? "
	cursor_player.execute(sql_player,(net,))
	values_player= cursor_player.fetchall()
	playerlist=[]
	for nowplayer in values_player:
		playerlist.append({'player' : nowplayer[2]})
	#endgetplayer
	#getnews
	conn_news=sqlite3.connect("teamidtitle.db")
	cursor_news = conn_news.cursor()
	sql_news="select * from tnt where urlteam = ? "
	cursor_news.execute(sql_news,(net,))
	values_news=cursor_news.fetchall()
	newslist=[]
	for news in values_news:
		newslist.append({'link':news[1],'title':news[2]})
	paginator=Paginator(newslist,10)
	page=request.GET.get('page')
	try:
		customer=paginator.page(page)
	except PageNotAnInteger:
		customer=paginator.page(1)
	except EmptyPage:
		customer=paginator.page(paginator.num_pages)
	#endgetnes
	return render(request,'team.html',{'title': nowtitle,'messagelist': messagelist,'playerlist' : playerlist,'newslist':customer})

def findindex(request):
	return render(request,'find.html')
	
def search(request):
	text = request.GET['text']
	text=str(text)
	print("search:",text)
	if (text):
		return HttpResponseRedirect(reverse('app:result',args=(text,)))
	else:
		return HttpResponseRedirect(reverse('app:findindex'))
		
def result(request,text):
	print("result:",text)
	words=text.split(' ')
	print(words)
	wordlist=[]
	jieba.load_userdict('word.txt')
	for everyword in words:
		wordlist.extend(jieba.lcut(everyword))
	#pre list
	cntlist=[]
	wordsum=[]
	conn_sum=sqlite3.connect("sum.db")
	cursor_sum = conn_sum.cursor()
	sql_sum="select * from sum"
	cursor_sum.execute(sql_sum)
	values_sum=cursor_sum.fetchall()
	nownumber=0
	for each_row in values_sum:
		nowurl=each_row[0]
		wordsum.append(each_row[1])
		cntlist.append({'url':nowurl,'sum':0.0,'num':nownumber})
		nownumber+=1
	#
	conn_dictionary=sqlite3.connect("dictionary.db")
	cursor_dictionary = conn_dictionary.cursor()
	#
	#start time
	start_time=time.time()
	#
	for word in wordlist:
		print(word)
		addlist=[]
		sql_dictionary="select * from dictionary where word = ?"
		cursor_dictionary.execute(sql_dictionary,(word,))
		values_dictionary=cursor_dictionary.fetchall()
		if (len(values_dictionary)==0):
			continue
		for each_row in values_dictionary:
			addlist.append(each_row[2])
		setlist=set(addlist)
		vlog=math.log(1.0 * len(cntlist) / len(setlist))
		for each_row in addlist:
			cntlist[each_row]['sum']+=1.0 * vlog * (1.0 / wordsum[each_row])
	#end time
	end_time=time.time()
	print("time=",end_time-start_time)
	#sort
	cntlist_by_sum = sorted(cntlist, key=itemgetter('sum'),reverse=True)
	#get dicts
	newslist=[]
	uselesslist=[]
	conn_news = sqlite3.connect("news.db")
	cursor_news = conn_news.cursor()
	for article in cntlist_by_sum:
		if (article['sum']<0.00001) :
			break
		uselesslist.append(0)
	paginator = Paginator(uselesslist, 20)
	page=request.GET.get('page')
	tmppage=page
	try:
		customer = paginator.page(page)
		tmppage=page
	except PageNotAnInteger:
		customer = paginator.page(1)
		tmppage=1
	except EmptyPage:
		customer = paginator.page(paginator.num_pages)		
		tmppage=paginator.num_pages
	tmppage=int(tmppage)
	tmpfrom=(tmppage-1) * 20
	tmpto=tmppage * 20
	tmpto=min(tmpto,len(uselesslist))
	for i in range(tmpfrom,tmpto):
		article=cntlist_by_sum[i]
		sql_news = "select * from news where url = ? "
		cursor_news.execute(sql_news,(article['url'],))
		values_news = cursor_news.fetchall()
		nowpage=values_news[0]
		nowtitle=nowpage[1]
		nowtext=nowpage[4]
		nowtitle=titlered(nowtitle,wordlist)
		nowtext=textred(nowtext,wordlist)
		newslist.append({'url':article['url'],'title':nowtitle,'text':nowtext})
	#
	return render(request,'result.html',{'text':text,'num':len(uselesslist),'time':end_time-start_time,'uselesslist':customer,'newslist':newslist})
	