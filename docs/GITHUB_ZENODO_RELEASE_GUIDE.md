# GitHub and Zenodo release guide

This is an instruction-only workflow. No repository or DOI has been published.

## 1. Complete the hold checklist

Finish `PRE_PUBLICATION_CHECKLIST.md`. In particular, approve authorship, choose a license, determine which derived tables can be shared, replace unlicensed boundaries, and recover or transparently document missing analytical code.

## 2. Build a clean public tree

From the repository directory:

```bash
python scripts/audits/preflight_public_tree.py
git init
git status --ignored
```

Inspect the output carefully. `data/review_required/`, `outputs/`, PPTX files, raw rasters/NetCDF/HDF files, caches, and secrets must not be staged by default.

Add only approved files:

```bash
git add README.md requirements.txt environment scripts docs data/README.md data/external .gitignore LICENSE CITATION.cff
git diff --cached --stat
git diff --cached
git commit -m "Prepare reproducibility package for manuscript review"
```

Do not use `git add .` until the ignored and untracked file list has been manually audited.

## 3. Create a private GitHub repository first

1. In GitHub, create a new repository under the approved personal or organizational owner.
2. Start it as **Private**.
3. Do not prepopulate it with another README, `.gitignore`, or license if this local directory will be pushed directly.
4. Add the remote and push:

```bash
git branch -M main
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

5. Add only approved collaborators.
6. Enable secret scanning/push protection where available.
7. Review the GitHub file list in the browser and confirm that review-hold data and large source artwork are absent.

## 4. Reviewer access before public release

Follow the journal's current confidential-review workflow. If a private repository link is unsuitable, provide a reviewer-only archival copy through the submission system or a repository feature that supports confidential access. The manuscript statement must distinguish reviewer access from permanent public availability.

## 5. Prepare citation metadata

Replace `CITATION.cff.template` with a validated `CITATION.cff` only after approving:

- title;
- creator order and ORCIDs;
- affiliation/contributor roles;
- release version and date;
- license;
- public GitHub URL; and
- Zenodo DOI after it exists.

If both `.zenodo.json` and `CITATION.cff` are present, Zenodo currently prioritizes `.zenodo.json` for GitHub release metadata. Use one authoritative metadata source unless there is a deliberate reason to maintain both.

## 6. Connect GitHub to Zenodo

1. Sign in to Zenodo with the approved account.
2. Link the GitHub account.
3. Open the Zenodo GitHub integration page and synchronize repositories.
4. Find the repository and enable the integration.
5. Confirm that the intended owner/repository, authors, license, and metadata are correct.

Use the Zenodo sandbox for a dry run if the team is unfamiliar with the workflow.

## 7. Create a release only after approval

1. Make the GitHub repository public only when all authors approve.
2. Create an annotated version tag, for example:

```bash
git tag -a v1.0.0 -m "Version associated with the manuscript"
git push origin v1.0.0
```

3. In GitHub Releases, create a **draft** release from that tag.
4. Verify release notes, files, authorship, and license.
5. Publish the GitHub release. Zenodo should ingest the enabled release and create an archived software record.
6. Wait for Zenodo processing, then open the resulting record and verify the DOI and archival status.

Publishing a GitHub release and Zenodo record is a consequential, externally visible action. Do it manually only after final approval.

## 8. Update the manuscript

Replace the manuscript placeholder with:

- the public GitHub development URL;
- the version-specific Zenodo DOI for the exact release used by the paper;
- the software version and license/access conditions; and
- a full software citation in the References.

Prefer the version DOI when citing the exact software used for the article. Keep any concept DOI for directing readers to the latest version only if that choice matches the journal and repository guidance.

## 9. Preserve release evidence

Archive locally:

- the exact commit SHA and tag;
- the GitHub release URL;
- the Zenodo DOI and exported citation;
- a copy of final `CITATION.cff` and `LICENSE`;
- the final public file manifest/checksums; and
- the Open Research wording submitted to the journal.

## 10. Future updates

Never replace files silently after publication. Correct code in a new Git commit and release a new semantic version. Zenodo will create a version-specific record, preserving the cited release.
