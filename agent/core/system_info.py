import platform
import subprocess
import getpass
import re

def get_domain_name():
    """Récupère le nom de domaine de la machine (Windows)."""
    try:
        output = subprocess.check_output('SYSTEMINFO | findstr /B /C:"Domain"', shell=True, text=True, stderr=subprocess.DEVNULL, encoding='utf-8', errors='ignore')
        domain = output.split(":")[1].strip()
        if domain.lower() == 'workgroup':
            return None # C'est un workgroup, pas un domaine
        return domain
    except subprocess.CalledProcessError:
        # La commande peut échouer si la machine n'est pas jointe à un domaine ou pour d'autres raisons
        return None
    except IndexError:
        return None

def get_local_users():
    """Liste les utilisateurs locaux (Windows)."""
    users = []
    try:
        output = subprocess.check_output("net user", shell=True, text=True, universal_newlines=True, stderr=subprocess.DEVNULL, encoding='utf-8', errors='ignore')
        # La sortie de 'net user' est un peu complexe à parser directement
        # Elle liste les utilisateurs dans des colonnes. On va chercher les noms.
        # On ignore les lignes vides, les lignes de titre/séparateur
        user_lines = [line.strip() for line in output.splitlines() if line.strip() and not line.startswith("---") and not "command completed successfully" in line.lower()]
        
        # Supprimer l'entête et le pied de page
        if len(user_lines) > 2: # Devrait y avoir au moins une ligne de titre et "The command completed successfully."
             # L'entête peut varier en fonction de la langue du système.
             # On va essayer de trouver la ligne qui contient "User accounts for" ou similaire
            header_end_index = 0
            for i, line in enumerate(user_lines):
                if "User accounts for" in line or "Utilisateurs pour" in line or "Konten für" in line: # Ajouter d'autres langues si nécessaire
                    header_end_index = i + 1
                    break
            
            # La ligne "The command completed successfully" est généralement la dernière
            # Nous avons déjà filtré cela plus haut.
            
            actual_user_lines = user_lines[header_end_index:]

            for line in actual_user_lines:
                # Les utilisateurs peuvent être listés sur plusieurs colonnes
                # On split par espace et on prend tous les mots non vides
                parts = [part for part in line.split('  ') if part.strip()] # Split par plusieurs espaces
                users.extend(p for p in parts if p and p != "-------------------------------------------------------------------------------")


        # Filtrer quelques noms par défaut qui ne sont généralement pas des utilisateurs réels pertinents
        default_accounts = ["Administrator", "Guest", "DefaultAccount", "WDAGUtilityAccount"]
        users = [u for u in users if u not in default_accounts and not u.startswith("IUSR_") and not u.startswith("IWAM_")]
        
        return list(set(users)) # Retourne une liste unique
    except subprocess.CalledProcessError:
        return [] # Retourne une liste vide en cas d'erreur

def get_local_admins():
    """Liste les membres du groupe Administrateurs local (Windows)."""
    admins = []
    try:
        # Tenter de récupérer le nom localisé du groupe "Administrators"
        command_get_admin_group_name = '(Get-LocalGroup -SID "S-1-5-32-544").Name'
        admin_group_name = "Administrators" # Valeur par défaut
        try:
            ps_output = subprocess.check_output(["powershell", "-Command", command_get_admin_group_name], text=True, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='ignore')
            admin_group_name = ps_output.strip()
        except Exception:
            pass # Utiliser la valeur par défaut si la commande PowerShell échoue

        output = subprocess.check_output(f'net localgroup "{admin_group_name}"', shell=True, text=True, universal_newlines=True, stderr=subprocess.DEVNULL, encoding='utf-8', errors='ignore')
        lines = output.splitlines()
        member_section = False
        for line in lines:
            if "Members" in line or "Membres" in line: # Gérer la localisation
                member_section = True
                continue
            if "-------------------------------------------------------------------------------" in line:
                if member_section: # On a fini la section des membres
                    break 
                else: # On est sur la ligne de séparation avant les membres
                    continue
            if member_section and line.strip():
                admins.append(line.strip())
        return admins
    except subprocess.CalledProcessError:
        return []

def get_current_user_privileges():
    """Vérifie si l'utilisateur actuel est administrateur (Windows)."""
    try:
        # whoami /groups affiche les groupes de l'utilisateur courant
        # On cherche le SID S-1-16-12288 qui correspond à "High Mandatory Level" (Admin)
        # ou le nom du groupe "BUILTIN\Administrators" ou son équivalent localisé
        output = subprocess.check_output("whoami /groups", shell=True, text=True, universal_newlines=True, stderr=subprocess.DEVNULL, encoding='utf-8', errors='ignore')
        if "S-1-16-12288" in output or "High Mandatory Level" in output:
            return "Admin"
        
        # Essayer de trouver le groupe Administrateurs par son nom aussi (plus robuste aux langues)
        command_get_admin_group_sid = '(New-Object System.Security.Principal.SecurityIdentifier("S-1-5-32-544")).Translate([System.Security.Principal.NTAccount]).Value'
        admin_group_name = "BUILTIN\\Administrators" # Valeur par défaut
        try:
            ps_output = subprocess.check_output(["powershell", "-Command", command_get_admin_group_sid], text=True, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='ignore')
            admin_group_name_localized = ps_output.strip()
            if admin_group_name_localized in output:
                 return "Admin"
        except Exception:
            if admin_group_name in output: # Fallback to english name if powershell fails
                return "Admin"

        return "User"
    except subprocess.CalledProcessError:
        return "Unknown" # Impossible de déterminer

def get_all_system_info():
    """Rassemble toutes les informations système pertinentes."""
    info = {
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "current_user": getpass.getuser(),
        "domain_name": get_domain_name(),
        "local_users": get_local_users(),
        "local_admins": get_local_admins(),
        "current_user_privileges": get_current_user_privileges()
    }
    return info

if __name__ == '__main__':
    # Pour des tests directs
    system_details = get_all_system_info()
    for key, value in system_details.items():
        print(f"{key}: {value}") 