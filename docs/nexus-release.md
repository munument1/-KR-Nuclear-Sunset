# Nexus Mods release publishing

Target: https://www.nexusmods.com/newvegas/mods/99974

The workflow uses the existing repository secret `NEXUS_KEY`. The key must belong to the mod owner.
It mirrors only `NuclearSunset-Korean-Patcher-<tag>.zip`; translation-data archives are not uploaded.
SHA256 and ZIP integrity, API authentication, ownership, target file and existing versions are checked before upload.
The sole active Nexus file is selected automatically. If multiple files exist, set repository variable
`NEXUSMODS_FILE_ID` to the upload API File ID shown under Files / Advanced for the patcher.

New stable GitHub releases trigger publishing. Drafts and prereleases are rejected.
Releases created with GITHUB_TOKEN do not trigger another release workflow: explicitly dispatch this workflow
after such releases. The current site build does not create patcher releases.

For existing releases, run **Publish patcher to Nexus Mods** from Actions with the release tag.
`dry_run=true` (default) validates the package and credentials without uploading.
Use `dry_run=false` to publish. An existing active version with the same version number is skipped.
Do not replace release assets under an already-published tag; publish a new version instead.

Previous Nexus versions are retained. Mod manager download is disabled because this is a standalone patcher.
File descriptions include the installation guide, GitHub release and an English notice that original game/mod
data is not included. The Nexus mod page Description is managed separately on the website.
