"""
WSGI config for TBZBlogs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TBZBlogs.settings')

application = get_wsgi_application()
'''
Project Overview: You are tasked with building a Blog Application using Django and PostgreSQL. This project involves creating a platform where users can:
View blog posts (listing and detailed view).
Register, log in, and manage their accounts.
Create, edit, and delete their posts.
Like, dislike and comment on blog posts. 
Also write test cases for everything.
Tools Required:
Python
Django
PostgreSQL
Basic knowledge of HTML, CSS, Pytest and bootstrap.

now see above is the basic project overview which i am required to create. now also see in the current directory that i have already done
all the required starting setup for our project. now i have learned the django from Chai or Code (youtube channel) and it's documentation links are as below so i hope you will inspect those and see how exactly that person is writing the code and all in easy modular way.
https://docs.chaicode.com/youtube/chai-aur-django/getting-started/
https://docs.chaicode.com/youtube/chai-aur-django/jinja-templates/
https://docs.chaicode.com/youtube/chai-aur-django/bbotstrap+tailwind/
https://docs.chaicode.com/youtube/chai-aur-django/models/
https://docs.chaicode.com/youtube/chai-aur-django/relationships-and-forms/

now see below are the main ideas that I need to implement other than this normal blog application which is mainly doing only CRUD.
1. To generate the blog from raw idea or language from AI.
2. An option for enhancing blog content after writing to any way like funny, professional, etc. which will be again done from AI.
3. Option to translate whole blog in any language at both time: while writing the blog or while reading the published blog.
4. Some way to suggest the these/images/video in the blog based on the written blog content as user need to add some image atleast in all written blog for making it look proper in list or our web application so suggestion based on free and opensourse images/videos or stickers (so anything is fine but it just need to be there something there visually instead of plain text only).
5. Then a complete dashboard for admin who can control everything (as django is providing already so if we use that, same will work for us now.)
6. Complete dashboard for all users to see his/her all blogs complete performance details like likes, dislikes, and most importantly comments analysis. 
7. In the complete comment analysis dashboard, each user should be able to see (i. whole visual chart of sentiment wise comments like position, negative, neutral) then (ii. option for getting most important and action taking comments (like a post have many comments like of appreation, improvements, reasons for something so from all of these, the comments with content of improvements or detailed feedbacks are important compared to all other ones so all user should get option for that filter for each of his/her blogs seperately so that user can get perfomance and all analysis for each posts seperately.))

now along while implementing these all stuff, make sure to follow official PEP8 documentation for writing code along with complete guideline for writing codes that i am attaching below and please don't be too much lengthy or long in writing comments and add it properly as per necessary requirements only.
please also tell me to run necessary commands or ask to run like of creating new templates or apps in for this project (like python manage.py startapp xyz) so that we can keep complete flow and everything in proper Django way. 
also one another important thing is to make to add the specific link or simple info from where each code block or all functions are referenced as my supervisor is strict and he will ask for each source from where i have took reference and wrote or pasted the code so please also take care for that.
and also use the best and kind of dark theme UI by getting everything from bootstrap only so that it becomes easy for us to make very beautiful and impressive UI and also tell my supervisor that these all are directly taken from bootstrap and I haven't used AI to wrote all those stuff.
'''