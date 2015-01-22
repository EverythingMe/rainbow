# v1.0 - ????
* Backward-incompatible change: removed --noop
* New parameters:
    --dump-stack-template-json
    --dump-stack-parameters-json
    --dump-template-json
    --dump-parameters-json
    --compare-template
    --compare-parameters

# v0.4 - 20150120
* Fixed a bug in handling of comma separated parameters
* Added --update-stack-if-exists command line option
* When updating a stack with no updates, exit with 0
* Comments in example bash scripts fixed
* New datasource: cfn_parameters

# v0.3 - 20140713
* Fixed Rb::InstanceChooser not to accept a string parameter, only lists
* Fixed a bug where Rb::InstanceChooser didn't handle pointers to lists properly
* Fixed handling of default values in Cloudformation parameters
* Template !yaml magic can now specify a root key
* Fixed preprocessing bug (Rb:: function handling) with int keys in templates

# v0.2 - 20140610
* setup.py changes for PIP
* README updated on usage/installation

# v0.1 - 20140610
* Initial release

