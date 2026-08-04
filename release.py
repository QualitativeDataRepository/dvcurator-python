#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check the repository over and tag a new dvcurator release.

Releases are driven by tags: pushing a "v*" tag triggers
.github/workflows/build.yml, which rewrites dvcurator/version.py from the tag,
builds the Windows executable with pyinstaller, and opens a DRAFT release with
the .exe attached.

This script does the checking and the tagging. It deliberately does not push
anything -- it prints the commands to run once you have looked the tag over.

    python release.py v1.1.3
    python release.py 1.1.3 --skip-tests
"""

import argparse
import os
import re
import subprocess
import sys

RELEASES = "https://github.com/QualitativeDataRepository/dvcurator-python/releases"

def fail(message):
    """Print an error and stop, leaving the repository as we found it"""
    print("\nERROR: " + message)
    sys.exit(1)

def step(message):
    print("\n==> " + message)

def run_git(*args):
    """Run a git command, returning the finished process"""
    return subprocess.run(("git",) + args, capture_output=True, text=True)

def git(*args):
    """Run a git command that is expected to succeed, returning its output"""
    result = run_git(*args)
    if (result.returncode != 0):
        fail("git " + " ".join(args) + " failed:\n" + result.stderr.strip())
    return result.stdout.strip()

def check_version(version):
    """
    Normalise a version and check it looks like a release tag

    :param version: Version as typed on the command line, i.e. "1.1.3"
    :type version: String
    :return: The version with a leading "v"
    :rtype: String
    """
    if not version.startswith("v"):
        version = "v" + version

    # build.yml triggers on "v*", and version.py is derived with --match "v[0-9]*"
    if not re.match(r"^v[0-9]+(\.[0-9]+)*$", version):
        fail("'" + version + "' is not a release version. Expected something like v1.1.3.")

    return version

def check_working_tree():
    """Refuse to tag a tree that doesn't match the commit we're tagging"""
    step("Checking the working tree")

    # Only tracked changes matter: those are the difference between the working
    # tree and the commit we are about to tag
    modified = git("status", "--porcelain", "--untracked-files=no")
    if modified:
        for line in modified.splitlines():
            print("  " + line)
        fail("Working tree has uncommitted changes. Commit or stash before releasing.")

    # Untracked files aren't in the commit, so they don't block the release.
    # Worth pointing out though, in case one was meant to be part of it
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if untracked:
        print("WARNING: untracked files, not part of this release:")
        for line in untracked[:10]:
            print("  " + line)
        if (len(untracked) > 10):
            # An un-ignored directory can run to thousands of files
            print("  ... and " + str(len(untracked) - 10) + " more")

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if (branch != "master"):
        fail("On branch '" + branch + "'. Releases are tagged on master.")

    print("Clean, on master.")

def check_tag_unused(version):
    """Refuse to reuse a version, locally or on origin"""
    step("Checking " + version + " is unused")

    if (run_git("rev-parse", "-q", "--verify", "refs/tags/" + version).returncode == 0):
        fail("Tag " + version + " already exists locally. "
            "Delete it with 'git tag -d " + version + "' if it was a mistake.")

    if git("ls-remote", "--tags", "origin", "refs/tags/" + version):
        fail("Tag " + version + " already exists on origin. Pick a new version.")

    print(version + " is free.")

def check_origin():
    """
    Compare the local branch with origin

    :return: How many commits master is ahead of origin
    :rtype: int
    """
    step("Comparing with origin/master")

    git("fetch", "origin", "master", "--quiet")

    behind = int(git("rev-list", "--count", "HEAD..origin/master"))
    if behind:
        fail("Local master is " + str(behind) + " commit(s) behind origin/master. "
            "Pull before releasing.")

    # Unpushed commits are fine to tag, but master has to be pushed first or the
    # release gets built from commits that aren't on the branch yet
    ahead = int(git("rev-list", "--count", "origin/master..HEAD"))
    if ahead:
        print("WARNING: " + str(ahead) + " commit(s) not yet on origin/master. "
            "Push master before the tag.")
    else:
        print("Up to date with origin/master.")

    return ahead

def run_tests():
    """Run the test suite with the interpreter running this script"""
    step("Running the test suite")

    probe = subprocess.run([sys.executable, "-c", "import pikepdf, requests, docx2pdf"],
        capture_output=True, text=True)
    if (probe.returncode != 0):
        message = ("Test dependencies are missing from " + sys.executable + ":\n"
            "  " + probe.stderr.strip().splitlines()[-1] + "\n\n"
            "Install them with:\n"
            "  " + sys.executable + " -m pip install -r requirements.txt")
        venv = os.path.join(".venv", "Scripts" if os.name == "nt" else "bin", "python")
        if os.path.exists(venv + (".exe" if os.name == "nt" else "")):
            message += "\n\nOr run this script with the venv you already have:\n  " + venv + " release.py ..."
        fail(message)

    if (subprocess.run([sys.executable, "-m", "unittest", "test"]).returncode != 0):
        fail("Tests failed. Fix them, or re-run with --skip-tests if you know better.")

    print("Tests passed.")

def main():
    parser = argparse.ArgumentParser(
        description="Check the repository over and tag a new dvcurator release.")
    parser.add_argument("version", help="version to tag, e.g. v1.1.3")
    parser.add_argument("--skip-tests", action="store_true",
        help="don't run the test suite first")
    args = parser.parse_args()

    # Always work from the repository, not wherever the shell happens to be
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    version = check_version(args.version)
    step("Releasing " + version)

    check_working_tree()
    check_tag_unused(version)
    ahead = check_origin()

    if args.skip_tests:
        step("Skipping tests (--skip-tests)")
    else:
        run_tests()

    step("Tagging")
    git("tag", "-a", version, "-m", "dvcurator " + version)
    print("Created " + version + " at " + git("rev-parse", "--short", "HEAD"))

    print("\nNothing has been pushed.\n")
    print("To release:")
    if ahead:
        print("  git push origin master")
    print("  git push origin " + version)
    print("\nThat starts the build. When it finishes it leaves a DRAFT release:")
    print("  " + RELEASES)
    print("\nPublish the draft. 'SU Lab Install.ps1' resolves /releases/latest, which")
    print("ignores drafts, so an unpublished release quietly keeps handing out the")
    print("previous version.")
    print("\nTo undo the tag before pushing: git tag -d " + version)

if __name__ == "__main__":
    main()
