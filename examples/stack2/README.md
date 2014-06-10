EXAMPLE 2 - Split stack
=======================

This example is based on example1, but I broke the stack into two stacks:
* `rainbow-stack2-sg` containing the `SecurityGroup` resource
* `rainbow-stack2-asg` containing the `AutoscalingGroup` and the `LaunchConfig` resources
 
The order of the creation is important because the `rainbow-stack2-asg` stack references the `SecurityGroup` resource from `rainbow-stack2-sg`. It does that by utilizing the `cfn_resources` datasource. You can read more about datasources by reading the main `README.md` file.

