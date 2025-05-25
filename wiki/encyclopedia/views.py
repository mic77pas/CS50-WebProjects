from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import util
import markdown2
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/not_found.html", {"title": title})
    html = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html
    })

def search(request):
    query = request.GET.get("q", "").strip()
    entries = util.list_entries()
    if query in entries:
        return redirect("entry", title=query)

    matches = [entry for entry in entries if query.lower() in entry.lower()]
    return render(request, "encyclopedia/search_results.html", {
        "query": query,
        "results": matches
    })
    
def create(request):
    if request.method == "POST":
        title = request.POST.get("title").strip()
        content = request.POST.get("content")
        if util.get_entry(title):
            return render(request, "encyclopedia/create.html", {
                "error": "An entry with this title already exists.",
                "title": title,
                "content": content
            })
        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/create.html")

def edit(request, title):
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect("entry", title=title)

    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/not_found.html", {"title": title})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })
    
    
def random_page(request):
    entries = util.list_entries()
    title = random.choice(entries)
    return redirect("entry", title=title)