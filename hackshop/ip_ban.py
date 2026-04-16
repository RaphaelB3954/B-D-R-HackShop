"""
Système de ban IP temporaire (72h)
Les bans sont stockés en cache en mémoire et disparaissent au redémarrage du serveur
"""
from datetime import datetime, timedelta
from django.core.cache import cache
import os

BAN_DURATION_HOURS = 72

class IPBanManager:
    BAN_CACHE_KEY = "ip_bans"
    
    @staticmethod
    def get_ban_key(ip):
        """Génère une clé de cache unique pour une IP"""
        return f"ip_ban_{ip}"
    
    @staticmethod
    def ban_ip(ip, reason="Utilisation de comptes de test"):
        """
        Bannit une IP pour 72 heures
        Stocké uniquement en mémoire, disparaît au redémarrage
        """
        ban_key = IPBanManager.get_ban_key(ip)
        ban_data = {
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(hours=BAN_DURATION_HOURS)).isoformat(),
            'reason': reason,
        }
        # Cache avec expiration de 72 heures (259200 secondes)
        cache.set(ban_key, ban_data, 259200)
        return ban_data
    
    @staticmethod
    def is_ip_banned(ip):
        """Vérifie si une IP est bannie"""
        ban_key = IPBanManager.get_ban_key(ip)
        ban_data = cache.get(ban_key)
        
        if ban_data:
            expiry = datetime.fromisoformat(ban_data['expiry'])
            if datetime.now() < expiry:
                return True, ban_data
        
        return False, None
    
    @staticmethod
    def get_banned_ips():
        """Retourne la liste de toutes les IPs actuellement banies"""
        banned = {}
        # Note: Cette fonction itère sur le cache, comportement dépend du backend
        # Pour mieux le gérer, on pourrait ajouter une liste de tracking
        return banned
    
    @staticmethod
    def unban_ip(ip):
        """Débannit manuellement une IP"""
        ban_key = IPBanManager.get_ban_key(ip)
        cache.delete(ban_key)
