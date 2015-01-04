#!/bin/bash -ex
rainbow \
    --block                                             `# block until the stack creation is finished. exits with a non-zero exit code upon failure` \
    rainbow-stack3-sgs                                  `# stack name` \
    templates/SecurityGroups/*.yaml                     `# stack templates. those are being merged into a single template`

for ROLE in loadbalancer web database; do               `# create a stack for each role: loadbalancer, web, database`
    rainbow \
        --block \
        --data-source yaml:parameters/${ROLE}.yaml      `# first priority data source, includes overrides for base.yaml` \
        --data-source yaml:parameters/base.yaml         `# default values` \
        --data-source cfn_resources:rainbow-stack3-sgs  `# security groups` \
        rainbow-stack3-${ROLE}                          `# stack name is rainbow-stack3-<role>` \
        templates/GenericRole.yaml                      `# use the same template for all 3 roles`
done

