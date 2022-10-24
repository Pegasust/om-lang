#!/usr/bin/env sh

# Migrate into subdirectory. First, create a temp copy and modify it there
mkdir /tmp/omega-lang
git clone ~/local_repos/csc453-compilers /tmp/omega-lang
cd /tmp/omega-lang

# Filter the history so that it's rewritten in subdirectory
git filter-branch -f --prune-empty --tree-filter '
    mkdir -p impl/python
    git ls-tree --name-only $GIT_COMMIT | xargs -I{} mv {} impl/python
'

# Add remote and merge history
cd ~/local_repos/omega-lang-pegasust
git remote add omega-lang-python /tmp/omega-lang
git fetch omega-lang-python
git merge omega-lang-python/master

# clean up
git remote rm omega-lang-python
rm -rf /tmp/omega-lang
