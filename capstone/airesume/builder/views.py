from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Resume, Experience, Education, Skill
from .forms import ResumeForm, ExperienceForm, EducationForm, SkillForm
from .ai import generate_resume_bullets
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.template.loader import get_template
from xhtml2pdf import pisa

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log them in after registration
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'builder/register.html', {'form': form})

@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'builder/dashboard.html', {'resumes': resumes})

@login_required
def create_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            return redirect('resume_detail', resume_id=resume.id)
    else:
        form = ResumeForm()
    return render(request, 'builder/resume_form.html', {'form': form})

@login_required
def resume_detail(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Handle Additions
    if request.method == 'POST':
        if 'add_experience' in request.POST:
            exp_form = ExperienceForm(request.POST)
            if exp_form.is_valid():
                exp = exp_form.save(commit=False)
                exp.resume = resume
                exp.save()
        elif 'add_education' in request.POST:
            edu_form = EducationForm(request.POST)
            if edu_form.is_valid():
                edu = edu_form.save(commit=False)
                edu.resume = resume
                edu.save()
        elif 'add_skill' in request.POST:
            skill_form = SkillForm(request.POST)
            if skill_form.is_valid():
                skill = skill_form.save(commit=False)
                skill.resume = resume
                skill.save()

        # Handle Deletes
        elif 'delete_experience' in request.POST:
            Experience.objects.filter(id=request.POST.get('delete_experience'), resume=resume).delete()
        elif 'delete_education' in request.POST:
            Education.objects.filter(id=request.POST.get('delete_education'), resume=resume).delete()
        elif 'delete_skill' in request.POST:
            Skill.objects.filter(id=request.POST.get('delete_skill'), resume=resume).delete()

        return redirect('resume_detail', resume_id=resume.id)

    # Display
    experiences = Experience.objects.filter(resume=resume)
    education = Education.objects.filter(resume=resume)
    skills = Skill.objects.filter(resume=resume)

    return render(request, 'builder/resume_preview.html', {
        'resume': resume,
        'experiences': experiences,
        'education': education,
        'skills': skills,
        'exp_form': ExperienceForm(),
        'edu_form': EducationForm(),
        'skill_form': SkillForm(),
    })
    
@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == "POST":
        resume.delete()
        return redirect('dashboard')
    return HttpResponseForbidden()

@csrf_exempt
def ai_suggest_view(request):
    if request.method == "POST":
        prompt = request.POST.get("prompt", "")
        user_api_key = request.POST.get("api_key", "").strip()

        print("📨 Prompt received:", prompt)
        print("🔑 User-supplied API key:", "Yes" if user_api_key else "No")

        if prompt:
            result = generate_resume_bullets(prompt, user_api_key or None)
            return JsonResponse({"bullets": result})
        return JsonResponse({"error": "No prompt provided"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=405)

def download_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    experiences = Experience.objects.filter(resume=resume)
    education = Education.objects.filter(resume=resume)
    skills = Skill.objects.filter(resume=resume)

    template = get_template("builder/resume_pdf.html")
    html = template.render({
        "resume": resume,
        "experiences": experiences,
        "education": education,
        "skills": skills
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resume_{resume.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response