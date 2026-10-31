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
