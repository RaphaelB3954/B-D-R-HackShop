"""
Middleware pour gestion des bans IP et détection des accès avec comptes de test
Only bans if BOTH account AND password are correct (ceux affichés dans login.html)
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.hashers import check_password
from hackshop.ip_ban import IPBanManager
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TEST_ACCOUNTS = ['admin', 'alice', 'bob']

TEST_ACCOUNTS_PASSWORDS = {
    'admin': 'admin',
    'alice': '1234',
    'bob': 'password',
}

def get_client_ip(request):
    """Extrait l'IP réelle du client (supporte les proxies)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class IPBanMiddleware:
    """Vérifie si l'IP est bannie avant de traiter la requête"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        client_ip = get_client_ip(request)
        is_banned, ban_data = IPBanManager.is_ip_banned(client_ip)
        
        if is_banned:
            return render(request, 'ban.html', {
                'ban_reason': ban_data['reason'],
                'ban_expiry': ban_data['expiry'],
            })
        
        response = self.get_response(request)
        return response

class TestAccountBanMiddleware:
    """
    Bannit une IP si une tentative de connexion aux comptes de test 
    avec le BON mot de passe est détectée (ceux de login.html).
    Sans le bon mot de passe = pas de ban
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.method == 'POST' and '/login/' in request.path:
            username = request.POST.get('username', '').lower()
            password = request.POST.get('password', '')
            
            if username in TEST_ACCOUNTS:
                if password == TEST_ACCOUNTS_PASSWORDS.get(username):
                    client_ip = get_client_ip(request)
                    
                    IPBanManager.ban_ip(
                        client_ip, 
                        reason=f"Accès réussi avec compte de test '{username}' (credentials valides)"
                    )
                    
                    # Afficher l'écran de ban
                    return render(request, 'ban.html', {
                        'ban_reason': f"Vous avez utilisé un compte de test ({username}) avec les bonnes identifiants !",
                        'ban_expiry': 'Dans 72 heures',
                    })
        
        response = self.get_response(request)
        return response
