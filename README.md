## Studio del framework Matrix per la comunicazione sicura di gruppo

### Candidati:

- Celentano Gaetano M63001636
- Navarra Luca M63001578

### Steps:

- Creazione della VM da usare come server (Azure)
  - Setup di rete
- Ottenimento del Domain Name
  - DuckDNS
  - AzureDNS
- Configurazione _reverse proxy_
  - `Caddy`
  - `nginx`
- Setup homeserver per consentire le comunicazioni con Matrix
  - installazione e configurazione di _Synapse_
  - installazione e configurazione di _PostgreSQL_
  - installazione e configurazione di _Matrix_
    - configurazione file `yaml`
  - configurazione per l'abilitazione alla registrazione degli utenti
    - setup di `Google Re-CAPTCHA`
  - configurazione per le `federation`
    - ottenimento dei certificati `ssl` tramite `Let's Encrypt`
    - modifiche dei file `homeserver.yaml` (e `Caddyfile`) per consentire le `federation`
- Studio dello scambio di messaggi (con _WireShark_)
  - lato client
  - lato server
- Studio degli aspetti di sicurezza
  - dump del traffico
  - dump del database
- Studio di possibili scenari di attacco
