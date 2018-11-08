#!/bin/bash

# don't delete this line, or copy that content and adjust it
. ./virtualization/drifter/ci/test-header.sh

~/ENV/bin/tox -r

# don't delete this line, or copy that content and adjust it
. ./virtualization/drifter/ci/test-footer.sh
