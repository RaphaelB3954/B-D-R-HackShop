from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import sqlite3, os
from pathlib import Path
from dotenv import load_dotenv
from hackshop.ip_ban import IPBanManager

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv('API_KEY')
ALICE_PASS = os.getenv('ALICE_PASS')
BOB_PASS = os.getenv('BOB_PASS')
SECRET_PASS = os.getenv('SECRET_PASS')
FLAG = os.getenv('FLAG')
CREDIT_CARD = os.getenv('CREDIT_CARD')

ADMIN_USER = settings.ADMIN_USER
ADMIN_PASS = settings.ADMIN_PASS

def zz(r):
    c=connection.cursor()
    try:
        c.execute("CREATE TABLE IF NOT EXISTS tbl_usr (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS tbl_msg (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS tbl_sec (id INTEGER PRIMARY KEY AUTOINCREMENT, info TEXT)")
        
        c.execute("DELETE FROM tbl_usr WHERE id IN (1,2,3)")
        
        admin_hash = make_password(ADMIN_PASS)
        alice_hash = make_password(ALICE_PASS)
        bob_hash = make_password(BOB_PASS)
        
        c.execute("INSERT INTO tbl_usr VALUES (1,%s,%s,'admin')", (ADMIN_USER, admin_hash))
        c.execute("INSERT INTO tbl_usr VALUES (2,'alice',%s,'user')", (alice_hash,))
        c.execute("INSERT INTO tbl_usr VALUES (3,'bob',%s,'user')", (bob_hash,))
        
        c.execute("DELETE FROM tbl_sec WHERE id IN (1,2)")
        c.execute("INSERT INTO tbl_sec VALUES (1,'FLAG{sql_injection_master}')")
        c.execute("INSERT INTO tbl_sec VALUES (2,'Carte: 4111-1111-1111-1111')")
        connection.connection.commit()
    except Exception as ex:
        print(f"Erreur zz: {ex}")

def index(request):
    zz(request)
    return render(request, 'index.html', {'u': request.session.get('u')})

def login_view(request):
    zz(request)
    e=None
    if request.method == 'POST':
        a=request.POST.get('username',''); b=request.POST.get('password','')
        try:
            c=connection.cursor()
            c.execute("SELECT * FROM tbl_usr WHERE username=%s", (a,))
            row=c.fetchone()
            
            if row and check_password(b, row[2]):
                request.session['u']=row[1]; request.session['r']=row[3]
                return redirect('/dashboard/')
            else:
                e='Mauvais identifiants'
        except Exception as ex:
            e=str(ex)
    return render(request,'login.html',{'e':e,'u':None})

def logout_view(request):
    request.session.flush()
    return redirect('/')

def dashboard(request):
    if not request.session.get('u'): return redirect('/login/')
    return render(request,'dashboard.html',{'u':request.session.get('u'),'r':request.session.get('r')})

def forum(request):
    zz(request)
    if request.method=='POST' and request.session.get('u'):
        m=request.POST.get('message','')
        if len(m) > 500 or len(m) == 0:
            return HttpResponse("Message invalide", status=400)
        c=connection.cursor(); c.execute("INSERT INTO tbl_msg (username,content) VALUES (%s,%s)",(request.session['u'],m)); connection.connection.commit()
    c=connection.cursor(); c.execute("SELECT * FROM tbl_msg ORDER BY id DESC"); msgs=c.fetchall()
    return render(request,'forum.html',{'msgs':msgs,'u':request.session.get('u')})

def admin_panel(request):
    if not request.session.get('u') or request.session.get('r') != 'admin':
        return redirect('/login/')
    
    c = connection.cursor()
    c.execute("SELECT * FROM tbl_usr")
    usrs = c.fetchall()

    env_passwords = {
        ADMIN_USER: ADMIN_PASS,
        "alice": ALICE_PASS,
        "bob": BOB_PASS,
    }

    usrs_display = []
    for u in usrs:
        user_id, username, _hashed_password, role = u
        clear_password = env_passwords.get(username, "(inconnu)")
        usrs_display.append((user_id, username, clear_password, role))

    c.execute("SELECT * FROM tbl_sec")
    secs = c.fetchall()

    return render(
        request,
        "admin.html",
        {"usrs": usrs_display, "secs": secs, "u": request.session.get("u"), "flag": FLAG, "card": CREDIT_CARD},
    )

@login_required
def backup(request):
    return HttpResponse(f"{ADMIN_USER}:{ADMIN_PASS}\nalice:{ALICE_PASS}\nbob:{BOB_PASS}\napi_key:{API_KEY}\nsecret:{SECRET_PASS}", content_type='text/plain')

def shop(request):
    """Page boutique"""
    zz(request)
    return render(request, 'shop.html', {'u': request.session.get('u')})

def manage_bans(request):
    """Panneau de gestion des bans IP (admin uniquement)"""
    if not request.session.get('u') or request.session.get('r') != 'admin':
        return redirect('/login/')
    
    from django.core.cache import cache
    bans_list = []
    
    
    if request.method == 'POST':
        ip_to_unban = request.POST.get('unban_ip', '')
        if ip_to_unban:
            IPBanManager.unban_ip(ip_to_unban)
            return redirect('/manage_bans/')
    
    return render(request, 'manage_bans.html', {
        'u': request.session.get('u'),
        'bans': bans_list,
    })

def admin_clear_forum(request):
    """Vide complètement le forum (admin uniquement)"""
    if not request.session.get('u') or request.session.get('r') != 'admin':
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            c = connection.cursor()
            c.execute("DELETE FROM tbl_msg")
            connection.connection.commit()
        except Exception as ex:
            print(f"Erreur lors du clear du forum: {ex}")
    
    return redirect('/admin-panel/')

def get_client_ip(request):
    """Extrait l'IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
