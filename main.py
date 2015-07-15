import sys
import os
import uuid

if sys.version_info < (3, 0):
    from typescript.libs import *
    from typescript.libs.reference import *
    from typescript.libs.view_helpers import *
    from typescript.listeners import *
    from typescript.commands import *
    from typescript.libs.telemetry import *
else:
    from .typescript.libs import *
    from .typescript.libs.reference import *
    from .typescript.libs.view_helpers import *
    from .typescript.libs.telemetry import *
    from .typescript.listeners import *
    from .typescript.commands import *

# Enable Python Tools for visual studio remote debugging
try:
    from ptvsd import enable_attach

    enable_attach(secret=None)
except ImportError:
    pass


def _cleanup_011():
    """Remove any old zipped package installed by 0.1.1 release"""
    this_file = os.path.abspath(__file__)

    # Is the current file running under installed packages or packages?
    offset = this_file.find(os.path.sep + 'Installed Packages' + os.path.sep)
    if offset == -1:
        offset = this_file.find(os.path.sep + 'Packages' + os.path.sep)

    if offset == -1:
        print('ERROR: Could not location parent packages folder')
        return

    # Move/delete old package if present
    old_package = os.path.join(this_file[:offset], 'Installed Packages', 'TypeScript.sublime-package')
    temp_name = os.path.join(this_file[:offset], 'Installed Packages', 'TypeScript.-old-sublime-package')
    if os.path.exists(old_package):
        # Rename first, in case delete fails due to file in use
        print('Detected outdated TypeScript plugin package. Removing ' + old_package)
        os.rename(old_package, temp_name)
        os.remove(temp_name)

try:
    _cleanup_011()
except:
    pass

logger.log.warn('TypeScript plugin initialized.')


def plugin_loaded():
    """
    Note: this is not always called on startup by Sublime, so we call it
    from on_activated or on_close if necessary.
    """
    log.debug("plugin_loaded started")

    settings = sublime.load_settings('Preferences.sublime-settings')
    if not settings.has(telemetry_setting_name):
        # TODO: get real privacy file text
        this_file = os.path.abspath(__file__)
        privacy_file = this_file[0:this_file.rfind(os.path.sep)] + os.path.sep + "privacyPolicy.txt"
        sublime.active_window().open_file(privacy_file)
        # TODO: get real prompt text
        res = sublime.yes_no_cancel_dialog("The TypeScript plugin collects anonymous usage data and sends it to Microsoft to help improve the product. \n\nIf you do not want your usage data to be sent to Microsoft click Cancel, otherwise click Ok. \n\nGo to www.typescriptlang.org/telemetry for more information.", "Accept", "Decline")
        acceptance_result = 'true' if res == sublime.DIALOG_YES else 'false'
        
        # If the user has an existing telemetry ID, re-use it
        # If they have none and accept telemetry generate a random GUID for an ID
        existing_telemetry_setting = settings.get(telemetry_setting_name, None) 
        current_telemetry_user_id =  "None" if not existing_telemetry_setting else existing_telemetry_setting['userID']
        if acceptance_result == 'true' and current_telemetry_user_id == "None":
            current_telemetry_user_id = str(uuid.uuid4())

        # TODO: this causes bools to be set as strings, need to use json for real?
        telemetry_settings_value = { "version": privacy_policy_version, "accepted": acceptance_result, 'userID': current_telemetry_user_id } 

        settings.set(telemetry_setting_name, telemetry_settings_value) 
        sublime.save_settings('Preferences.sublime-settings')

    cli.initialize()

    ref_view = get_ref_view(False)
    if ref_view:
        settings = ref_view.settings()
        ref_info_view = settings.get('refinfo')
        if ref_info_view:
            print("got refinfo from settings")
            ref_info = build_ref_info(ref_info_view)
            cli.update_ref_info(ref_info)
            ref_view.set_scratch(True)
            highlight_ids(ref_view, ref_info.get_ref_id())
            cur_line = ref_info.get_ref_line()
            if cur_line:
                update_ref_line(ref_info, int(cur_line), ref_view)
            else:
                print("no current ref line")
        else:
            window = sublime.active_window()
            if window:
                window.focus_view(ref_view)
                window.run_command('close')
    else:
        print("ref view not found")
    log.debug("plugin_loaded ended")


def plugin_unloaded():
    """
    Note: this unload is not always called on exit
    """
    print('typescript plugin unloaded')
    ref_view = get_ref_view()
    if ref_view:
        ref_info = cli.get_ref_info()
        if ref_info:
            ref_view.settings().set('refinfo', ref_info.as_value())
    cli.service.exit()
