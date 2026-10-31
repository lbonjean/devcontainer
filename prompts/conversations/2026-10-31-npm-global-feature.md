# Globale npm-pakketten als Dev Container Feature — 2026-10-31

## Gebruikersverzoeken (verbatim)

```text
ik wil een devcontainer feature maken dat een aantal npm modules installeert met npm zoals in dit commando.
npm install -g @openai/codex
in de devcontainer is npm al geinstalleerd.
```

```text
committen in een andere branch
```

```text
zet dit pakket mee in de packages  @fission-ai/openspec@latest
```

## Geleverde wijziging

- Branch `feature/npm-global-packages` aangemaakt.
- Lokale Feature `npm-global-packages` met instelbare, door witruimte gescheiden npm-pakketten; standaard `@openai/codex @fission-ai/openspec@latest`.
- Feature ingeschakeld in `.devcontainer/devcontainer.json`. De reeds bestaande, niet-gecommitte `uv`-wijziging van de gebruiker is behouden en uitgesloten van de commit.
- Globale installatie gebruikt de eigenaar van de npm-prefix, zodat de nvm-installatie van `vscode` schrijfbaar blijft.
- README bijgewerkt met gebruiksvoorbeeld en toepassingsgebied; duurzame les vastgelegd.

## Validatie

- Bash-syntax en Feature JSON gevalideerd.
- Twee lokale testpakketten tweemaal met succes in een tijdelijke globale npm-prefix geïnstalleerd.
- Foutpad voor ontbrekende npm en lege pakketlijst gecontroleerd.
- Root-test van de scriptstap in de lopende container geblokkeerd door `no new privileges` bij `sudo`; volledige devcontainerbouw niet uitgevoerd omdat Docker/Dev Container CLI ontbreken.
- Eerste poging om alleen de eigen `devcontainer.json`-hunk te stagen faalde door een foutieve patchlengte; gecorrigeerde indexpatch is toegepast en de `uv`-wijziging blijft unstaged.
- Eerste ad-hoc JSON-controle faalde doordat inline `//`-commentaar niet was verwijderd; de gecorrigeerde controle slaagde voor beide features.
- `git diff --check` uitgevoerd voor de commit.

## Vervolgverzoek (verbatim)

```text
graag de packages als een array opbouwen.
["pakket1","pakket2"]
```

## Aanpassing en validatie

- De Dev Container Feature-specificatie accepteert alleen string- en boolean-opties. De pakketlijst is daarom verplaatst naar een echte JSON-array in `.devcontainer/features/npm-global-packages/packages.json`; de Feature-verwijzing in `devcontainer.json` gebruikt nu `{}`.
- `install.sh` leest en valideert de array met Node, dat met npm al in de image aanwezig is. De Feature-versie is verhoogd naar 2.0.0 vanwege de gewijzigde configuratievorm. README en duurzame les bijgewerkt.
- Twee lokale npm-testpakketten via de JSON-array tweemaal met succes geïnstalleerd; een array met ongeldig element gaf een fout en een lege array sloeg de installatie over.
- De bestaande, niet-gecommitte `uv`-regel blijft buiten de commit.

## Tweede vervolgverzoek (verbatim)

```text
ik wil het opgeven zoals hier de modules
[https://github.com/devcontainers/features/tree/main/src/powershell](https://github.com/devcontainers/features/tree/main/src/powershell)
```

## Correctie en validatie

- De officiële PowerShell Feature gebruikt voor `modules` een komma-gescheiden stringoptie in `devcontainer.json`. De eerdere interpretatie als aparte JSON-array was onjuist voor de bedoelde interface.
- `packages` is nu dezelfde soort stringoptie, met standaardwaarde leeg. Deze devcontainer stelt `@openai/codex,@fission-ai/openspec@latest` in. Het aparte `packages.json` is verwijderd en de README is aangepast. Feature-versie verhoogd naar 3.0.0 wegens gewijzigde configuratievorm.
- Twee lokale npm-testpakketten via de komma-gescheiden optie tweemaal succesvol geïnstalleerd. Lege lijst wordt overgeslagen; lege entries en een afsluitende komma leveren een fout op. Bash-syntax en Feature JSON gecontroleerd.
- De bestaande niet-gecommitte `uv`-regel blijft buiten de commit. Er is geen volledige devcontainerbuild uitgevoerd omdat Docker en de Dev Container CLI ontbreken.

## Vraag over arrayoptie (verbatim)

```text
kan dat ook als een list tussen []?
```

## Antwoord en controle

