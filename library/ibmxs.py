#!/usr/bin/python

#
#=======
# Author: Maksim fominov <mfominov@gmail.com>
#
# This is an Ansible module. Installs/Uninstall IBM WebSphere Extreme Scale Server Binaries
#
# $IM_INSTALL_DIR/eclipse/tools/imcl install com.ibm.websphere.WXS.v86_8.6.0.20121115_1943
# -repositories $XS_REPO_DIR
# -installationDirectory $XS_INSTALL_DIR
# -acceptLicense -showProgress

import os
import subprocess
import platform
import datetime
import shutil

def check_xs_installed(ibmim):
    child = subprocess.Popen([ibmim + "/eclipse/tools/imcl listInstalledPackages"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find("com.ibm.websphere.WXS") < 0:
        return True

def main():

    # XS offerings
    offerings = [
        'com.ibm.websphere.WXS.v86',
        'com.ibm.websphere.WXS.was7.v86',
        'com.ibm.websphere.WXS.was8.v86',
        'com.ibm.websphere.WXSCLIENT.v86',
        'com.ibm.websphere.WXSCLIENT.was7.v86',
        'com.ibm.websphere.WXSCLIENT.was8.v86'
    ]

    # Read arguments
    module = AnsibleModule(
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            ibmim     = dict(required=True),
            dest      = dict(required=True),
            repo      = dict(required=False),
            offering  = dict(default='com.ibm.websphere.WXS.v86', choices=offerings),
            logdir    = dict(required=False)
        )
    )

    state = module.params['state']
    ibmim = module.params['ibmim']
    dest = module.params['dest']
    repo = module.params['repo']
    offering = module.params['offering']
    logdir = module.params['logdir']

    # Check if paths are valid
    if not os.path.exists(ibmim + "/eclipse"):
        module.fail_json(msg=ibmim + "/eclipse not found")

    # Installation
    if state == 'present':
        if check_xs_installed(ibmim):
            child = subprocess.Popen([ibmim + "/eclipse/tools/imcl install " + offering + " -repositories " + repo + " -installationDirectory " + dest + " -acceptLicense"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(msg="XS install failed", stdout=stdout_value, stderr=stderr_value)
            module.exit_json(changed=True, msg="XS installed successfully", stdout=stdout_value)
        else:
            module.exit_json(changed=False, msg="XS already installed")

    # Uninstall
    if state == 'absent':
        if os.path.exists(logdir):
            if not os.listdir(logdir):
                os.makedirs(logdir)
        if check_xs_installed(ibmim):
            logfile = platform.node() + "_xs_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xml"
            child = subprocess.Popen([ibmim + "/eclipse/tools/imcl uninstall " + offering + " -installationDirectory " + dest + " -log " + logdir + "/" + logfile], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(msg="XS uninstall failed", stdout=stdout_value, stderr=stderr_value)
            shutil.rmtree(dest, ignore_errors=False, onerror=None)
            module.exit_json(changed=True, msg="XS uninstalled successfully", stdout=stdout_value)
        else:
            module.exit_json(changed=False, msg="XS already uninstalled")

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
