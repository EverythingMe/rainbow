EXAMPLE 3 - Big cluster
=======================

* `rainbow-stack3-sgs` containing the `SecurityGroup` resources `AllSecurityGroup`, `LoadBalancerSecurityGroup`, `WebSecurityGroup` and `DatabaseSecurityGroup`. Stack is generated from multiple templates being merged (`templates/SecurityGroups/*.yaml`)
* `rainbow-stack3-loadbalancer`, `rainbow-stack3-web`, `rainbow-stack3-database` containing the `AutoscalingGroup` and the `LaunchConfig` resources for each role. All stacks are generated from a single template (`templates/GenericRole.yaml`) with datasource overrides per-role (`parameters/role.yaml`).