- Nee: de Dev Container Feature-specificatie laat voor een optie alleen `string` of `boolean` toe. Een directe configuratie zoals `"packages": ["pakket1", "pakket2"]` is daarom geen geldige Feature-optie.
- De huidige komma-gescheiden string is de vorm die de PowerShell Feature voor `modules` gebruikt. Een echte JSON-array kan wel in een apart bestand staan, maar dan wordt de lijst niet als Feature-optie in `devcontainer.json` opgegeven.
- Geen codebestanden gewijzigd. Specificatie opnieuw gecontroleerd; `git diff --check` uitgevoerd. De bestaande `uv`-wijziging blijft buiten de commit.

## PowerShell Feature en publicatie — vervolgverzoek (verbatim)

```text
- ik zou het idee van feature npm-global-packages graag gebruiken om een feature te maken wat hetzelfde doet voor powershell modules.
- ik zou de features ook graag publiceren zoals de container om ze makkelijkt te kunnen gebruiken op andere plaatsen. Echter zonder veel tagging enz, zo eenvoudig mogelijk.
```

## Geleverde wijziging en beslissingen

- `.devcontainer/features/powershell-modules/` toegevoegd met Feature-metadata, Bash-entrypoint en PowerShell-installatiescript. Optie `modules` accepteert komma-gescheiden Gallery-modulenamen; lege lijst slaat installatie over en ongeldige/lege entries worden geweigerd.
- Bestaande PowerShell/PowerShellGet-installatie vereist. Modules inclusief dependencies worden met `Save-Module` buiten PSModulePath opgehaald, naar de systeemwijde modulemap gekopieerd en tijdelijke bestanden worden altijd opgeruimd. Ontbrekende PSGallery-registratie wordt aangemaakt. Modulelicenties worden geaccepteerd. Bestaande versies blijven behouden.
- `.github/workflows/features.yml` packageert beide Features op PRs en publiceert op relevante main-pushes of handmatig op main met GITHUB_TOKEN naar GHCR onder de repositorynamespace. Publicaties worden geserialiseerd. Geen Git-tags, releasepromotie of documentatie-PRs; alleen Feature-versie verhogen bij een wijziging, waarna de officiële CLI versiealiases en latest beheert.
- README uitgebreid met lokaal PowerShell-gebruik, beide GHCR-referenties, publicatie, versieonderhoud, lockfile-upgrades en publieke packagezichtbaarheid.
- Bestaande niet-gecommitte `.devcontainer/devcontainer.json` en `.devcontainer/devcontainer-lock.json` blijven onaangeroerd en buiten de commit. Werk uitgevoerd op bestaande branch `feature/npm-global-packages`.

## Validatie en beperkingen

- Bash-syntax, PowerShell-parser, beide Feature-JSON-bestanden en workflow-YAML succesvol gecontroleerd; `git diff --check` geslaagd.
- Lege modulelijst getest via het echte Bash-entrypoint. Afsluitende komma, lege entry en wildcard worden geweigerd.
- Herhaalde installatie tweemaal getest met gesimuleerde Gallery en tijdelijke doelmap, inclusief trimmen, deduplicatie en het kopiëren van dependencies. Geen echte Gallery-download of systeeminstallatie uitgevoerd.
- Officiële `npx @devcontainers/cli features package` geprobeerd, maar npm leverde geen uitvoer en de poging is afgebroken. CLI-packaging en Docker-integratie zijn lokaal niet geverifieerd; Docker en de CLI ontbreken in de devcontainer. De nieuwe workflow voert de packagingcontrole op GitHub uit.
- Officiële CLI-publishbron en Microsoft Save-Module-documentatie geraadpleegd. Een aanvankelijk geraadpleegde CLI-documentatie-URL gaf 404; gecorrigeerd naar de broncode.
- Geen push of daadwerkelijke registrypublicatie uitgevoerd; die volgt na het beschikbaar maken van de workflow op main.

## Installatie ImportExcel controleren — gebruikersverzoek (verbatim)

```text
hoe weet ik of import-excel ginstalleerd is?
```

## Antwoord en validatie

- Controle uitgevoerd met `Get-Module -ListAvailable -Name ImportExcel | Select-Object Name, Version, ModuleBase` in een verse PowerShell-sessie. Geen resultaten: ImportExcel is niet beschikbaar via PSModulePath in deze container.
- Gebruiker krijgt het controlecommando, uitleg dat geen uitvoer betekent dat PowerShell de module niet vindt en `Import-Module ImportExcel -ErrorAction Stop` als laadcontrole.
- Alleen gesprekslog gewijzigd; `git diff --check` geslaagd. Eerste commitpoging van het vorige verzoek werd door de alleen-lezen .git-sandbox geblokkeerd; daarna met toegestane escalatie succesvol gecommit.
