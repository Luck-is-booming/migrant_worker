# blog/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import get_language
from django.core.mail import send_mail  
from .models import OrganizationInfo, ServiceCard, DestinationCountry, ResourcePublication, ContactMessage, TeamMember
from blog.models import Article 
from django.contrib.auth.models import User
from django.http import HttpResponse 

def create_admin_view(request):
    username = "admin"  
    password = "admin" 
    email = "kheshahang44668800@gmail.com" 
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        return HttpResponse(f"Admin '{username}' created successfully!")
    else:
        return HttpResponse("Admin already exists.")
    
def index_view(request):
    current_lang = get_language()
    
    # 1. Extract structural baseline information matrix
    db_info = OrganizationInfo.objects.first()
    if db_info:
        info = {
            "name": db_info.name_ne if current_lang == 'ne' else db_info.name_en,
            "slogan": db_info.slogan_ne if current_lang == 'ne' else db_info.slogan_en,
            "objective": db_info.objective_ne if current_lang == 'ne' else db_info.objective_en,
            "commitment": db_info.commitment_ne if current_lang == 'ne' else db_info.commitment_en,
            "chairperson": db_info.chairperson_name_ne if current_lang == 'ne' else db_info.chairperson_name_en,
            "message": db_info.chairperson_message_ne if current_lang == 'ne' else db_info.chairperson_message_en,
        }
    else:
        if current_lang == 'ne':
            info = {
                "name": "आप्रवासी कामदार हकहित संरक्षण केन्द्र, इलाम",
                "slogan": "सुरक्षित वैदेशिक रोजगार, समृद्ध परिवार र समृद्ध राष्ट्रको आधार।",
                "objective": "वैदेशिक रोजगारीलाई सुरक्षित, भरपर्दो, मर्यादित र उपलब्धिमूलक बनाउने।",
                "commitment": "वैदेशिक रोजगारीबाट फर्किएका श्रमिकको सीप, पूँजी, प्रविधि र अनुभवको राष्ट्र निर्माणमा उच्चतम सार्थक उपयोग गर्ने।",
                "chairperson": "राम बहादुर गुरुङ",
                "message": "वैदेशिक रोजगारीमा जाने प्रत्येक नेपाली नागरिकको अधिकार र सुरक्षा सुनिश्चित गर्नु हाम्रो परम कर्तव्य हो। इलाम जिल्ला र आसपासका क्षेत्रमा सचेतना फैलाउन हामी निरन्तर प्रतिबद्ध छौं।"
            }
        else:
            info = {
                "name": "Migrant Workers Rights and Welfare Protection Center, Ilam",
                "slogan": "Safe Foreign Employment: The Foundation of a Prosperous Family and a Prosperous Nation.",
                "objective": "To make foreign employment safe, reliable, dignified, and productive.",
                "commitment": "To achieve the highest meaningful utilization of the skills, capital, technology, and experience of returnee migrant workers in nation-building.",
                "chairperson": "Ram Bahadur Gurung",
                "message": "Ensuring the safety, dignity, and legal rights of every migrant worker is our utmost duty. We continuously strive to build a transparent ecosystem from the grass-roots level upward."
            }

    # 2. Extract Operational Service Items
    services_qs = ServiceCard.objects.all()
    services = []
    for s in services_qs:
        services.append({
            "title": s.title_ne if current_lang == 'ne' else s.title_en,
            "desc": s.desc_ne if current_lang == 'ne' else s.desc_en,
            "process": s.process_ne if current_lang == 'ne' else s.process_en,
            "icon": s.icon_svg
        })
        
    if not services:
        if current_lang == 'ne':
            services = [
                {
                    "title": "पूर्व-प्रस्थान परामर्श",
                    "desc": "श्रम सम्झौता, भिसा, बीमा र गन्तव्य देशको कानुनबारे विस्तृत जानकारी र अभिमुखीकरण परामर्श।",
                    "process": "केन्द्रको कार्यालयमा सक्कल राहदानी र श्रम इजाजत पत्र सहित सम्पर्क राख्ने।",
                    "icon": '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'
                },
                {
                    "title": "कानुनी सहायता र उद्धार",
                    "desc": "अलपत्र परेका, ठगीमा परेका वा बन्धक बनाइएका श्रमिकहरूको कानुनी उपचार र द्रुत सरकारी उद्धार समन्वय।",
                    "process": "केन्द्रको आकस्मिक हेल्पलाईन नम्बर वा प्रमाण सहित अनलाइन फारम भर्ने।",
                    "icon": '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"></path></svg>'
                }
            ]
        else:
            services = [
                {
                    "title": "Pre-Departure Counselling",
                    "desc": "Comprehensive verification checks regarding employment contracts, medical benefits, insurance limits, and legal documentation.",
                    "process": "Visit our main physical helpdesk in Ilam with your valid passport draft copy.",
                    "icon": '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'
                },
                {
                    "title": "Legal Aid & Emergency Rescue",
                    "desc": "Active cross-border coordination with local embassies, safe houses, and ministries to track down wage theft and coordinate rescue operations.",
                    "process": "Submit official contractual deployment complaints directly via our secure portals.",
                    "icon": '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"></path></svg>'
                }
            ]

    # 3. Extract Destination Countries Metrics
    countries_qs = DestinationCountry.objects.all().order_by('name_en')
    countries = []
    for c in countries_qs:
        countries.append({
            "name": c.name_ne if current_lang == 'ne' else c.name_en,
            "currency": c.currency_ne if current_lang == 'ne' else c.currency_en,
            "capital": c.capital_ne if current_lang == 'ne' else c.capital_en,
            "cost": c.estimated_cost,
            "time": c.avg_processing_days,
            "flag": c.flag_emoji
        })

    if not countries:
        if current_lang == 'ne':
            countries = [
                {"name": "मलेसिया", "currency": "मलेसियन रिंगिट (MYR)", "capital": "क्वालालम्पुर", "cost": 35000, "time": 45, "flag": "🇲🇾"},
                {"name": "कतार", "currency": "कतारी रियाल (QAR)", "capital": "दोहा", "cost": 25000, "time": 30, "flag": "🇶🇦"}
            ]
        else:
            countries = [
                {"name": "Malaysia", "currency": "Malaysian Ringgit (MYR)", "capital": "Kuala Lumpur", "cost": 35000, "time": 45, "flag": "🇲🇾"},
                {"name": "Qatar", "currency": "Qatari Riyal (QAR)", "capital": "Doha", "cost": 25000, "time": 30, "flag": "🇶🇦"}
            ]

    # 4. Extract Legal Resources and Publication Artifacts 
    resources_qs = ResourcePublication.objects.all().order_by('-id')
    resources = []
    for r in resources_qs:
        resources.append({
            "title": r.title_ne if current_lang == 'ne' else r.title_en,
            "category": "निर्देशिका र पुस्तिकाहरू" if current_lang == 'ne' else "Guides & Manuals",
            "file_url": r.download_url if r.download_url else "#",
            "size": r.file_size if r.file_size else "1.2 MB"
        })

    if not resources:
        if current_lang == 'ne':
            resources = [
                {"title": "सुरक्षित वैदेशिक रोजगार हातेपुस्तिका २०२६", "category": "निर्देशिका र पुस्तिकाहरू", "file_url": "#", "size": "2.4 MB"},
                {"title": "म्यानपावर एजेन्सी ठगी नियन्त्रण निर्देशिका", "category": "कानुनी दस्तावेज", "file_url": "#", "size": "1.1 MB"}
            ]
        else:
            resources = [
                {"title": "Safe Foreign Employment Handbook 2026", "category": "Guides & Manuals", "file_url": "#", "size": "2.4 MB"},
                {"title": "Manpower Agency Fraud Prevention Guide", "category": "Legal Resources", "file_url": "#", "size": "1.1 MB"}
            ]

    # 5. Extract Operational Team Members
    team_qs = TeamMember.objects.filter(is_active=True).order_by('sort_order')
    team_members = []
    for member in team_qs:
        team_members.append({
            "name": member.name_ne if (hasattr(member, 'name_ne') and current_lang == 'ne') else member.name,
            "designation": member.designation_ne if (hasattr(member, 'designation_ne') and current_lang == 'ne') else member.designation,
            "email": member.email,
            "phone": member.phone,
            "image": member.image if member.image else None
        })

    if not team_members:
        if current_lang == 'ne':
            team_members = [
                {"name": "सीता राजबंशी", "designation": "वरिष्ठ कानुनी अधिकारी", "email": "sita.legal@mrcilam.org", "phone": "+९७७-२७-५२०१११", "image": None},
                {"name": "रमेश श्रेष्ठ", "designation": "मनोसामाजिक परामर्शदाता", "email": "ramesh.counselor@mrcilam.org", "phone": "+९७७-२७-५२०२२२", "image": None}
            ]
        else:
            team_members = [
                {"name": "Sita Rajbanshi", "designation": "Senior Legal Protection Officer", "email": "sita.legal@mrcilam.org", "phone": "+977-27-520111", "image": None},
                {"name": "Ramesh Shrestha", "designation": "Lead Psychosocial Counselor", "email": "ramesh.counselor@mrcilam.org", "phone": "+977-27-520222", "image": None}
            ]

    # 6. Fetch real Articles
    latest_articles = Article.objects.all().order_by('-is_alert', '-published_date')[:3]

    # 🚨 FIXED: Fallback uses cloud URLs instead of static file directory arrays
    if not latest_articles:
        if current_lang == 'ne':
            latest_articles = [
                {
                    "title": "मलेसिया जाने कामदारहरूको लागि नयाँ स्वास्थ्य मापदण्ड",
                    "content": "मलेसिया सरकारले आगामी महिनादेखि लागू हुने गरी स्वास्थ्य परीक्षण मापदण्डमा परिमार्जन गरेको छ। सम्पूर्ण म्यानपावर र अभिमुखीकरण संस्थाहरूले नयाँ स्वास्थ्य निर्देशिका पालना गर्नुहुन सूचित गरिन्छ।",
                    "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop",
                    "formatted_date": "२०८३ जेठ २७ गते",
                    "is_alert": True
                }
            ]
        else:
            latest_articles = [
                {
                    "title": "New Medical Examination Standards for Malaysia Bound Workers",
                    "content": "The government of Malaysia has announced updated diagnostic compliance criteria effective next month. Ensure all panel clinics verify candidate records accordingly.",
                    "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop",
                    "formatted_date": "June 10, 2026",
                    "is_alert": True
                }
            ]

    # 7. Post Routing
    if request.method == "POST":
        msg_instance = ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        
        email_subject = f"🚨 New Portal Influx: {msg_instance.subject}"
        email_body = (
            f"An official support request packet has been filed.\n\n"
            f"Sender Identity: {msg_instance.name}\n"
            f"Communication Handle: {msg_instance.email}\n\n"
            f"Detailed Content Parameter Block:\n"
            f"{msg_instance.message}"
        )
        
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email=None, 
            recipient_list=['kheshahang44668800@gmail.com'], 
            fail_silently=False,
        )

        msg = "तपाईंको सन्देश दर्ता भयो। हामी छिट्टै सम्पर्क गर्नेछौं।" if current_lang == 'ne' else "Your inquiry message has been securely submitted. Our officers will contact you shortly."
        messages.success(request, msg)
        return redirect('index')

    context = {
        'info': info,
        'services': services,
        'countries': countries,
        'resources': resources,
        'team_members': team_members, 
        'latest_articles': latest_articles,  
        'current_year': 2026
    }
    return render(request, 'core/index.html', context)