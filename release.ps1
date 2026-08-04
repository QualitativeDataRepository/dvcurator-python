<#
.SYNOPSIS
    Check the repository over and tag a new dvcurator release.

.DESCRIPTION
    Releases are driven by tags: pushing a "v*" tag triggers .github/workflows/build.yml,
    which rewrites dvcurator/version.py from the tag, builds the Windows executable with
    pyinstaller, and opens a DRAFT release with the .exe attached.

    This script does the checking and the tagging. It deliberately does not push
    anything -- it prints the commands to run once you have reviewed the tag.

.PARAMETER Version
    Version to tag, e.g. "v1.1.3". The leading "v" is added if you leave it off.

.PARAMETER SkipTests
    Skip the test suite. The tests need the packages in requirements.txt and they
    do hit the network, so this is here for when that isn't possible.

.EXAMPLE
    .\release.ps1 v1.1.3

.EXAMPLE
    .\release.ps1 1.1.3 -SkipTests
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Version,

    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'

function Fail($message) {
    Write-Host ""
    Write-Host "ERROR: $message" -ForegroundColor Red
    exit 1
}

function Step($message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Cyan
}

# Always work from the repository, not wherever the shell happens to be
Set-Location -Path $PSScriptRoot

# --- Check the version looks like a release tag ------------------------------

if (-not $Version.StartsWith('v')) {
    $Version = "v$Version"
}

# build.yml triggers on "v*", and version.py is derived with --match "v[0-9]*"
if ($Version -notmatch '^v[0-9]+(\.[0-9]+)*$') {
    Fail "'$Version' is not a release version. Expected something like v1.1.3."
}

Step "Releasing $Version"

# --- Check the working tree --------------------------------------------------

Step "Checking the working tree"

$dirty = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    Fail "git status failed. Is this a git repository?"
}
if ($dirty) {
    $dirty | ForEach-Object { Write-Host "  $_" }
    Fail "Working tree is not clean. Commit or stash before releasing."
}

$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if ($branch -ne 'master') {
    Fail "On branch '$branch'. Releases are tagged on master."
}

Write-Host "Clean, on master." -ForegroundColor Green

# --- Check the tag is actually new -------------------------------------------

Step "Checking $Version is unused"

$null = git rev-parse -q --verify "refs/tags/$Version"
if ($LASTEXITCODE -eq 0) {
    Fail "Tag $Version already exists locally. Delete it with 'git tag -d $Version' if it was a mistake."
}

$remoteTag = git ls-remote --tags origin "refs/tags/$Version"
if ($LASTEXITCODE -ne 0) {
    Fail "Could not reach origin to check existing tags."
}
if ($remoteTag) {
    Fail "Tag $Version already exists on origin. Pick a new version."
}

Write-Host "$Version is free." -ForegroundColor Green

# --- Compare against origin --------------------------------------------------

Step "Comparing with origin/master"

git fetch origin master --quiet
if ($LASTEXITCODE -ne 0) {
    Fail "Could not fetch from origin."
}

$behind = (git rev-list --count "HEAD..origin/master").Trim()
if ($behind -ne '0') {
    Fail "Local master is $behind commit(s) behind origin/master. Pull before releasing."
}

# Unpushed commits are fine to tag, but master has to be pushed first or the
# release will be built from commits nobody else can see
$ahead = (git rev-list --count "origin/master..HEAD").Trim()
if ($ahead -ne '0') {
    Write-Host "$ahead commit(s) not yet on origin/master. Push master before the tag." -ForegroundColor Yellow
} else {
    Write-Host "Up to date with origin/master." -ForegroundColor Green
}

# --- Tests -------------------------------------------------------------------

if ($SkipTests) {
    Step "Skipping tests (-SkipTests)"
} else {
    Step "Running the test suite"

    $python = 'python'
    if (Test-Path '.venv\Scripts\python.exe') {
        $python = '.venv\Scripts\python.exe'
        Write-Host "Using .venv"
    }

    & $python -m unittest test
    if ($LASTEXITCODE -ne 0) {
        Fail "Tests failed. Fix them, or re-run with -SkipTests if you know better."
    }

    Write-Host "Tests passed." -ForegroundColor Green
}

# --- Tag ---------------------------------------------------------------------

Step "Tagging"

git tag -a $Version -m "dvcurator $Version"
if ($LASTEXITCODE -ne 0) {
    Fail "Could not create the tag."
}

$sha = (git rev-parse --short HEAD).Trim()
Write-Host "Created $Version at $sha" -ForegroundColor Green

# --- What to do next ---------------------------------------------------------

Write-Host ""
Write-Host "Nothing has been pushed." -ForegroundColor Yellow
Write-Host ""
Write-Host "To release:"
if ($ahead -ne '0') {
    Write-Host "  git push origin master"
}
Write-Host "  git push origin $Version"
Write-Host ""
Write-Host "That starts the build. When it finishes it leaves a DRAFT release:"
Write-Host "  https://github.com/QualitativeDataRepository/dvcurator-python/releases"
Write-Host ""
Write-Host "Publish the draft. 'SU Lab Install.ps1' resolves /releases/latest, which"
Write-Host "ignores drafts, so an unpublished release quietly keeps handing out the"
Write-Host "previous version."
Write-Host ""
Write-Host "To undo the tag before pushing: git tag -d $Version"
Write-Host ""
