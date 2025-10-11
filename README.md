# Frame Art — Intégration Home Assistant (UI)

**Prérequis :** l’intégration **SamsungTV Smart (ollo69)** doit être installée et configurée (entité `media_player` disponible).

Intégration avec **Config Flow** :
- ajoute automatiquement un **switch** pour activer/désactiver l’Art Mode,
- quand le switch passe sur **OFF**, bascule sur l’entrée HDMI (libellé) puis le contexte **TV/HDMI** via **ha-samsungtv-smart**.

## Installation
1. Copiez `custom_components/frame_art` dans votre config Home Assistant.
2. Redémarrez Home Assistant.
3. Allez dans *Paramètres → Intégrations → Ajouter une intégration → Frame Art*.

## Options
- **Adresse TV (resource)** : IP/host utilisé par `samsungtvws` pour l’Art Mode.
- **Entité Samsung TV** : `media_player` de l’intégration `ha-samsungtv-smart`.
- **Source (HDMI)** : libellé tel que vu dans `source_list` (ex. `Home cinéma`).
- **Contexte/App** : généralement `TV/HDMI`.
- **Délais & retries** : pour fiabiliser la séquence OFF → HDMI.

Remarques :
- Séquence **source puis app** (retour terrain).
- Fallback si `select_app` absent : `media_player.select_source(app_id)`.
