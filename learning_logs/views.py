from django.shortcuts import render
from .models import Topic,Entry
from django.http import HttpResponseRedirect,Http404
from django.urls import reverse
from .forms import TopicForm,EntryForm
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
	return render(request,'learning_logs/index.html')

@login_required
def topics(request):
	topics = Topic.objects.filter(owner=request.user).order_by('date_added')
	context = {'topics':topics}
	return render(request,'learning_logs/topics.html',context)

@login_required
def topic(request,topic_id):
	topic = Topic.objects.get(id=topic_id)
	if topic.owner != request.user:
		raise Http404
	entries = topic.entry_set.order_by('-date_added')      #按照date的降序排列#
	context = {'topic':topic,'entries':entries}
	return render(request,'learning_logs/topic.html',context)

@login_required
def new_topic(request):
	if request.method != 'POST':
		form = TopicForm()
	else:
		form = TopicForm(request.POST)
		if form.is_valid():
			new_topic = form.save(commit=False)
			new_topic.owner = request.user
			new_topic.save()
			return HttpResponseRedirect(reverse('learning_logs:topics'))	

	context = {'form':form}
	return render(request,'learning_logs/new_topic.html',context)

@login_required
def new_entry(request,topic_id):
	topic = Topic.objects.get(id=topic_id)
	if topic.owner != request.user:
		raise Http404
	if request.method != 'POST':
		form = EntryForm()
	else:
		form = EntryForm(data=request.POST)
		if form.is_valid():
			new_entry = form.save(commit=False)#创建了新的条目对象，存到了new_entry里 但没存到数据库#
			new_entry.topic = topic            #目的是为了把这个东西的topic给填写进去#
			new_entry.save()                   #现在才把包含topic的new_entry存储到数据库里去#

			return HttpResponseRedirect(reverse('learning_logs:topic',args=[topic_id]))	

	context = {'topic':topic,'form':form}
	return render(request,'learning_logs/new_entry.html',context)

@login_required
def edit_entry(request,entry_id):
	entry = Entry.objects.get(id=entry_id)
	topic = entry.topic
	if topic.owner != request.user:
		raise Http404
	if request.method != 'POST':
		form = EntryForm(instance=entry) #没修改的话，保持原来的entry不去动#
	else:
		form = EntryForm(instance=entry,data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('learning_logs:topic',args=[topic.id]))	

	context = {'entry':entry,'topic':topic,'form':form}
	return render(request,'learning_logs/edit_entry.html',context)	