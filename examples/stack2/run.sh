#!/bin/bash -ex
rainbow \
    --block \                                        # block until the stack creation is finished. exits with a non-zero exit code upon failure
    --data-source yaml:parameters.yaml \             # the only data source is our parameters.yaml
    rainbow-stack2-sg \                              # stack name
    templates/SecurityGroup.yaml                     # stack template

rainbow \                                            # note that this script is run with bash -e
    --block \                                        # block until the stack creation is finished (and show the events)
    --data-source yaml:parameters.yaml \             # first priority data source is parameters.yaml, like the previous stack
    --data-source cfn_resources:rainbow-stack2-sg \  # second priority data source is the CFN resources created on previous stack
    rainbow-stack2-asg \                             # stack name
    templates/AutoscalingGroup.yaml                  # stack template

