# Accès SSH distant au Raspberry Pi via Tailscale

Par défaut, le Pi est seulement accessible sur le réseau local (192.168.x.x).
Tailscale crée un tunnel chiffré entre tes appareils — accessible depuis n'importe où, sans toucher au routeur.

## Installation (à faire une fois, depuis le réseau local)

### 1. Installer Tailscale sur le Raspberry Pi

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Un lien s'affiche dans le terminal. Ouvre-le dans un navigateur et connecte-toi avec ton compte (Google, GitHub ou email). Le Pi apparaît dans ton réseau Tailscale et reçoit une IP fixe (`100.x.x.x`).

### 2. Installer Tailscale sur ta machine personnelle

**Linux :**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**Windows / Mac :** télécharger l'app sur [tailscale.com/download](https://tailscale.com/download) et se connecter avec le même compte.

### 3. Vérifier que le Pi est visible

```bash
tailscale status
```

Tu verras le Pi listé avec son IP Tailscale (`100.x.x.x`).

---

## Connexion SSH depuis n'importe où

```bash
ssh pi@100.x.x.x
# ou avec ton nom d'utilisateur réel
ssh <user>@100.x.x.x
```

L'IP Tailscale du Pi est fixe — elle ne change pas même si ton IP publique change.

### Avec un fichier ~/.ssh/config (pratique)

Ajoute ceci dans `~/.ssh/config` sur ta machine :

```
Host queens-pi
    HostName 100.x.x.x
    User pi
```

Ensuite tu peux juste faire :

```bash
ssh queens-pi
```

---

## Récupérer l'IP Tailscale du Pi (si tu ne l'as pas notée)

Depuis le Pi en local :
```bash
tailscale ip -4
```

Ou depuis le dashboard en ligne : [login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines)

---

## Démarrage automatique au boot

Tailscale se lance automatiquement après l'installation. Pour vérifier :

```bash
sudo systemctl status tailscaled
# doit afficher "active (running)"
```

Si ce n'est pas le cas :
```bash
sudo systemctl enable --now tailscaled
```

---

## Commandes utiles

```bash
# Statut de la connexion
tailscale status

# IP du Pi
tailscale ip -4

# Déconnecter (le Pi disparaît du réseau Tailscale)
sudo tailscale down

# Reconnecter
sudo tailscale up
```

---

## Notes

- **Gratuit** pour un usage personnel (jusqu'à 100 appareils).
- **Chiffrement** bout en bout via WireGuard — plus sécurisé qu'un port 22 exposé sur le routeur.
- **Fonctionne partout** : derrière un NAT strict, 4G, VPN entreprise…
- Le Pi doit être allumé et connecté à Internet pour être joignable.
