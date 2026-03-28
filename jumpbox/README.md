# Jumpbox + MySQL-proxy (Terraform)

Dette prosjektet setter opp en **jumpbox-VM i Azure** som kjører Nginx som **TCP-proxy** på port **3306** mot prod DB MySQL-instansen. VM-en klargjøres via cloud-init: den installerer bl.a. `mysql-client` og `nginx`, skriver en Nginx-konfig som åpner en `stream {}`-proxy på port 3306 og peker videre til `${db_host}:3306`, og setter tidssone (`${timezone}`).&#x20;

## Arkitektur i korte trekk

* **Azure VM (jumpbox)** med offentlig IP og SSH-tilgang.
* **Nginx TCP-proxy** på VM-en lytter på `:3306` og videresender direkte til MySQL-FQDN (`db_host`). Dette gjør at du kan koble MySQL-klienter til jumpbox (evt. via SSH-tunnel) og treffe databasen uten å eksponere DB-en.&#x20;
* **cloud-init** sørger for installasjoner, Nginx-konfig og enable/reload av tjenesten.&#x20;

## Innhold i repoet

* `main.tf` – Azure-ressurser (RG, nett, IP, NIC, VM osv.)
* `vars.tf` – Variabler (f.eks. `db_host`, `timezone`, VM-størrelse, brukernavn/SSH-nøkkel)
* `data.tf` – Eventuelle data-kilder (f.eks. hent siste Ubuntu-image)
* `outputs.tf` – Nyttige outputs (f.eks. public IP, private IP, FQDN)
* `cloud-init.yaml.tmpl` – Cloud-init-mal som bl.a. setter opp Nginx TCP-proxy til `${db_host}` og tidssone `${timezone}`.&#x20;

## Forutsetninger

* Terraform installert og innlogget mot Azure (`az login`).
* SSH-nøkkel tilgjengelig (public key referert i variabler).


## Variabler

Opprett en fil `vars.auto.tfvars` i rotmappen for å sette disse verdiene:

```hcl
subscription_id = "<din-azure-subscription-id>"
tenant_id       = "<din-azure-tenant-id>"

admin_username  = "azureuser"
ssh_public_keys = ["<din-public-key>"]

timezone  = "Europe/Oslo"
```

Terraform vil automatisk plukke opp denne filen.

## Kom i gang

1. **Init / plan / apply**

```bash
terraform init
terraform plan
terraform apply
```

2. **Finn IP-en**
   Etter `apply` får du outputs (f.eks. `jumpbox_public_ip`). Bruk denne for SSH/MySQL-tilkobling.

3. **Test Nginx-proxyen**
   Koble direkte fra din maskin til jumpbox på 3306 (åpen port må tillates i NSG):

```bash
mysql -h <jumpbox_public_ip> -P 3306 -u <db_user> -p
```

Nginx videresender da til `${db_host}:3306`.&#x20;

**Alternativ (anbefalt): SSH-tunnel + lokal klient**

```bash
ssh -N -L 3306:127.0.0.1:3306 azureuser@<jumpbox_public_ip>
# Nytt terminalvindu:
mysql -h 127.0.0.1 -P 3306 -u <db_user> -p
```

Da snakker klienten din til Nginx på VM-en, som igjen proxier til DB-FQDN.&#x20;

## Hva cloud-init gjør (high-level)

* Installerer pakker: `mysql-client`, `nginx-full`, `htop`, `jq`, `curl`, `net-tools`.
* Skriver `/etc/nginx/nginx.conf` med en `stream { server { listen 3306; proxy_pass ${db_host}:3306; } }`.
* Kjører `nginx -t`, enable + start, og `systemctl reload`.
* Setter tidssone med `timedatectl set-timezone ${timezone}`.&#x20;

## Vanlige problemer

* **Access denied mot MySQL:** Sjekk at brukeren er opprettet korrekt for tilkoblinger via jumpbox (kilden vil se ut som jumpbox-ens IP).
* **Tilkobling henger ut:** Verifiser at port 3306 er åpen i NSG mot din klient/SSH-tunnel, og at `db_host` er riktig.
* **Privat DB / Private Endpoint:** Hvis DB-en kun er privat, må jumpbox ha nettverksrute/DNS som kan resolve og nå privat FQDN/IP. Nginx-proxyen forventer at `${db_host}` er nåbar fra VM-en.&#x20;

## Rydd opp

```bash
terraform destroy
```

