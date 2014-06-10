#!/bin/bash -ex
rainbow \
    --block \
    --data-source yaml:parameters.yaml \ # the only data source we have for this stack is our parameters.yaml file
    rainbow-stack1 \                     # stack name
    template.yaml                        # stack template

