import os
import sys
import django
from datetime import datetime
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackshop.settings')
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
django.setup()

from hackshop.ip_ban import IPBanManager
from django.core.cache import cache

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def list_bans():
    print_header("IPs ACTUELLEMENT BANIES")
    
    bans_found = False
    
    print("Note: Le système utilise un cache en mémoire.")
    print("Pour voir les bans, implémentez un tracking list dans ip_ban.py")
    print("\nExemple :")
    print("  from hackshop.ip_ban import IPBanManager")
    print("  IPBanManager.ban_ip('192.168.1.100')")
    print("  is_banned, data = IPBanManager.is_ip_banned('192.168.1.100')")

def ban_ip(ip, reason="Ban manuel"):
    print_header(f"BANNIR L'IP: {ip}")
    
    ban_data = IPBanManager.ban_ip(ip, reason)
    
    print(f"IP bannie avec succès!")
    print(f"\nDétails du ban :")
    print(f"  IP: {ban_data['ip']}")
    print(f"  Raison: {ban_data['reason']}")
    print(f"  Timestamp: {ban_data['timestamp']}")
    print(f"  Expiration: {ban_data['expiry']}")

def unban_ip(ip):
    print_header(f"DÉBANNIR L'IP: {ip}")
    
    is_banned, ban_data = IPBanManager.is_ip_banned(ip)
    
    if is_banned:
        IPBanManager.unban_ip(ip)
        print(f"IP débanie avec succès!")
        print(f"\nPréalablement bani pour: {ban_data['reason']}")
    else:
        print(f"Cette IP n'est pas actuellement bannie.")

def check_ban(ip):
    print_header(f"VÉRIFIER LE STATUT DE L'IP: {ip}")
    
    is_banned, ban_data = IPBanManager.is_ip_banned(ip)
    
    if is_banned:
        print(f"STATUT: BANNIE")
        print(f"\nDétails :")
        print(f"  Raison: {ban_data['reason']}")
        print(f"  Ban à: {ban_data['timestamp']}")
        print(f"  Expiration: {ban_data['expiry']}")
    else:
        print(f"STATUT: NON BANNIE")

def clear_all_bans():
    print_header("SUPPRIMER TOUS LES BANS")
    
    response = input("Êtes-vous sûr? Cela supprimera TOUS les bans. (yes/no): ")
    
    if response.lower() == "yes":
        cache.clear()
        print("Tous les bans ont été supprimés!")
    else:
        print(" Annulé.")

def test_accounts():
    print_header("COMPTES DE TEST PROTÉGÉS")
    
    from hackshop.middlewares import TEST_ACCOUNTS
    
    print("Les comptes suivants sont protégés:")
    for i, account in enumerate(TEST_ACCOUNTS, 1):
        print(f"  {i}. {account}")
    print(f"\nTotal: {len(TEST_ACCOUNTS)} comptes")

def show_help():
    print_header("AIDE - GESTION DES BANS IP")
    
    print("Commandes disponibles:\n")
    print("  list               - Lister tous les bans actifs")
    print("  ban <ip> [reason]  - Bannir une IP")
    print("  unban <ip>         - Débannir une IP")
    print("  check <ip>         - Vérifier le statut d'une IP")
    print("  clear              - Supprimer tous les bans (ATTENTION!)")
    print("  accounts           - Voir les comptes de test protégés")
    print("  help               - Afficher cette aide")
    
    print("\nExemples:\n")
    print("  python manage_bans.py list")
    print("  python manage_bans.py ban 192.168.1.100")
    print("  python manage_bans.py check 192.168.1.100")
    print("  python manage_bans.py unban 192.168.1.100")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_bans()
    elif command == 'ban':
        if len(sys.argv) < 3:
            print("Erreur: Usage: python manage_bans.py ban <ip> [reason]")
            return
        ip = sys.argv[2]
        reason = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else "Ban manuel"
        ban_ip(ip, reason)
    elif command == 'unban':
        if len(sys.argv) < 3:
            print("Erreur: Usage: python manage_bans.py unban <ip>")
            return
        ip = sys.argv[2]
        unban_ip(ip)
    elif command == 'check':
        if len(sys.argv) < 3:
            print("Erreur: Usage: python manage_bans.py check <ip>")
            return
        ip = sys.argv[2]
        check_ban(ip)
    elif command == 'clear':
        clear_all_bans()
    elif command == 'accounts':
        test_accounts()
    elif command in ['help', '--help', '-h']:
        show_help()
    else:
        print(f"Erreur: Commande inconnue '{command}'")
        print("Tapez 'python manage_bans.py help' pour l'aide")

if __name__ == '__main__':
    main()
